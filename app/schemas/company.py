from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl, field_validator

class CompanyInput(BaseModel):
    company_name: str = Field(min_length=1)
    website: str | None = None
    industry: str | None = None
    location: str | None = None
    employee_count: int | None = Field(default=None, ge=1)
    source: str = "manual"
    source_note: str | None = None

    @field_validator("company_name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = " ".join(v.split()).strip(" ,;|")
        if not v:
            raise ValueError("Company name is required")
        return v

class DiscoveryCriteria(BaseModel):
    industry: str = Field(min_length=2)
    location: str = Field(min_length=2)
    min_employees: int = Field(ge=1)
    max_employees: int = Field(ge=1)
    count: int = Field(ge=1, le=25)
