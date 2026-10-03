# Verification Report — v1.1.0

## Automated tests
`python -m pytest -q` → **24 passed**

Coverage includes:
- ICP validation
- compact manual company parsing
- labelled multi-line manual blocks (Website / Industry / Location / Employees are not treated as companies)
- orphan metadata handling
- CSV parsing and invalid-URL reporting
- deterministic lead scoring and classification
- persistent configurable score thresholds
- SQLite repository persistence
- central pipeline processing
- partial batch resilience
- persisted `failed` lead state with useful error reason
- persisted `partial` lead state when autonomous outreach fails after intelligence has been saved
- HOT autonomous outreach + follow-up
- HIGH PRIORITY autonomous outreach + follow-up
- LOW lead protection from autonomous processing
- real scheduled follow-up timestamps
- stage-level progress callbacks
- run-history ordering
- outreach/follow-up interfaces
- Demo Mode score diversity (HOT / HIGH PRIORITY / WARM / LOW)
- AI-unavailable validation
- malformed JSON and schema-invalid AI response handling

## End-to-end Demo Mode smoke test
`python -m app.scripts.smoke_demo` → **SMOKE_DEMO_OK**

Verified five prospects through the real application pipeline:
Discovery → Research → Decision Maker → Needs → Score → Classification → Persistence → Autonomous Outreach → Follow-Up Scheduling.

Observed result:
- 5 submitted
- 5 successful
- 0 failed
- 5 persisted leads
- classifications: HOT, HIGH PRIORITY, HIGH PRIORITY, WARM, LOW
- 3 outreach records (only HOT/HIGH PRIORITY)
- 3 follow-up records (only HOT/HIGH PRIORITY)
- all generated follow-ups have persisted scheduled dates

This confirms Demo Mode no longer forces every prospect into a priority class.

## Static/runtime checks
- `python -m compileall -q app` passes.
- SQLite schema initialization passes.
- Lightweight migration support adds new follow-up scheduling columns to older SQLite databases.
- No real `.env` file is included.
- `.gitignore` excludes `.env` and SQLite runtime databases.
- Source scan contains no `sk-...` style API key.

## Browser-runtime environment limitation
The execution sandbox does not have Streamlit or the OpenAI Python package preinstalled. An actual `pip install -r requirements.txt` was attempted, but outbound package access failed because the sandbox DNS/network cannot reach the package index. Therefore the browser UI and a real OpenAI request cannot be launched in this sandbox.

The dependencies are declared in `requirements.txt`. In a normal connected environment:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/app.py
```

All code paths that do not require those unavailable packages were executed and verified as described above.
