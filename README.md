# Autonomous AI Sales Development Agent

A professional internship-grade Streamlit application that turns target companies into structured, explainable sales intelligence through one central pipeline: **research → decision maker → needs → ICP fit → scoring → prioritization → outreach → follow-up → automation**.

## Problem Statement
Traditional prospecting is slow, repetitive and inconsistent. Sales teams repeatedly research companies, identify relevant buyers, infer business needs, qualify leads, prioritize accounts and write follow-ups. This project combines Generative AI with deterministic application logic, explainable scoring and persistent workflow state.

## Solution
The application provides a unified prospecting workspace with four acquisition paths—AI-assisted discovery, manual entry, CSV import and Demo Mode. Every prospect is processed by the same pipeline. AI enriches research synthesis and messaging; conventional code handles validation, persistence, CSV parsing, thresholds, filtering and run tracking.

## Key Features
- Persistent Ideal Customer Profile configuration
- Manual, CSV, AI-assisted and Demo prospect acquisition
- Manual parser supports compact rows and labelled multi-line company blocks
- Cautious website research with evidence capture
- Decision-maker reasoning and needs analysis
- Explainable 0–100 lead scoring with persistent configurable classification thresholds
- Searchable/sortable lead management with classification, industry, outreach and pipeline-status filters
- Personalized outreach and follow-up generation with persisted due dates and Due Today / Upcoming / Needs Review grouping
- Optional Autonomous Mode for selected priority classes
- Partial-failure resilience across batches with visible Failed/Partial lead records and retry support
- SQLite persistence and pipeline run history
- Light, colorful professional SaaS UI
- Meaningful pytest suite with external AI mocked/avoided

## System Architecture
```text
Streamlit UI
   ↓
Central PipelineOrchestrator
   ├─ CompanyResearchAgent → ResearchService → website/OpenAI
   ├─ DecisionMakerAgent
   ├─ NeedsAnalysisAgent
   ├─ LeadScoringAgent → deterministic ScoringService
   ├─ OutreachAgent → OpenAI/Demo generator
   └─ FollowUpAgent → OpenAI/Demo generator
   ↓
Repository → SQLAlchemy → SQLite
```

## AI Workflow
OpenAI is used only for intelligence-heavy work when Live Mode is configured. Demo Mode returns clearly labelled deterministic fictional sample intelligence with intentionally varied ICP fit, so scoring demonstrates HOT/HIGH/WARM/LOW outcomes instead of forcing every prospect to qualify. The application never labels demo data as live research.

## Technology Stack
Python, Streamlit, SQLAlchemy, SQLite, Pydantic, OpenAI API, pandas, requests, BeautifulSoup, python-dotenv and pytest.

## Installation
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `app/.env` and add an API key if Live Mode is desired:
```env
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini
```
Never commit the `.env` file.

## How to Run
```bash
streamlit run app/app.py
```
Required SQLite directories and tables are initialized automatically.

## How to Run Tests
```bash
pytest -q
```

## Live Mode
With `OPENAI_API_KEY` configured, the app can fetch public website text and use the configured model to synthesize structured intelligence. Missing or unverifiable information is represented as Unknown/Not available instead of invented precise facts.

## Demo Mode
Demo Mode requires no API credits or internet access. It uses clearly fictional sample companies and deliberately includes strong, medium and weak ICP fits so the scoring and human-review logic can be demonstrated honestly.

## Autonomous Mode
When enabled, only user-selected classifications are auto-processed. The default classes are `HOT` and `HIGH PRIORITY`. Lower-quality leads remain available for human review unless explicitly configured otherwise. Lead-classification thresholds can be changed and persisted from Settings.

## Database
SQLite persists ICPs, companies, research-derived lead records, score breakdowns, outreach, follow-ups, activity events and pipeline runs.

## Project Structure
```text
app/
  agents/        AI/domain agents
  pipeline/      central orchestration
  services/      OpenAI, research, discovery, scoring and messaging
  database/      SQLAlchemy database + repositories
  schemas/       Pydantic validation models
  ui/            Streamlit pages/components/styles
  utils/         parsers and follow-up date utilities
  tests/         pytest suite
  app.py         application entry point
```

## Internship Demo Flow
1. Open **ICP Configuration** and save the default SaaS ICP.
2. Open **Discovery** and choose **Demo** (or AI Discovery in Live Mode).
3. Run five prospects and watch batch progress.
4. Open **Leads** and inspect score/classification/needs.
5. Open **Lead Detail** to see evidence and score breakdown.
6. Generate outreach and a follow-up.
7. Repeat with **Autonomous Mode** enabled for HOT/HIGH PRIORITY.
8. Open **Pipeline Runs** and **Overview** to show persistence and history.

## Screenshots
Add portfolio screenshots here after running the application locally:
- Overview dashboard
- Discovery workspace
- Lead detail + score breakdown
- Outreach workspace
- Pipeline run history

## Future Improvements
- Auth/RBAC and multi-user workspaces
- Verified third-party enrichment providers
- CRM integrations
- Email/calendar connectors
- Scheduled cadence engine
- Vector-backed account memory
- Production deployment and observability
