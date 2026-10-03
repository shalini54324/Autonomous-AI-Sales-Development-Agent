from __future__ import annotations
from app.schemas.icp import ICPInput
from app.schemas.lead import ResearchResult,DecisionMaker,NeedItem,ScoreResult
from app.schemas.outreach import OutreachContent,FollowUpContent
from app.services.openai_service import OpenAIService

class OutreachService:
    def __init__(self,ai:OpenAIService|None=None): self.ai=ai or OpenAIService()
    def generate(self,r,dm,needs,score,icp,demo=False)->OutreachContent:
        primary=needs[0].need if needs else "operational efficiency"
        if demo or not self.ai.available:
            greeting=f"Hi {dm.name if dm.name!='Unknown' else dm.role},"
            return OutreachContent(subject=f"A practical idea for {r.company_name}'s {primary}",greeting=greeting,
                opening=f"I noticed {r.company_name} is focused on {', '.join(r.growth_signals[:1]) or 'scaling its operations'}.",
                value_proposition=f"Our {icp.product_service} is designed to help teams improve {primary} without adding unnecessary process overhead.",
                reason_for_outreach=f"Based on the available intelligence, this appears relevant to your priorities and the lead scored {score.total}/100 for fit.",
                cta="Would a short 15-minute conversation next week be useful to compare your current workflow with a lighter approach?",closing="Best regards,\nSales Development Team")
        system="Write concise professional B2B outreach. Avoid generic greetings like 'I hope this email finds you well'. Return JSON with subject,greeting,opening,value_proposition,reason_for_outreach,cta,closing. Do not invent facts."
        prompt=f"Company research={r.model_dump()}\nDecision maker={dm.model_dump()}\nNeeds={[n.model_dump() for n in needs]}\nScore={score.model_dump()}\nProduct={icp.product_service}\nICP={icp.ideal_customer_description}"
        return self.ai.json_completion(system,prompt,OutreachContent)

    def followup(self,r,dm,needs,score,icp,demo=False)->FollowUpContent:
        if demo or not self.ai.available:
            timing="In 3 business days" if score.total>=70 else "In 5 business days"
            action="Send concise value-led follow-up" if score.total>=70 else "Research further before follow-up"
            msg=f"Hi {dm.name if dm.name!='Unknown' else dm.role}, following up with one concrete idea for {r.company_name}: we may be able to help with {needs[0].need if needs else 'workflow efficiency'}. Would a brief comparison be useful?"
            return FollowUpContent(action=action,timing=timing,message=msg,reason=f"Priority is {score.classification}; keep the next touch proportional to fit and evidence.")
        system="Return JSON with action,timing,message,reason for a professional sales follow-up. Do not invent facts."
        prompt=f"Company={r.model_dump()}\nDecision maker={dm.model_dump()}\nNeeds={[n.model_dump() for n in needs]}\nScore={score.model_dump()}\nProduct={icp.product_service}"
        return self.ai.json_completion(system,prompt,FollowUpContent)
