from __future__ import annotations
import json
import streamlit as st
from app.ui.components import title_block, badge, status_pill


def _latest_status(items, default="Not generated"):
    if not items:
        return default
    latest = max(items, key=lambda x: x.id)
    return latest.status.replace("_", " ").title()


def _next_action(lead):
    if lead.pipeline_status in {"failed", "partial"}:
        return "Retry / Review Error"
    pending = [f for f in lead.followups if f.status not in {"done", "completed"}]
    if pending:
        latest = max(pending, key=lambda x: x.id)
        return latest.action
    if lead.outreaches:
        return "Create Follow-Up"
    return "Generate Outreach"


def render(repo):
    title_block(
        "Lead Management CRM",
        "Search, filter, and triage prospects with explainable ICP scoring, persona intelligence, and workflow status.",
        badge_text="LEAD PIPELINE",
    )
    leads = repo.list_leads()
    if not leads:
        st.info("No leads in your pipeline yet. Go to **Discovery** to discover and research prospects.")
        return

    industries = sorted({(l.company.industry or "Unknown") for l in leads})
    pipeline_states = sorted({l.pipeline_status for l in leads})
    outreach_states = sorted({_latest_status(l.outreaches) for l in leads})

    # CRM Filter Bar
    st.markdown(
        '''
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px 18px 4px 18px; margin-bottom:16px; box-shadow:0 1px 3px rgba(15,23,42,0.04);">
        ''',
        unsafe_allow_html=True,
    )
    
    f1, f2, f3, f4 = st.columns([2, 1.2, 1.2, 1.2])
    q = f1.text_input("🔍 Search Company Name", placeholder="Type company name...")
    cls = f2.multiselect("Classification", ["HOT", "HIGH PRIORITY", "WARM", "LOW"], default=[])
    industry_filter = f3.multiselect("Industry", industries, default=[])
    minscore = f4.slider("Minimum Fit Score", 0, 100, 0)

    g1, g2, g3 = st.columns([1.3, 1.3, 1.4])
    outreach_filter = g1.multiselect("Outreach Status", outreach_states, default=[])
    pipeline_filter = g2.multiselect("Pipeline Status", pipeline_states, default=[])
    sort_by = g3.selectbox(
        "Sort Order",
        ["Score: High to Low", "Score: Low to High", "Newest Added", "Company A–Z"],
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

    rows = []
    for l in leads:
        company_industry = l.company.industry or "Unknown"
        outreach_status = _latest_status(l.outreaches)
        if q and q.lower() not in l.company.name.lower():
            continue
        if cls and l.classification not in cls:
            continue
        if industry_filter and company_industry not in industry_filter:
            continue
        if outreach_filter and outreach_status not in outreach_filter:
            continue
        if pipeline_filter and l.pipeline_status not in pipeline_filter:
            continue
        if l.score < minscore:
            continue

        try:
            dm = json.loads(l.decision_maker_json)
            dm_str = f"{dm.get('name', 'Unknown')} · {dm.get('role', 'Unknown')}"
        except Exception:
            dm_str = "Unknown Contact"

        try:
            needs = json.loads(l.needs_json)
            top_need = needs[0].get("need") if needs else "—"
        except Exception:
            top_need = "—"

        rows.append(
            {
                "Lead ID": l.id,
                "Company": l.company.name,
                "Industry": company_industry,
                "Decision Maker": dm_str,
                "Score": l.score,
                "Tier": l.classification,
                "Key Need": top_need,
                "Outreach Status": outreach_status,
                "Pipeline Status": l.pipeline_status.title(),
                "Next Action": _next_action(l),
                "Created": l.created_at,
            }
        )

    if sort_by == "Score: High to Low":
        rows.sort(key=lambda x: (x["Score"], x["Created"]), reverse=True)
    elif sort_by == "Score: Low to High":
        rows.sort(key=lambda x: (x["Score"], x["Created"]))
    elif sort_by == "Newest Added":
        rows.sort(key=lambda x: x["Created"], reverse=True)
    else:
        rows.sort(key=lambda x: x["Company"].lower())

    display_rows = [{k: v for k, v in r.items() if k != "Created"} for r in rows]
    if not display_rows:
        st.info("No leads match your selected filters. Adjust your search criteria above.")
        return

    # Table Count Summary
    st.markdown(
        f'<div style="font-size:0.85rem; font-weight:700; color:#64748b; margin-bottom:8px;">'
        f'Showing {len(display_rows)} of {len(leads)} leads</div>',
        unsafe_allow_html=True,
    )
    
    st.dataframe(display_rows, use_container_width=True, hide_index=True)

    # Lead Detail Navigation Action Box
    st.markdown(
        '''
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px 20px; margin-top:16px; box-shadow:0 1px 3px rgba(15,23,42,0.04);">
            <div style="font-size:0.92rem; font-weight:750; color:#0f172a; margin-bottom:8px;">
                🎯 Open Deep Intelligence Dossier
            </div>
        ''',
        unsafe_allow_html=True,
    )
    nav_c1, nav_c2 = st.columns([3, 1])
    lead_ids = [r["Lead ID"] for r in rows]
    chosen = nav_c1.selectbox(
        "Select Prospect",
        lead_ids,
        format_func=lambda x: next(f"{r['Company']} (Score: {r['Score']} | {r['Tier']})" for r in rows if r["Lead ID"] == x),
        label_visibility="collapsed",
    )
    if nav_c2.button("Open Lead Detail →", type="primary"):
        st.session_state.selected_lead_id = chosen
        st.session_state.page = "Lead Detail"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
