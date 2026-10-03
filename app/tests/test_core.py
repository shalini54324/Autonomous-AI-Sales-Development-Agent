from app.schemas.icp import ICPInput
from app.schemas.lead import ResearchResult, DecisionMaker, NeedItem
from app.schemas.company import DiscoveryCriteria
from app.services.scoring_service import ScoringService, classify_score
from app.services.discovery_service import DiscoveryService
from app.pipeline.orchestrator import PipelineOrchestrator
from app.utils.parsers import parse_manual_companies, parse_csv_bytes


def icp():
    return ICPInput(
        target_industry="SaaS",
        target_roles=["CTO", "Founder"],
        target_location="Global",
        min_employees=50,
        max_employees=500,
        product_service="AI sales automation",
        ideal_customer_description="Growing SaaS companies",
        known_pain_points=["manual prospecting"],
    )


def test_icp_validation():
    assert icp().target_industry == "SaaS"


def test_manual_company_parsing():
    rows, errs = parse_manual_companies("Acme, https://acme.test\nBeta | https://beta.test")
    assert len(rows) == 2 and not errs and rows[0].company_name == "Acme"


def test_manual_labelled_block_does_not_create_metadata_companies():
    rows, errs = parse_manual_companies(
        "Acme\nWebsite: https://acme.test\nIndustry: SaaS\nLocation: India\nEmployees: 120"
    )
    assert not errs
    assert len(rows) == 1
    assert rows[0].company_name == "Acme"
    assert rows[0].website == "https://acme.test"
    assert rows[0].industry == "SaaS"
    assert rows[0].location == "India"
    assert rows[0].employee_count == 120


def test_orphan_metadata_is_error_not_company():
    rows, errs = parse_manual_companies("Website: https://acme.test\nIndustry: SaaS")
    assert rows == []
    assert len(errs) == 2


def test_csv_parsing():
    rows, errs = parse_csv_bytes(
        b"company_name,website,industry,location\nAcme,https://acme.test,SaaS,India\n"
    )
    assert len(rows) == 1 and not errs


def test_csv_invalid_url_is_reported_without_crashing():
    rows, errs = parse_csv_bytes(
        b"company_name,website,industry,location\nAcme,not a url,SaaS,India\n"
    )
    assert len(rows) == 1
    assert rows[0].website is None
    assert any("invalid website" in e for e in errs)


def test_lead_scoring_and_classification():
    r = ResearchResult(
        company_name="Acme",
        industry="SaaS",
        location="India",
        company_size=100,
        growth_signals=["growth"],
        recent_signals=["launch"],
        research_status="complete",
    )
    dm = DecisionMaker(name="A", role="CTO", company="Acme")
    n = [
        NeedItem(
            need="manual prospecting",
            evidence_reasoning="x",
            relevance="high",
            product_connection="x",
        ),
        NeedItem(
            need="scaling",
            evidence_reasoning="x",
            relevance="medium",
            product_connection="x",
        ),
    ]
    s = ScoringService().calculate(r, dm, n, icp())
    assert 0 <= s.total <= 100
    assert s.classification in {"HOT", "HIGH PRIORITY", "WARM", "LOW"}
    assert sum(s.breakdown.values()) >= s.total


def test_thresholds():
    assert classify_score(90) == "HOT"
    assert classify_score(75) == "HIGH PRIORITY"
    assert classify_score(55) == "WARM"
    assert classify_score(20) == "LOW"


def test_custom_thresholds_persist(repo):
    repo.save_thresholds(90, 75, 55)
    assert repo.get_thresholds() == {
        "HOT": 90,
        "HIGH PRIORITY": 75,
        "WARM": 55,
        "LOW": 0,
    }


def test_demo_mode_has_realistic_score_diversity(repo):
    cfg = icp()
    repo.save_icp(cfg)
    companies = DiscoveryService().discover_demo(
        DiscoveryCriteria(
            industry="SaaS", location="Global", min_employees=50, max_employees=500, count=5
        )
    )
    result = PipelineOrchestrator(repo).process_batch(
        companies,
        cfg,
        demo=True,
        autonomous=True,
        auto_classes={"HOT", "HIGH PRIORITY"},
    )
    classes = {lead.classification for lead in result["leads"]}
    assert result["successful"] == 5
    assert {"HOT", "HIGH PRIORITY", "WARM", "LOW"}.issubset(classes)
    assert len(repo.list_outreaches()) < len(repo.list_leads())
