# Fixes in v1.1.0

This build closes the gaps found during the full specification audit.

- Manual input now supports labelled multi-line company blocks without treating Website/Industry/Location/Employees as separate companies.
- CSV parsing reports invalid URLs safely.
- Demo Mode now uses clearly fictional sample companies and produces realistic scoring diversity instead of forcing every prospect to HOT.
- Failed core-pipeline prospects are persisted as `failed` leads with a useful error reason.
- Failures after intelligence persistence (for example autonomous outreach failure) mark the lead `partial` instead of leaving it `complete`.
- Lead Management now supports industry, outreach-status and pipeline-status filters plus sorting and a Next Action column.
- Follow-ups now persist a scheduled timestamp and are grouped by actual Due Today / Upcoming / Needs Review logic.
- AI Discovery includes Select All and Deselect All controls.
- Pipeline UI reports stage-level progress (research, decision maker, needs, scoring, persistence, autonomous actions).
- Failed lead detail pages surface the error and provide Retry Intelligence.
- Added regression tests for all of the above plus custom thresholds and malformed AI responses.

Verification: `24 passed` and `SMOKE_DEMO_OK`.
