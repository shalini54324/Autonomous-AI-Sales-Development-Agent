from app.schemas.icp import ICPInput
from app.schemas.company import CompanyInput
from app.schemas.lead import ResearchResult, DecisionMaker, NeedItem, ScoreResult
from app.schemas.outreach import OutreachContent, FollowUpContent
from app.pipeline.orchestrator import PipelineOrchestrator


def icp():
    return ICPInput(
        target_industry="SaaS",
        target_roles=["CTO"],
        target_location="Global",
        min_employees=50,
        max_employees=500,
        product_service="AI sales automation",
        ideal_customer_description="SaaS",
        known_pain_points=["manual prospecting"],
    )


class Research:
    def run(self, c, demo=False):
        if c.company_name == "BadCo":
            raise RuntimeError("simulated research failure")
        return ResearchResult(
            company_name=c.company_name,
            website=c.website,
            industry=c.industry or "SaaS",
            location=c.location or "Global",
            company_size=c.employee_count or 100,
            growth_signals=["growth"],
            research_status="demo" if demo else "complete",
            evidence=["demo"],
        )


class DM:
    def run(self, r, i, demo=False):
        return DecisionMaker(name="Alex", role="CTO", company=r.company_name, confidence="high")


class Needs:
    def run(self, r, i, demo=False):
        return [
            NeedItem(
                need="manual prospecting",
                evidence_reasoning="matched",
                relevance="high",
                product_connection="fit",
            )
        ]


class ScoreHot:
    def run(self, *a):
        return ScoreResult(total=90, classification="HOT", breakdown={"x": 90}, rationale=["fit"])


class ScoreHigh:
    def run(self, *a):
        return ScoreResult(
            total=78, classification="HIGH PRIORITY", breakdown={"x": 78}, rationale=["fit"]
        )


class ScoreLow:
    def run(self, *a):
        return ScoreResult(total=30, classification="LOW", breakdown={"x": 30}, rationale=["low"])


class Outreach:
    def run(self, *a, **k):
        return OutreachContent(
            subject="Subject",
            greeting="Hi",
            opening="Open",
            value_proposition="Value",
            reason_for_outreach="Reason",
            cta="CTA",
            closing="Close",
        )


class BrokenOutreach:
    def run(self, *a, **k):
        raise RuntimeError("simulated OpenAI outage")


class Follow:
    def run(self, *a, **k):
        return FollowUpContent(
            action="Follow up", timing="In 3 business days", message="Message", reason="Reason"
        )


def orch(repo, score, outreach=None):
    return PipelineOrchestrator(
        repo, Research(), DM(), Needs(), score, outreach or Outreach(), Follow()
    )


def test_database_persistence(repo):
    repo.save_icp(icp())
    assert repo.get_icp().product_service == "AI sales automation"


def test_pipeline_processing(repo):
    res = orch(repo, ScoreHot()).process_batch(
        [CompanyInput(company_name="Acme", industry="SaaS", employee_count=100)],
        icp(),
        demo=True,
    )
    assert res["successful"] == 1 and repo.list_leads()[0].score == 90


def test_one_bad_company_does_not_break_the_batch_and_failure_is_persisted(repo):
    cs = [
        CompanyInput(company_name="Good1"),
        CompanyInput(company_name="BadCo"),
        CompanyInput(company_name="Good2"),
    ]
    res = orch(repo, ScoreHot()).process_batch(cs, icp(), demo=True)
    assert res["successful"] == 2 and res["failed"] == 1
    leads = repo.list_leads()
    assert len(leads) == 3
    failed = next(l for l in leads if l.company.name == "BadCo")
    assert failed.pipeline_status == "failed"
    assert "simulated research failure" in failed.error_message


def test_hot_lead_gets_auto_outreach_and_followup(repo):
    orch(repo, ScoreHot()).process_batch(
        [CompanyInput(company_name="HotCo")],
        icp(),
        demo=True,
        autonomous=True,
        auto_classes={"HOT", "HIGH PRIORITY"},
    )
    assert len(repo.list_outreaches()) == 1 and len(repo.list_followups()) == 1


def test_high_priority_lead_gets_auto_outreach_and_followup(repo):
    orch(repo, ScoreHigh()).process_batch(
        [CompanyInput(company_name="HighCo")],
        icp(),
        demo=True,
        autonomous=True,
        auto_classes={"HOT", "HIGH PRIORITY"},
    )
    assert len(repo.list_outreaches()) == 1 and len(repo.list_followups()) == 1


def test_low_quality_lead_is_not_auto_processed(repo):
    orch(repo, ScoreLow()).process_batch(
        [CompanyInput(company_name="LowCo")],
        icp(),
        demo=True,
        autonomous=True,
        auto_classes={"HOT", "HIGH PRIORITY"},
    )
    assert len(repo.list_outreaches()) == 0 and len(repo.list_followups()) == 0


def test_autonomous_failure_marks_existing_lead_partial(repo):
    res = orch(repo, ScoreHot(), BrokenOutreach()).process_batch(
        [CompanyInput(company_name="PartialCo")],
        icp(),
        demo=True,
        autonomous=True,
        auto_classes={"HOT"},
    )
    assert res["successful"] == 0 and res["failed"] == 1
    leads = repo.list_leads()
    assert len(leads) == 1
    assert leads[0].pipeline_status == "partial"
    assert "autonomous outreach" in leads[0].error_message
    assert "simulated OpenAI outage" in leads[0].error_message


def test_followup_gets_real_scheduled_date(repo):
    orch(repo, ScoreHot()).process_batch(
        [CompanyInput(company_name="ScheduledCo")],
        icp(),
        demo=True,
        autonomous=True,
        auto_classes={"HOT"},
    )
    follow = repo.list_followups()[0]
    assert follow.scheduled_for is not None
    assert follow.scheduled_for > follow.created_at.replace(tzinfo=None) if follow.created_at.tzinfo is None else follow.scheduled_for > follow.created_at


def test_progress_reports_real_pipeline_stages(repo):
    events = []
    orch(repo, ScoreHot()).process_batch(
        [CompanyInput(company_name="ProgressCo")],
        icp(),
        demo=True,
        progress=lambda i, total, name, stage: events.append(stage),
    )
    assert "Researching company…" in events
    assert "Finding decision makers…" in events
    assert "Analyzing business needs…" in events
    assert "Calculating lead score…" in events
    assert "Saving intelligence…" in events
    assert "Complete" in events


def test_multiple_runs_are_listed_most_recent_first(repo):
    o = orch(repo, ScoreHot())
    o.process_batch([CompanyInput(company_name="A")], icp(), demo=True)
    o.process_batch([CompanyInput(company_name="B")], icp(), demo=True)
    runs = repo.list_runs()
    assert runs[0].id > runs[1].id


def test_outreach_and_followup_interfaces(repo):
    o = orch(repo, ScoreHot())
    o.process_batch(
        [CompanyInput(company_name="A")],
        icp(),
        demo=True,
        autonomous=True,
        auto_classes={"HOT"},
    )
    assert repo.list_outreaches()[0].subject == "Subject"
    assert repo.list_followups()[0].action == "Follow up"
