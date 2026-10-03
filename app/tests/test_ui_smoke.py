from __future__ import annotations
import pytest
from app.database.models import Base, Company, Lead, Outreach, FollowUp, PipelineRun, Activity
from app.database.repositories import Repository
from app.schemas.icp import ICPInput
from app.schemas.company import CompanyInput
from app.schemas.lead import ResearchResult, DecisionMaker, NeedItem, ScoreResult
from app.schemas.outreach import OutreachContent, FollowUpContent
from app.ui.components import badge, status_pill, parse_json
from app.ui import dashboard, discovery, leads, lead_detail, outreach, followups, icp, settings as settings_page, pipeline_runs
import streamlit as st


def test_ui_components_unit():
    assert "hot" in badge("HOT")
    assert "high" in badge("HIGH PRIORITY")
    assert "warm" in badge("WARM")
    assert "low" in badge("LOW")
    assert "ready" in status_pill("ready")
    assert "sent" in status_pill("sent")
    assert "review" in status_pill("review")
    assert parse_json('{"a": 1}', {}) == {"a": 1}
    assert parse_json("invalid json", {"fallback": True}) == {"fallback": True}


def test_ui_pages_smoke(repo):
    # Setup test data
    cfg = ICPInput(
        target_industry="SaaS",
        target_roles=["CTO", "Founder"],
        target_location="Global",
        min_employees=50,
        max_employees=500,
        product_service="AI sales automation",
        ideal_customer_description="Growing SaaS companies",
        known_pain_points=["manual prospecting"],
    )
    repo.save_icp(cfg)

    c_input = CompanyInput(
        company_name="Acme Corp",
        website="https://acme.test",
        industry="SaaS",
        location="Global",
        employee_count=100,
        source="manual",
        source_note="test",
    )
    c = repo.save_company(c_input)

    research = ResearchResult(
        company_name="Acme Corp",
        website="https://acme.test",
        industry="SaaS",
        location="Global",
        company_size=100,
        description="Acme SaaS platform",
        products_services=["Platform", "API"],
        business_model="B2B SaaS",
        research_status="complete",
        evidence=["Evidence 1", "Evidence 2"],
    )
    dm = DecisionMaker(
        name="Alice Smith",
        role="CTO",
        confidence="high",
        company="Acme Corp",
        relevance_reason="Technical buyer",
    )
    needs = [
        NeedItem(
            need="Automate sales prospecting",
            evidence_reasoning="High manual volume",
            relevance="high",
            product_connection="Direct match",
        )
    ]
    score = ScoreResult(
        total=85,
        classification="HOT",
        breakdown={"Industry Fit": 20, "Size Fit": 15, "Location Fit": 10, "Decision Maker": 15, "Need Fit": 25},
        rationale=["Strong overall match across all dimensions"],
    )

    l = repo.save_lead(c, research, dm, needs, score)

    outreach_content = OutreachContent(
        subject="Quick question on sales automation",
        greeting="Hi Alice,",
        opening="Noticed Acme Corp's rapid growth.",
        value_proposition="We automate B2B prospecting.",
        reason_for_outreach="Saw your tech scaling initiative.",
        cta="Worth a 10-minute chat?",
        closing="Best,\nSalesPilot Team",
    )
    repo.save_outreach(l.id, outreach_content)

    followup_content = FollowUpContent(
        action="Email nudge",
        message="Following up...",
        reason="3 days elapsed",
        timing="In 3 days",
    )
    repo.save_followup(l.id, followup_content)
    repo.log("pipeline_complete", "Processed Acme successfully")

    # Render each page to ensure no syntax/runtime crash
    dashboard.render(repo)
    discovery.render(repo, force_demo=True)
    leads.render(repo)
    
    st.session_state.selected_lead_id = l.id
    lead_detail.render(repo, demo_mode=True)
    outreach.render(repo, demo_mode=True)
    followups.render(repo)
    pipeline_runs.render(repo)
    icp.render(repo)
    settings_page.render(repo)


def test_ui_pages_empty_state(repo):
    # Verify all pages render safely when database has zero records
    st.session_state.selected_lead_id = None
    dashboard.render(repo)
    discovery.render(repo, force_demo=True)
    leads.render(repo)
    lead_detail.render(repo, demo_mode=True)
    outreach.render(repo, demo_mode=True)
    followups.render(repo)
    pipeline_runs.render(repo)
    icp.render(repo)
    settings_page.render(repo)

