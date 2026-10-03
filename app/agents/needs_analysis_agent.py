from app.schemas.lead import NeedItem
from app.services.openai_service import OpenAIService
from app.data.demo_profiles import get_demo_profile


class NeedsAnalysisAgent:
    def __init__(self, ai=None):
        self.ai = ai or OpenAIService()

    def _fallback(self, research, icp, demo):
        if demo:
            profile = get_demo_profile(research.company_name)
            if profile:
                return [
                    NeedItem(
                        need=need,
                        evidence_reasoning=reason,
                        relevance=relevance,
                        product_connection=(
                            f"{icp.product_service} could be evaluated against this need; demo data "
                            "does not claim a real buying intent."
                        ),
                    )
                    for need, reason, relevance in profile["needs"]
                ][:3]
            # Do not manufacture pain points for arbitrary companies in Demo Mode.
            return []

        needs = []
        base = icp.known_pain_points[:2] or [
            "reducing repetitive sales work",
            "improving lead qualification",
        ]
        for i, n in enumerate(base):
            needs.append(
                NeedItem(
                    need=n,
                    evidence_reasoning=(
                        "Configured ICP pain point plausibly matches the available company context; verify in discovery"
                    ),
                    relevance="high" if i == 0 else "medium",
                    product_connection=f"{icp.product_service} can be positioned around this outcome.",
                )
            )
        if research.growth_signals:
            needs.append(
                NeedItem(
                    need="scaling operations efficiently",
                    evidence_reasoning=f"Signal observed: {research.growth_signals[0]}",
                    relevance="high",
                    product_connection=f"Position {icp.product_service} as a scalable workflow enabler.",
                )
            )
        return needs[:3]

    def run(self, research, icp, demo=False):
        if demo or not self.ai.available:
            return self._fallback(research, icp, demo)
        system = (
            "You are a cautious B2B needs analyst. Infer only plausible business needs grounded in "
            "supplied research and ICP context. Return JSON object with a needs array. Each item: need, "
            "evidence_reasoning, relevance (high/medium/low), product_connection. Avoid generic unsupported pain points."
        )
        prompt = (
            f"Research={research.model_dump()}\nICP pain points={icp.known_pain_points}\n"
            f"Product={icp.product_service}\nIdeal customer={icp.ideal_customer_description}"
        )
        try:
            data = self.ai.raw_json(system, prompt)
            parsed = [NeedItem.model_validate(x) for x in data.get("needs", [])[:3]]
            return parsed or self._fallback(research, icp, False)
        except Exception:
            return self._fallback(research, icp, False)
