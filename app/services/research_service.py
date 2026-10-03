from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from app.schemas.company import CompanyInput
from app.schemas.lead import ResearchResult
from app.services.openai_service import OpenAIService
from app.data.demo_profiles import get_demo_profile


class ResearchService:
    def __init__(self, ai: OpenAIService | None = None):
        self.ai = ai or OpenAIService()

    def _website_text(self, url: str | None) -> tuple[str, list[str]]:
        if not url:
            return "", []
        try:
            r = requests.get(
                url,
                timeout=8,
                headers={"User-Agent": "Mozilla/5.0 SalesResearchBot/1.0"},
            )
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = " ".join(soup.stripped_strings)
            return text[:12000], [url]
        except Exception:
            return "", []

    def live_research(self, c: CompanyInput) -> ResearchResult:
        text, evidence = self._website_text(c.website)
        if not text:
            return ResearchResult(
                company_name=c.company_name,
                website=c.website,
                industry=c.industry or "Unknown",
                location=c.location or "Unknown",
                company_size=c.employee_count,
                evidence=evidence,
                research_status="partial",
                description="Unable to verify website content",
            )
        system = (
            "You are a cautious B2B research analyst. Use only supplied website text. "
            "Never invent precise facts. Return JSON matching the requested fields; "
            "use Unknown/Not available when unsupported."
        )
        prompt = (
            f"Company: {c.company_name}\nWebsite: {c.website}\nKnown industry: {c.industry}\n"
            f"Known location: {c.location}\nWebsite text:\n{text}\nReturn fields: company_name, "
            "website, industry, location, description, products_services(list), business_model, "
            "company_size(integer|null), technology_signals(list), growth_signals(list), "
            "recent_signals(list), evidence(list), research_status."
        )
        try:
            result = self.ai.json_completion(system, prompt, ResearchResult)
            if c.website and c.website not in result.evidence:
                result.evidence.append(c.website)
            return result
        except Exception:
            return ResearchResult(
                company_name=c.company_name,
                website=c.website,
                industry=c.industry or "Unknown",
                location=c.location or "Unknown",
                description=text[:500],
                company_size=c.employee_count,
                evidence=evidence,
                research_status="partial",
            )

    def demo_research(self, c: CompanyInput) -> ResearchResult:
        profile = get_demo_profile(c.company_name)
        if profile:
            return ResearchResult(
                company_name=profile["company_name"],
                website=profile["website"],
                industry=profile["industry"],
                location=profile["location"],
                description=profile["description"],
                products_services=profile["products_services"],
                business_model="Fictional demo business model",
                company_size=profile["employee_count"],
                technology_signals=profile["technology_signals"],
                growth_signals=profile["growth_signals"],
                recent_signals=profile["recent_signals"],
                evidence=["DEMO DATA — fictional sample intelligence; not live research"],
                research_status="demo",
            )
        # Manual/CSV prospects processed in demo mode still get clearly-labelled generic data.
        return ResearchResult(
            company_name=c.company_name,
            website=c.website,
            industry=c.industry or "Unknown",
            location=c.location or "Unknown",
            description="Demo intelligence generated from the user-provided company fields only.",
            products_services=[],
            business_model="Unknown",
            company_size=c.employee_count,
            technology_signals=[],
            growth_signals=[],
            recent_signals=[],
            evidence=["DEMO DATA — derived only from user-provided fields"],
            research_status="demo",
        )
