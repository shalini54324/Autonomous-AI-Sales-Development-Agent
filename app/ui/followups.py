from __future__ import annotations
from datetime import datetime, timezone
import json
import streamlit as st
from app.ui.components import title_block, badge, status_pill


def _day(value):
    return value.date() if value else None


def _card(f):
    try:
        dm = json.loads(f.lead.decision_maker_json)
        dm_text = f"{dm.get('name', 'Contact')} · {dm.get('role', 'Executive')}"
    except Exception:
        dm_text = "Executive Contact"

    latest_outreach = max(f.lead.outreaches, key=lambda x: x.id) if f.lead.outreaches else None
    due_text = f.scheduled_for.strftime("%d %b %Y") if f.scheduled_for else "Needs Review"
    
    st.markdown(
        f'''
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
                <div>
                    <span style="font-size:1.05rem; font-weight:800; color:#0f172a;">{f.lead.company.name}</span>
                    &nbsp; {badge(f.lead.classification)}
                    <div style="font-size:0.80rem; color:#475467; margin-top:2px;">👤 {dm_text}</div>
                </div>
                <div style="text-align:right;">
                    <span class="pill {'hot' if 'Needs' in due_text else 'ai'}">📅 Due: {due_text}</span>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Timing: {f.timing}</div>
                </div>
            </div>
            
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 14px; margin:10px 0;">
                <div style="font-size:0.82rem; font-weight:750; color:#4f46e5; text-transform:uppercase; margin-bottom:4px;">
                    ⚡ Action: {f.action}
                </div>
                <div style="font-size:0.86rem; color:#1e293b; line-height:1.5;">
                    {f.message}
                </div>
            </div>
            
            <div style="font-size:0.80rem; color:#64748b;">
                <b>Rationale:</b> {f.reason}
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    if latest_outreach:
        with st.expander(f"✉️ Context: Previous Outreach Sent ({latest_outreach.subject})"):
            st.write(latest_outreach.body)


def render(repo):
    title_block(
        "Follow-Up Cadence Engine",
        "Automated sequencing and timing recommendations for prospect engagement. Tasks requiring manual discretion are held for review.",
        badge_text="CADENCE & FOLLOW-UP",
    )
    rows = repo.list_followups()
    if not rows:
        st.info("No follow-ups recorded yet. Run leads through Autonomous Mode or generate follow-ups individually in Lead Detail.")
        return

    today = datetime.now(timezone.utc).date()
    due_today = [
        f
        for f in rows
        if f.status not in {"done", "completed"}
        and _day(f.scheduled_for) == today
    ]
    upcoming = [
        f
        for f in rows
        if f.status not in {"done", "completed", "review"}
        and f.scheduled_for is not None
        and _day(f.scheduled_for) > today
    ]
    needs_review = [
        f
        for f in rows
        if f.status == "review"
        or f.scheduled_for is None
        or (
            f.status not in {"done", "completed"}
            and f.scheduled_for is not None
            and _day(f.scheduled_for) < today
        )
    ]

    due_tab, upcoming_tab, review_tab = st.tabs(
        [
            f"🔔 Due Today ({len(due_today)})",
            f"📅 Upcoming ({len(upcoming)})",
            f"⚠️ Needs Review ({len(needs_review)})",
        ]
    )
    for container, subset, empty_msg in [
        (due_tab, due_today, "No follow-ups are scheduled for execution today."),
        (upcoming_tab, upcoming, "No upcoming future follow-ups currently on the calendar."),
        (review_tab, needs_review, "All follow-ups have validated schedules; no items require manual review."),
    ]:
        with container:
            if not subset:
                st.caption(empty_msg)
            for f in subset:
                _card(f)
