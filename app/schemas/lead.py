from __future__ import annotations
from pydantic import BaseModel, Field

class ResearchResult(BaseModel):
    company_name: str
    website: str | None = None
    industry: str = "Unknown"
    location: str = "Unknown"
    description: str = "Not available"
    products_services: list[str] = Field(default_factory=list)
    business_model: str = "Unknown"
    company_size: int | None = None
    technology_signals: list[str] = Field(default_factory=list)
    growth_signals: list[str] = Field(default_factory=list)
    recent_signals: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    research_status: str = "complete"

class DecisionMaker(BaseModel):
    name: str = "Unknown"
    role: str = "Unknown"
    company: str
    relevance_reason: str = "Not available"
    confidence: str = "low"
    evidence: str = "Not available"

class NeedItem(BaseModel):
    need: str
    evidence_reasoning: str
    relevance: str = "medium"
    product_connection: str

class ScoreResult(BaseModel):
    total: int = Field(ge=0, le=100)
    classification: str
    breakdown: dict[str, int]
    rationale: list[str] = Field(default_factory=list)
