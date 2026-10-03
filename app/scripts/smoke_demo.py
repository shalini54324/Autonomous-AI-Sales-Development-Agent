from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
from app.database.repositories import Repository
from app.schemas.icp import ICPInput
from app.schemas.company import DiscoveryCriteria
from app.services.discovery_service import DiscoveryService
from app.pipeline.orchestrator import PipelineOrchestrator

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
S = sessionmaker(bind=engine, expire_on_commit=False)
s = S()
repo = Repository(s)
icp = ICPInput(
    target_industry="SaaS",
    target_roles=["CTO", "Founder", "CEO"],
    target_location="Global",
    min_employees=50,
    max_employees=500,
    product_service="AI sales workflow automation platform",
    ideal_customer_description="Growing B2B software teams",
    known_pain_points=["repetitive prospecting", "inconsistent lead qualification", "manual research"],
)
repo.save_icp(icp)
companies = DiscoveryService().discover_demo(
    DiscoveryCriteria(
        industry="SaaS", location="Global", min_employees=50, max_employees=500, count=5
    )
)
result = PipelineOrchestrator(repo).process_batch(
    companies,
    icp,
    demo=True,
    autonomous=True,
    auto_classes={"HOT", "HIGH PRIORITY"},
)
leads = repo.list_leads()
priority_count = sum(l.classification in {"HOT", "HIGH PRIORITY"} for l in leads)
print("submitted=", len(companies))
print("successful=", result["successful"], "failed=", result["failed"])
print(
    "leads=",
    len(leads),
    "outreach=",
    len(repo.list_outreaches()),
    "followups=",
    len(repo.list_followups()),
)
print("scores=", [(l.company.name, l.score, l.classification) for l in leads])
assert result["successful"] == 5 and result["failed"] == 0
assert len(leads) == 5
assert {"HOT", "HIGH PRIORITY", "WARM", "LOW"}.issubset({l.classification for l in leads})
assert len(repo.list_outreaches()) == priority_count
assert len(repo.list_followups()) == priority_count
assert all(f.scheduled_for is not None for f in repo.list_followups())
print("SMOKE_DEMO_OK")
