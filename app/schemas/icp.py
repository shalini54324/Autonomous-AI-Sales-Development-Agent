from __future__ import annotations
from pydantic import BaseModel, Field, field_validator

class ICPInput(BaseModel):
    target_industry: str = Field(min_length=2)
    target_roles: list[str] = Field(min_length=1)
    target_location: str = Field(min_length=2)
    min_employees: int = Field(default=1, ge=1)
    max_employees: int = Field(default=10000, ge=1)
    product_service: str = Field(min_length=3)
    ideal_customer_description: str = Field(min_length=3)
    known_pain_points: list[str] = Field(default_factory=list)
    technology_requirements: list[str] = Field(default_factory=list)

    @field_validator("target_roles", "known_pain_points", "technology_requirements", mode="before")
    @classmethod
    def split_csv(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.replace("\n", ",").split(",") if x.strip()]
        return v

    @field_validator("max_employees")
    @classmethod
    def max_not_tiny(cls, v, info):
        min_e = info.data.get("min_employees", 1)
        if v < min_e:
            raise ValueError("Maximum company size must be greater than or equal to minimum size")
        return v
