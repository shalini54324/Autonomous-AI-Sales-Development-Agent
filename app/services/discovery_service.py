from __future__ import annotations
from app.schemas.company import CompanyInput, DiscoveryCriteria
from app.services.openai_service import OpenAIService
from app.data.demo_profiles import DEMO_PROFILES


class DiscoveryService:
    def __init__(self, ai: OpenAIService | None = None):
        self.ai = ai or OpenAIService()

    def discover_demo(self, c: DiscoveryCriteria) -> list[CompanyInput]:
        """Return clearly fictional sample prospects without rewriting their attributes.

        The pool intentionally includes strong, medium, and weak fits so Demo Mode
        demonstrates qualification honestly rather than manufacturing HOT leads.
        """
        out = []
        for profile in DEMO_PROFILES[: c.count]:
            out.append(
                CompanyInput(
                    company_name=profile["company_name"],
                    website=profile["website"],
                    industry=profile["industry"],
                    location=profile["location"],
                    employee_count=profile["employee_count"],
                    source="demo",
                    source_note=(
                        "DEMO DATA — fictional sample candidate. "
                        + profile["recommendation_reason"]
                    ),
                )
            )
        return out

    def discover_live(self, c: DiscoveryCriteria) -> list[CompanyInput]:
        system = (
            "You propose B2B prospect candidates. Return JSON with a companies array. "
            "Do not claim verification. Use well-known companies and label each recommendation "
            "as AI-suggested and requiring verification."
        )
        prompt = (
            f"Propose {c.count} companies for industry={c.industry}, location={c.location}, "
            f"employee range={c.min_employees}-{c.max_employees}. Each item: company_name, "
            "website, industry, location, employee_count (integer|null), reason."
        )
        data = self.ai.raw_json(system, prompt)
        out = []
        for item in data.get("companies", [])[: c.count]:
            try:
                out.append(
                    CompanyInput(
                        company_name=item.get("company_name", ""),
                        website=item.get("website"),
                        industry=item.get("industry") or c.industry,
                        location=item.get("location") or c.location,
                        employee_count=item.get("employee_count"),
                        source="ai_discovery",
                        source_note=(
                            "AI-suggested candidate — verify before use. "
                            + str(item.get("reason", ""))
                        ),
                    )
                )
            except Exception:
                pass
        return out
