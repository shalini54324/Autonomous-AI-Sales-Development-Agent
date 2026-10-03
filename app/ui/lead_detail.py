from __future__ import annotations
import json
import streamlit as st
from app.schemas.lead import ResearchResult, DecisionMaker, NeedItem, ScoreResult
from app.schemas.company import CompanyInput
from app.ui.components import title_block, badge, status_pill
from app.agents.outreach_agent import OutreachAgent
from app.agents.followup_agent import FollowUpAgent
from app.pipeline.orchestrator import PipelineOrchestrator


def render(repo, demo_mode=False):
    lid = st.session_state.get("selected_lead_id")
    if not lid:
        st.info("No lead currently selected. Please choose a prospect from the **Leads CRM** page.")
        if st.button("← Back to Leads CRM"):
            st.session_state.page = "Leads"
            st.rerun()
        return
        
    l = repo.get_lead(int(lid))
    if not l:
        st.error("The requested lead record could not be found.")
        return

    r = ResearchResult.model_validate_json(l.research_json)
    dm = DecisionMaker.model_validate_json(l.decision_maker_json)
    needs = [NeedItem.model_validate(x) for x in json.loads(l.needs_json)]
    score = ScoreResult(
        total=l.score,
        classification=l.classification,
        breakdown=json.loads(l.score_breakdown_json),
        rationale=json.loads(l.rationale_json),
    )

    # Lead Header Dossier Card
    website_url = r.website or l.company.website or ""
    website_link = f'<a href="{website_url}" target="_blank" style="color:#4f46e5; text-decoration:none;">{website_url} ↗</a>' if website_url else 'Website unavailable'
    
    st.markdown(
        f'''
        <div class="header-banner">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div class="header-banner-badge">✦ PROSPECT DOSSIER #{l.id}</div>
                    <h1>{l.company.name}</h1>
                    <p>🏢 {r.industry or 'Technology'} &nbsp;•&nbsp; 📍 {r.location or 'Global'} &nbsp;•&nbsp; 🌐 {website_link}</p>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:2rem; font-weight:800; color:#0f172a; line-height:1;">
                        {l.score} <span style="font-size:1rem; color:#64748b; font-weight:600;">/ 100</span>
                    </div>
                    <div style="margin-top:4px;">{badge(l.classification)}</div>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # Error handling / Pipeline partial status alert
    if l.pipeline_status in {"failed", "partial"}:
        message = l.error_message or "Pipeline encountered an exception during processing."
        if l.pipeline_status == "failed":
            st.error(f"Pipeline Status: FAILED — {message}")
            if st.button("🔄 Retry Intelligence Pipeline", type="primary"):
                company = CompanyInput(
                    company_name=l.company.name,
                    website=l.company.website,
                    industry=l.company.industry,
                    location=l.company.location,
                    employee_count=l.company.employee_count,
                    source=l.company.source,
                    source_note=l.company.source_note,
                )
                result = PipelineOrchestrator(repo).process_batch(
                    [company], repo.get_icp(), demo=demo_mode, autonomous=False
                )
                if result["successful"]:
                    st.success("Retry finished successfully. Please refresh the latest record from Leads CRM.")
                else:
                    st.warning("Retry still could not complete cleanly. Error has been recorded.")
        else:
            st.warning(f"Pipeline Status: PARTIAL — {message}")

    # Action Toolbar
    act_col1, act_col2, act_col3 = st.columns([1.5, 1.5, 3])
    with act_col1:
        if st.button("✉️ Generate Outreach Draft", type="primary", disabled=l.pipeline_status == "failed", key="btn_gen_out"):
            icp = repo.get_icp()
            content = OutreachAgent().run(r, dm, needs, score, icp, demo=demo_mode)
            repo.save_outreach(l.id, content)
            st.success("Personalized outreach drafted and saved to repository.")
            st.rerun()
    with act_col2:
        if st.button("⏱️ Generate Follow-Up Plan", disabled=l.pipeline_status == "failed", key="btn_gen_fup"):
            icp = repo.get_icp()
            content = FollowUpAgent().run(r, dm, needs, score, icp, demo=demo_mode)
            repo.save_followup(l.id, content)
            st.success("Follow-up sequence created and scheduled.")
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 7 Structured Dossier Tabs
    tabs = st.tabs(
        [
            "📋 Overview",
            "👤 Decision Maker",
            "🎯 Needs & Pain Points",
            "📊 Score Breakdown",
            "✉️ Outreach Drafts",
            "⏱️ Follow-Up Schedule",
            "🔍 Research Evidence",
        ]
    )

    # TAB 1: Overview
    with tabs[0]:
        st.markdown(
            f'''
            <div class="card">
                <div style="font-size:0.95rem; font-weight:750; color:#0f172a; margin-bottom:8px;">
                    Company Summary
                </div>
                <div style="font-size:0.88rem; color:#334155; line-height:1.6; margin-bottom:14px;">
                    {r.description or 'No detailed description available.'}
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                    <div>
                        <span style="font-size:0.78rem; font-weight:700; color:#64748b; text-transform:uppercase;">Business Model</span>
                        <div style="font-size:0.88rem; font-weight:600; color:#0f172a; margin-top:2px;">{r.business_model or 'B2B'}</div>
                    </div>
                    <div>
                        <span style="font-size:0.78rem; font-weight:700; color:#64748b; text-transform:uppercase;">Pipeline Health</span>
                        <div style="font-size:0.88rem; font-weight:600; color:#0f172a; margin-top:2px;">{status_pill(l.pipeline_status)}</div>
                    </div>
                </div>
                <div style="margin-top:14px;">
                    <span style="font-size:0.78rem; font-weight:700; color:#64748b; text-transform:uppercase;">Core Products / Services</span>
                    <div style="margin-top:6px; display:flex; flex-wrap:wrap; gap:6px;">
                        {"".join(f'<span class="pill low">{prod}</span>' for prod in r.products_services) if r.products_services else '<span style="color:#64748b; font-size:0.85rem;">Not listed</span>'}
                    </div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        if l.error_message:
            st.info(f"**Pipeline Note:** {l.error_message}")

    # TAB 2: Decision Maker
    with tabs[1]:
        st.markdown(
            f'''
            <div class="card">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:14px;">
                    <div style="width:44px; height:44px; border-radius:50%; background:#eef2ff; color:#4f46e5; display:flex; align-items:center; justify-content:center; font-size:1.3rem; font-weight:800;">
                        👤
                    </div>
                    <div>
                        <div style="font-size:1.15rem; font-weight:800; color:#0f172a;">{dm.name}</div>
                        <div style="font-size:0.85rem; font-weight:600; color:#4f46e5;">{dm.role}</div>
                    </div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 14px; margin-bottom:12px;">
                    <div style="font-size:0.78rem; font-weight:700; color:#64748b; text-transform:uppercase; margin-bottom:4px;">
                        Relevance Rationale
                    </div>
                    <div style="font-size:0.86rem; color:#334155; line-height:1.5;">
                        {dm.relevance_reason}
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:0.80rem; font-weight:700; color:#64748b;">Confidence Rating:</span>
                    <span class="pill ai">{dm.confidence}</span>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    # TAB 3: Needs & Pain Points
    with tabs[2]:
        if not needs:
            st.info("No specific business needs or pain points identified for this account.")
        for n in needs:
            st.markdown(
                f'''
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="font-size:0.95rem; font-weight:750; color:#0f172a;">🎯 {n.need}</span>
                        <span class="pill {'hot' if n.relevance=='high' else 'warm'}">{n.relevance.upper()} PRIORITY</span>
                    </div>
                    <div style="font-size:0.85rem; color:#475467; margin-bottom:10px;">
                        <b>Evidence & Context:</b> {n.evidence_reasoning}
                    </div>
                    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:8px 12px; font-size:0.82rem; color:#166534;">
                        <b>💡 Value Proposition Match:</b> {n.product_connection}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True,
            )

    # TAB 4: Score Breakdown
    with tabs[3]:
        st.markdown(
            '''
            <div style="font-size:0.95rem; font-weight:750; color:#0f172a; margin-bottom:8px;">
                Weighted ICP Fit Analysis
            </div>
            ''',
            unsafe_allow_html=True,
        )
        maxima = {
            "Industry Fit": 20,
            "Size Fit": 15,
            "Location Fit": 10,
            "Decision Maker": 15,
            "Need Fit": 25,
            "Technology Fit": 8,
            "Signals": 7,
            "Research Confidence": 5,
        }
        b_cols = st.columns(2)
        items = list(score.breakdown.items())
        half = (len(items) + 1) // 2
        
        with b_cols[0]:
            for k, v in items[:half]:
                max_v = maxima.get(k, 20)
                st.write(f"**{k}** ({v} / {max_v} pts)")
                st.progress(min(1.0, v / max(1, max_v)))
        with b_cols[1]:
            for k, v in items[half:]:
                max_v = maxima.get(k, 20)
                st.write(f"**{k}** ({v} / {max_v} pts)")
                st.progress(min(1.0, v / max(1, max_v)))

        st.markdown(
            f'''
            <div style="background:#eef2ff; border:1px solid #c7d2fe; border-radius:10px; padding:14px 16px; margin-top:16px;">
                <div style="font-size:0.82rem; font-weight:750; color:#4338ca; text-transform:uppercase; margin-bottom:4px;">
                    🤖 AI Scoring Rationale
                </div>
                <div style="font-size:0.88rem; color:#1e1b4b; line-height:1.5;">
                    {score.rationale}
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    # TAB 5: Outreach Drafts
    with tabs[4]:
        rows = [o for o in l.outreaches]
        if not rows:
            st.info("No outreach draft generated yet. Click **Generate Outreach Draft** above to create one.")
        else:
            for idx, o in enumerate(rows):
                with st.expander(f"✉️ Draft #{o.id}: {o.subject}", expanded=(idx == len(rows) - 1)):
                    st.text_input("Subject Line", o.subject, key=f"d_sub_{o.id}")
                    st.text_area("Email Content", o.body, height=220, key=f"d_body_{o.id}")
                    st.caption("Status: " + o.status.title())

    # TAB 6: Follow-Up Schedule
    with tabs[5]:
        if not l.followups:
            st.info("No follow-up action scheduled yet. Click **Generate Follow-Up Plan** above to create one.")
        else:
            for f in l.followups:
                due = f.scheduled_for.strftime("%d %b %Y") if f.scheduled_for else "Needs Review"
                st.markdown(
                    f'''
                    <div class="card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-size:0.95rem; font-weight:750; color:#0f172a;">⚡ {f.action}</span>
                            <span class="pill {'ready' if f.status=='done' else 'review'}">Due: {due}</span>
                        </div>
                        <div style="font-size:0.85rem; color:#334155; margin-bottom:8px;">
                            <b>Timing:</b> {f.timing}
                        </div>
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 12px; font-size:0.84rem; color:#1e293b; margin-bottom:8px;">
                            {f.message}
                        </div>
                        <div style="font-size:0.78rem; color:#64748b;">
                            <b>Strategy:</b> {f.reason}
                        </div>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )

    # TAB 7: Research Evidence
    with tabs[6]:
        st.markdown(
            f'''
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-size:0.92rem; font-weight:750; color:#0f172a;">Research Audit Trail</span>
                    <span class="pill ai">Status: {r.research_status.upper()}</span>
                </div>
                <div style="font-size:0.84rem; color:#475467;">
                    Verified intelligence signals collected during automated prospect analysis:
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        if not r.evidence:
            st.caption("No external evidence snippets attached.")
        else:
            for e in r.evidence:
                st.markdown(f"• &nbsp; <span style='font-size:0.85rem; color:#334155;'>{e}</span>", unsafe_allow_html=True)
