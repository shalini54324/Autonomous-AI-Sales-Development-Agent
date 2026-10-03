from app.schemas.lead import DecisionMaker
from app.services.openai_service import OpenAIService
from app.data.demo_profiles import get_demo_profile


class DecisionMakerAgent:
    def __init__(self, ai=None):
        self.ai = ai or OpenAIService()

    def run(self, research, icp, demo=False):
        role = icp.target_roles[0] if icp.target_roles else "Decision Maker"
        if demo:
            profile = get_demo_profile(research.company_name)
            if profile:
                chosen_role = profile["buyer_role"]
                return DecisionMaker(
                    name=profile["buyer_name"],
                    role=chosen_role,
                    company=research.company_name,
                    relevance_reason=(
                        f"Fictional demo buyer role: {chosen_role}. Its relevance is evaluated "
                        "against the configured ICP rather than forced to match it."
                    ),
                    confidence="medium",
                    evidence="DEMO DATA — fictional sample contact persona",
                )
            return DecisionMaker(
                name="Unknown",
                role=role,
                company=research.company_name,
                relevance_reason=(
                    f"{role} is the configured target role. Demo mode does not invent a named contact."
                ),
                confidence="low",
                evidence="DEMO DATA — no fictional profile exists for this manually supplied company",
            )
        if self.ai.available:
            system = (
                "You are a cautious B2B account analyst. Identify the most relevant buyer role from "
                "the configured target roles using only supplied company research. Do not invent a "
                "person's name. Return JSON fields name, role, company, relevance_reason, confidence, "
                "evidence. Use name='Unknown' unless a person is actually present in the evidence."
            )
            prompt = (
                f"Research={research.model_dump()}\nTarget roles={icp.target_roles}\n"
                f"Product={icp.product_service}"
            )
            try:
                return self.ai.json_completion(system, prompt, DecisionMaker)
            except Exception:
                pass
        return DecisionMaker(
            name="Unknown",
            role=role,
            company=research.company_name,
            relevance_reason=(
                f"{role} is the closest configured buying role for {icp.product_service}; "
                "verify the individual before outreach."
            ),
            confidence="low",
            evidence="No verified public person supplied by research source",
        )
