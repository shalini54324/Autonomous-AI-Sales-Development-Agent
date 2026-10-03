from __future__ import annotations
import csv
import io
import re
from urllib.parse import urlparse
from app.schemas.company import CompanyInput

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
LABEL_RE = re.compile(
    r"^(company(?:\s+name)?|name|website|url|industry|location|employee(?:s|\s*count)?|company\s*size)\s*:\s*(.*)$",
    re.I,
)


def _normalize_url(v: str | None):
    if not v:
        return None
    v = v.strip()
    if not v or any(ch.isspace() for ch in v):
        return None
    if v.startswith("www."):
        v = "https://" + v
    if not v.startswith(("http://", "https://")):
        v = "https://" + v
    try:
        p = urlparse(v)
        if not p.netloc or "." not in p.netloc:
            return None
        return v
    except Exception:
        return None


def _company_from_fields(fields: dict, source: str, context: str, errors: list[str]):
    name = (fields.get("company_name") or "").strip()
    if not name:
        errors.append(f"{context}: missing company name")
        return None
    raw_website = (fields.get("website") or "").strip()
    website = _normalize_url(raw_website) if raw_website else None
    if raw_website and not website:
        errors.append(f"{context}: invalid website '{raw_website}'")
    employee_count = fields.get("employee_count")
    try:
        if employee_count not in (None, ""):
            employee_count = int(str(employee_count).replace(",", "").strip())
        else:
            employee_count = None
        return CompanyInput(
            company_name=name,
            website=website,
            industry=(fields.get("industry") or "").strip() or None,
            location=(fields.get("location") or "").strip() or None,
            employee_count=employee_count,
            source=source,
        )
    except Exception as e:
        errors.append(f"{context}: {e}")
        return None


def _parse_compact_line(line: str, line_no: int, errors: list[str]):
    parts = [p.strip() for p in re.split(r"\s*[|,\t]\s*", line) if p.strip()]
    if not parts:
        return None
    fields = {"company_name": None, "website": None}
    for p in parts:
        if URL_RE.fullmatch(p) or p.lower().startswith(("http://", "https://", "www.")):
            fields["website"] = p
        elif fields["company_name"] is None:
            fields["company_name"] = p
    return _company_from_fields(fields, "manual", f"Line {line_no}", errors)


def parse_manual_companies(text: str) -> tuple[list[CompanyInput], list[str]]:
    """Parse both compact one-line entries and labelled multi-line blocks.

    Supported examples:
      Acme, https://acme.test

      Company Name: Acme
      Website: https://acme.test
      Industry: SaaS
      Location: India

    Metadata lines are attached to the current company and are never interpreted
    as separate companies.
    """
    companies: list[CompanyInput] = []
    errors: list[str] = []
    seen: set[str] = set()
    current: dict | None = None
    current_start = 0

    def flush_current():
        nonlocal current, current_start
        if not current:
            return
        company = _company_from_fields(current, "manual", f"Block starting line {current_start}", errors)
        current = None
        current_start = 0
        if not company:
            return
        key = company.company_name.lower()
        if key in seen:
            errors.append(f"Duplicate company '{company.company_name}'")
            return
        seen.add(key)
        companies.append(company)

    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            flush_current()
            continue

        match = LABEL_RE.match(line)
        if match:
            label, value = match.group(1).lower().strip(), match.group(2).strip()
            normalized = {
                "company": "company_name",
                "company name": "company_name",
                "name": "company_name",
                "website": "website",
                "url": "website",
                "industry": "industry",
                "location": "location",
                "employee": "employee_count",
                "employees": "employee_count",
                "employee count": "employee_count",
                "company size": "employee_count",
            }.get(label)
            if normalized == "company_name":
                if current and current.get("company_name"):
                    flush_current()
                current = {"company_name": value}
                current_start = i
            else:
                if current is None:
                    # Preserve the requirement that metadata lines never become companies.
                    errors.append(f"Line {i}: '{label}' has no company name to attach to")
                    continue
                current[normalized] = value
            continue

        # A plain company name can start a labelled block (e.g. "Acme" followed by Website: ...).
        if current is not None:
            flush_current()

        # Compact entries with separators/URLs are immediately complete.
        if "," in line or "|" in line or "\t" in line or URL_RE.search(line):
            company = _parse_compact_line(line, i, errors)
            if company:
                key = company.company_name.lower()
                if key in seen:
                    errors.append(f"Line {i}: duplicate company '{company.company_name}'")
                else:
                    seen.add(key)
                    companies.append(company)
        else:
            current = {"company_name": line}
            current_start = i

    flush_current()
    return companies, errors


def parse_csv_bytes(data: bytes) -> tuple[list[CompanyInput], list[str]]:
    text = data.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    companies: list[CompanyInput] = []
    errors: list[str] = []
    seen: set[str] = set()
    aliases = {"name": "company_name", "company": "company_name", "url": "website"}
    for idx, row in enumerate(reader, 2):
        clean = {}
        for k, v in (row or {}).items():
            if k is None:
                continue
            key = aliases.get(k.strip().lower(), k.strip().lower())
            clean[key] = (v or "").strip()
        name = clean.get("company_name", "")
        if not name:
            errors.append(f"Row {idx}: missing company_name")
            continue
        if name.lower() in seen:
            errors.append(f"Row {idx}: duplicate company '{name}'")
            continue
        seen.add(name.lower())
        raw_website = clean.get("website", "")
        website = _normalize_url(raw_website) if raw_website else None
        if raw_website and not website:
            errors.append(f"Row {idx}: invalid website '{raw_website}'")
        try:
            count = int(clean["employee_count"].replace(",", "")) if clean.get("employee_count") else None
            companies.append(
                CompanyInput(
                    company_name=name,
                    website=website,
                    industry=clean.get("industry") or None,
                    location=clean.get("location") or None,
                    employee_count=count,
                    source="csv",
                )
            )
        except Exception as e:
            errors.append(f"Row {idx}: {e}")
    return companies, errors
