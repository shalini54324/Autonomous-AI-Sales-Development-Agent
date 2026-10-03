from __future__ import annotations
import json
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.database.models import ICPConfig, Company, Lead, Outreach, FollowUp, PipelineRun, Activity, AppSetting
from app.schemas.icp import ICPInput
from app.schemas.company import CompanyInput
from app.schemas.lead import ResearchResult, DecisionMaker, NeedItem, ScoreResult
from app.schemas.outreach import OutreachContent, FollowUpContent
from app.utils.dates import followup_due_at


class Repository:
    def __init__(self, session: Session):
        self.s = session

    def save_icp(self, icp: ICPInput) -> ICPConfig:
        row = self.s.execute(select(ICPConfig).order_by(desc(ICPConfig.id))).scalars().first()
        if row is None:
            row = ICPConfig()
        row.target_industry = icp.target_industry
        row.target_roles_json = json.dumps(icp.target_roles)
        row.target_location = icp.target_location
        row.min_employees = icp.min_employees
        row.max_employees = icp.max_employees
        row.product_service = icp.product_service
        row.ideal_customer_description = icp.ideal_customer_description
        row.known_pain_points_json = json.dumps(icp.known_pain_points)
        row.technology_requirements_json = json.dumps(icp.technology_requirements)
        self.s.add(row)
        self.s.commit()
        self.s.refresh(row)
        return row

    def get_icp(self) -> ICPInput | None:
        row = self.s.execute(select(ICPConfig).order_by(desc(ICPConfig.id))).scalars().first()
        if not row:
            return None
        return ICPInput(
            target_industry=row.target_industry,
            target_roles=json.loads(row.target_roles_json),
            target_location=row.target_location,
            min_employees=row.min_employees,
            max_employees=row.max_employees,
            product_service=row.product_service,
            ideal_customer_description=row.ideal_customer_description,
            known_pain_points=json.loads(row.known_pain_points_json or "[]"),
            technology_requirements=json.loads(row.technology_requirements_json or "[]"),
        )

    def save_company(self, c: CompanyInput) -> Company:
        q = select(Company).where(Company.name.ilike(c.company_name))
        row = self.s.execute(q).scalars().first()
        if not row:
            row = Company(
                name=c.company_name,
                website=c.website,
                industry=c.industry,
                location=c.location,
                employee_count=c.employee_count,
                source=c.source,
                source_note=c.source_note,
            )
        else:
            row.website = c.website or row.website
            row.industry = c.industry or row.industry
            row.location = c.location or row.location
            row.employee_count = c.employee_count or row.employee_count
            row.source = c.source or row.source
            row.source_note = c.source_note or row.source_note
        self.s.add(row)
        self.s.commit()
        self.s.refresh(row)
        return row

    def save_lead(
        self,
        company: Company,
        research: ResearchResult,
        dm: DecisionMaker,
        needs: list[NeedItem],
        score: ScoreResult,
        status="complete",
        error=None,
    ) -> Lead:
        row = Lead(
            company_id=company.id,
            research_json=research.model_dump_json(),
            decision_maker_json=dm.model_dump_json(),
            needs_json=json.dumps([n.model_dump() for n in needs]),
            score=score.total,
            classification=score.classification,
            score_breakdown_json=json.dumps(score.breakdown),
            rationale_json=json.dumps(score.rationale),
            pipeline_status=status,
            error_message=error,
        )
        self.s.add(row)
        self.s.commit()
        self.s.refresh(row)
        return row

    def save_failed_lead(self, c: CompanyInput, error: str, stage: str = "pipeline") -> Lead:
        company = self.save_company(c)
        research = ResearchResult(
            company_name=c.company_name,
            website=c.website,
            industry=c.industry or "Unknown",
            location=c.location or "Unknown",
            company_size=c.employee_count,
            description=f"Processing stopped during {stage}.",
            research_status="failed",
            evidence=[],
        )
        dm = DecisionMaker(
            name="Unknown",
            role="Unknown",
            company=c.company_name,
            relevance_reason="Not available because processing did not complete.",
            confidence="low",
            evidence="Not available",
        )
        score = ScoreResult(
            total=0,
            classification="LOW",
            breakdown={
                "Industry Fit": 0,
                "Size Fit": 0,
                "Location Fit": 0,
                "Decision Maker": 0,
                "Need Fit": 0,
                "Technology Fit": 0,
                "Signals": 0,
                "Research Confidence": 0,
            },
            rationale=[f"Pipeline failed during {stage}; no qualification score was inferred."],
        )
        return self.save_lead(company, research, dm, [], score, status="failed", error=error)

    def mark_lead_partial(self, lead_id: int, error: str) -> Lead | None:
        row = self.s.get(Lead, lead_id)
        if not row:
            return None
        row.pipeline_status = "partial"
        row.error_message = error
        self.s.add(row)
        self.s.commit()
        self.s.refresh(row)
        return row

    def save_outreach(self, lead_id: int, content: OutreachContent, generated_by="ai") -> Outreach:
        row = Outreach(
            lead_id=lead_id,
            subject=content.subject,
            body=content.as_email(),
            generated_by=generated_by,
        )
        self.s.add(row)
        self.s.commit()
        self.s.refresh(row)
        return row

    def save_followup(self, lead_id: int, content: FollowUpContent) -> FollowUp:
        now = datetime.now(timezone.utc)
        row = FollowUp(
            lead_id=lead_id,
            action=content.action,
            timing=content.timing,
            message=content.message,
            reason=content.reason,
            scheduled_for=followup_due_at(content.timing, now),
        )
        self.s.add(row)
        self.s.commit()
        self.s.refresh(row)
        return row

    def list_leads(self):
        return list(
            self.s.execute(select(Lead).order_by(desc(Lead.score), desc(Lead.created_at)))
            .scalars()
            .all()
        )

    def get_lead(self, lead_id: int):
        return self.s.get(Lead, lead_id)

    def list_outreaches(self):
        return list(
            self.s.execute(select(Outreach).order_by(desc(Outreach.created_at))).scalars().all()
        )

    def list_followups(self):
        return list(
            self.s.execute(
                select(FollowUp).order_by(FollowUp.scheduled_for.asc().nulls_last(), desc(FollowUp.created_at))
            )
            .scalars()
            .all()
        )

    def get_thresholds(self) -> dict[str, int]:
        row = self.s.get(AppSetting, "lead_thresholds")
        if not row:
            return {"HOT": 85, "HIGH PRIORITY": 70, "WARM": 50, "LOW": 0}
        try:
            data = json.loads(row.value_json)
            return {
                "HOT": int(data["HOT"]),
                "HIGH PRIORITY": int(data["HIGH PRIORITY"]),
                "WARM": int(data["WARM"]),
                "LOW": 0,
            }
        except Exception:
            return {"HOT": 85, "HIGH PRIORITY": 70, "WARM": 50, "LOW": 0}

    def save_thresholds(self, hot: int, high: int, warm: int) -> dict[str, int]:
        if not (100 >= hot > high > warm >= 0):
            raise ValueError("Thresholds must satisfy 100 ≥ HOT > HIGH > WARM ≥ 0")
        data = {"HOT": int(hot), "HIGH PRIORITY": int(high), "WARM": int(warm), "LOW": 0}
        row = self.s.get(AppSetting, "lead_thresholds") or AppSetting(
            key="lead_thresholds", value_json="{}"
        )
        row.value_json = json.dumps(data)
        self.s.add(row)
        self.s.commit()
        return data

    def create_run(self, submitted: int, mode: str, autonomous: bool) -> PipelineRun:
        row = PipelineRun(companies_submitted=submitted, mode=mode, autonomous=autonomous)
        self.s.add(row)
        self.s.commit()
        self.s.refresh(row)
        return row

    def finish_run(self, row: PipelineRun, **stats):
        for k, v in stats.items():
            setattr(row, k, v)
        row.completed_at = datetime.now(timezone.utc)
        self.s.add(row)
        self.s.commit()
        self.s.refresh(row)
        return row

    def list_runs(self):
        return list(
            self.s.execute(select(PipelineRun).order_by(desc(PipelineRun.started_at))).scalars().all()
        )

    def log(self, event_type, message, company_name=None):
        row = Activity(event_type=event_type, message=message, company_name=company_name)
        self.s.add(row)
        self.s.commit()
        return row

    def list_activity(self, limit=20):
        return list(
            self.s.execute(select(Activity).order_by(desc(Activity.created_at)).limit(limit))
            .scalars()
            .all()
        )
