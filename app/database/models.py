from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def now_utc():
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

class ICPConfig(Base):
    __tablename__ = "icp_configs"
    id: Mapped[int] = mapped_column(primary_key=True)
    target_industry: Mapped[str] = mapped_column(String(200))
    target_roles_json: Mapped[str] = mapped_column(Text)
    target_location: Mapped[str] = mapped_column(String(200))
    min_employees: Mapped[int] = mapped_column(Integer)
    max_employees: Mapped[int] = mapped_column(Integer)
    product_service: Mapped[str] = mapped_column(Text)
    ideal_customer_description: Mapped[str] = mapped_column(Text)
    known_pain_points_json: Mapped[str] = mapped_column(Text, default="[]")
    technology_requirements_json: Mapped[str] = mapped_column(Text, default="[]")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(300), index=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="manual")
    source_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    leads: Mapped[list["Lead"]] = relationship(back_populates="company", cascade="all, delete-orphan")

class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    research_json: Mapped[str] = mapped_column(Text)
    decision_maker_json: Mapped[str] = mapped_column(Text)
    needs_json: Mapped[str] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer, index=True)
    classification: Mapped[str] = mapped_column(String(50), index=True)
    score_breakdown_json: Mapped[str] = mapped_column(Text)
    rationale_json: Mapped[str] = mapped_column(Text, default="[]")
    pipeline_status: Mapped[str] = mapped_column(String(50), default="complete")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    company: Mapped[Company] = relationship(back_populates="leads")
    outreaches: Mapped[list["Outreach"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    followups: Mapped[list["FollowUp"]] = relationship(back_populates="lead", cascade="all, delete-orphan")

class Outreach(Base):
    __tablename__ = "outreaches"
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), index=True)
    subject: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    generated_by: Mapped[str] = mapped_column(String(50), default="ai")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    lead: Mapped[Lead] = relationship(back_populates="outreaches")

class FollowUp(Base):
    __tablename__ = "followups"
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), index=True)
    action: Mapped[str] = mapped_column(String(200))
    timing: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    lead: Mapped[Lead] = relationship(back_populates="followups")

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    mode: Mapped[str] = mapped_column(String(50))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    companies_submitted: Mapped[int] = mapped_column(Integer, default=0)
    companies_successful: Mapped[int] = mapped_column(Integer, default=0)
    companies_failed: Mapped[int] = mapped_column(Integer, default=0)
    qualified_leads: Mapped[int] = mapped_column(Integer, default=0)
    priority_leads: Mapped[int] = mapped_column(Integer, default=0)
    outreach_generated: Mapped[int] = mapped_column(Integer, default=0)
    followups_generated: Mapped[int] = mapped_column(Integer, default=0)
    autonomous: Mapped[bool] = mapped_column(Boolean, default=False)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

class AppSetting(Base):
    __tablename__ = "app_settings"
    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value_json: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(80))
    message: Mapped[str] = mapped_column(Text)
    company_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
