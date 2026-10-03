from __future__ import annotations
import streamlit as st
from app.ui.components import title_block, render_kpis, status_pill


def render(repo):
    title_block(
        "Pipeline Audit & Execution History",
        "Inspect historical batch executions, throughput, partial failure diagnostics, and autonomous actions.",
        badge_text="RUN AUDIT",
    )
    runs = repo.list_runs()
    if not runs:
        st.info("No pipeline executions recorded yet. Execute discovery to record your first batch run.")
        return

    # Top summary metrics
    total_runs = len(runs)
    total_sub = sum(r.companies_submitted for r in runs)
    total_succ = sum(r.companies_successful for r in runs)
    total_prio = sum(r.priority_leads for r in runs)
    total_out = sum(r.outreach_generated for r in runs)

    render_kpis([
        ("Total Runs", total_runs, "Batch runs executed", "sky", "⚡"),
        ("Prospects", total_sub, f"{total_succ} successful ({int(total_succ/max(1, total_sub)*100)}%)", "teal", "🏢"),
        ("Priority Tiers", total_prio, "Hot & High identified", "coral", "🔥"),
        ("Outreach Generated", total_out, "Emails drafted", "violet", "✉️"),
    ])

    st.markdown(
        '<div style="font-size:1.05rem; font-weight:750; color:#0f172a; margin: 18px 0 10px 0;">'
        'Detailed Run Logs</div>',
        unsafe_allow_html=True,
    )

    for r in runs:
        status_label = "Success" if r.companies_failed == 0 else f"{r.companies_failed} Failed"
        with st.expander(
            f"Run #{r.id} · {r.mode.title()} Mode · {r.started_at.strftime('%Y-%m-%d %H:%M')} · {status_label}",
            expanded=False,
        ):
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Submitted", r.companies_submitted)
            c2.metric("Successful", r.companies_successful)
            c3.metric("Failed", r.companies_failed)
            c4.metric("Qualified", r.qualified_leads)
            c5.metric("Priority Leads", r.priority_leads)
            c6.metric("Outreach", r.outreach_generated)

            st.markdown(
                f'''
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 14px; margin-top:8px; font-size:0.85rem; color:#334155;">
                    <b>Autonomous Mode:</b> {"Yes (Auto-drafted outreach and follow-ups)" if r.autonomous else "No (Manual triage mode)"}
                </div>
                ''',
                unsafe_allow_html=True,
            )
            if r.error_summary:
                st.warning(f"Error diagnostics: {r.error_summary}")
