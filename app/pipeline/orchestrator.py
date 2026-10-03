from __future__ import annotations
from app.database.repositories import Repository
from app.schemas.company import CompanyInput
from app.schemas.icp import ICPInput
from app.agents.company_research_agent import CompanyResearchAgent
from app.agents.decision_maker_agent import DecisionMakerAgent
from app.agents.needs_analysis_agent import NeedsAnalysisAgent
from app.agents.lead_scoring_agent import LeadScoringAgent
from app.agents.outreach_agent import OutreachAgent
from app.agents.followup_agent import FollowUpAgent


class PipelineCompanyError(RuntimeError):
    def __init__(self, message: str, *, stage: str, lead_id: int | None = None):
        super().__init__(message)
        self.stage = stage
        self.lead_id = lead_id


class PipelineOrchestrator:
    def __init__(
        self,
        repo: Repository,
        research_agent=None,
        dm_agent=None,
        needs_agent=None,
        scoring_agent=None,
        outreach_agent=None,
        followup_agent=None,
    ):
        self.repo = repo
        self.research = research_agent or CompanyResearchAgent()
        self.dm = dm_agent or DecisionMakerAgent()
        self.needs = needs_agent or NeedsAnalysisAgent()
        self.scoring = scoring_agent or LeadScoringAgent()
        self.outreach = outreach_agent or OutreachAgent()
        self.followup = followup_agent or FollowUpAgent()

    @staticmethod
    def _emit(stage_progress, stage: str):
        if stage_progress:
            stage_progress(stage)

    def process_company(
        self,
        c: CompanyInput,
        icp: ICPInput,
        demo=False,
        autonomous=False,
        auto_classes=None,
        stage_progress=None,
    ):
        company = self.repo.save_company(c)
        lead = None
        stage = "research"
        try:
            self._emit(stage_progress, "Researching company…")
            r = self.research.run(c, demo=demo)
            self.repo.log("research", f"Research completed for {c.company_name}", c.company_name)

            stage = "decision maker"
            self._emit(stage_progress, "Finding decision makers…")
            dm = self.dm.run(r, icp, demo=demo)
            self.repo.log(
                "decision_maker",
                f"Decision maker identified: {dm.role}",
                c.company_name,
            )

            stage = "needs analysis"
            self._emit(stage_progress, "Analyzing business needs…")
            needs = self.needs.run(r, icp, demo=demo)
            self.repo.log("needs", f"Detected {len(needs)} business need(s)", c.company_name)

            stage = "lead scoring"
            self._emit(stage_progress, "Calculating lead score…")
            score = self.scoring.run(r, dm, needs, icp, self.repo.get_thresholds())
            self.repo.log(
                "score",
                f"Score calculated: {score.total} ({score.classification})",
                c.company_name,
            )

            stage = "saving intelligence"
            self._emit(stage_progress, "Saving intelligence…")
            lead = self.repo.save_lead(company, r, dm, needs, score)

            generated_o = generated_f = 0
            if autonomous and score.classification in (auto_classes or {"HOT", "HIGH PRIORITY"}):
                stage = "autonomous outreach"
                self._emit(stage_progress, "Generating autonomous outreach…")
                o = self.outreach.run(r, dm, needs, score, icp, demo=demo)
                self.repo.save_outreach(lead.id, o, "autonomous")
                generated_o = 1
                self.repo.log("outreach", "Autonomous outreach generated", c.company_name)

                stage = "autonomous follow-up"
                self._emit(stage_progress, "Scheduling follow-up intelligence…")
                f = self.followup.run(r, dm, needs, score, icp, demo=demo)
                self.repo.save_followup(lead.id, f)
                generated_f = 1
                self.repo.log("followup", "Autonomous follow-up created", c.company_name)

            self._emit(stage_progress, "Complete")
            return lead, generated_o, generated_f
        except Exception as exc:
            message = str(exc)
            if lead is not None:
                self.repo.mark_lead_partial(lead.id, f"{stage}: {message}")
            raise PipelineCompanyError(message, stage=stage, lead_id=lead.id if lead else None) from exc

    def process_batch(
        self,
        companies: list[CompanyInput],
        icp: ICPInput,
        demo=False,
        autonomous=False,
        auto_classes=None,
        progress=None,
    ):
        run = self.repo.create_run(len(companies), "demo" if demo else "live", autonomous)
        ok = fail = qualified = priority = outs = fups = 0
        errors = []
        leads = []

        def notify(i, total, name, stage):
            if not progress:
                return
            try:
                progress(i, total, name, stage)
            except TypeError:
                progress(i, total, name)

        for idx, c in enumerate(companies, 1):
            try:
                lead, o, f = self.process_company(
                    c,
                    icp,
                    demo,
                    autonomous,
                    auto_classes,
                    stage_progress=lambda stage, i=idx, name=c.company_name: notify(
                        i, len(companies), name, stage
                    ),
                )
                leads.append(lead)
                ok += 1
                outs += o
                fups += f
                if lead.score >= self.repo.get_thresholds()["WARM"]:
                    qualified += 1
                if lead.classification in {"HOT", "HIGH PRIORITY"}:
                    priority += 1
            except PipelineCompanyError as e:
                fail += 1
                error_text = f"{c.company_name}: {e.stage}: {e}"
                errors.append(error_text)
                if e.lead_id is None:
                    failed_lead = self.repo.save_failed_lead(c, str(e), e.stage)
                    leads.append(failed_lead)
                else:
                    existing = self.repo.get_lead(e.lead_id)
                    if existing:
                        leads.append(existing)
                self.repo.log("error", f"Partial failure during {e.stage}: {e}", c.company_name)
                notify(idx, len(companies), c.company_name, "Failed / Partial")
            except Exception as e:
                fail += 1
                errors.append(f"{c.company_name}: {e}")
                failed_lead = self.repo.save_failed_lead(c, str(e), "pipeline")
                leads.append(failed_lead)
                self.repo.log("error", f"Partial failure: {e}", c.company_name)
                notify(idx, len(companies), c.company_name, "Failed / Partial")

        self.repo.finish_run(
            run,
            companies_successful=ok,
            companies_failed=fail,
            qualified_leads=qualified,
            priority_leads=priority,
            outreach_generated=outs,
            followups_generated=fups,
            error_summary="\n".join(errors) or None,
        )
        return {
            "run": run,
            "leads": leads,
            "successful": ok,
            "failed": fail,
            "errors": errors,
        }
