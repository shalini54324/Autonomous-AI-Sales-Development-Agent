from __future__ import annotations
from pydantic import BaseModel

class OutreachContent(BaseModel):
    subject: str
    greeting: str
    opening: str
    value_proposition: str
    reason_for_outreach: str
    cta: str
    closing: str

    def as_email(self) -> str:
        return "\n\n".join([self.greeting, self.opening, self.value_proposition, self.reason_for_outreach, self.cta, self.closing])

class FollowUpContent(BaseModel):
    action: str
    timing: str
    message: str
    reason: str
