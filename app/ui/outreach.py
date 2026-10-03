from __future__ import annotations
import json
import streamlit as st
from app.ui.components import title_block, badge, status_pill
from app.schemas.lead import ResearchResult, DecisionMaker, NeedItem, ScoreResult
from app.agents.outreach_agent import OutreachAgent


def render(repo, demo_mode=False):
    title_block(
        "Outreach Email Workspace",
        "Review, customize, and approve AI-generated sales emails with live prospect intelligence side-by-side.",
        badge_text="SALES OUTREACH",
    )
    leads = repo.list_leads()
    if not leads:
        st.info("No leads available in the database yet. Discover and qualify prospects first.")
        return

    # Select Lead Selector Card
    st.markdown(
        '''
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:12px 18px; margin-bottom:18px; box-shadow:0 1px 3px rgba(15,23,42,0.04);">
            <div style="font-size:0.82rem; font-weight:750; color:#64748b; text-transform:uppercase; margin-bottom:6px;">
                Active Prospect Workspace
            </div>
        ''',
        unsafe_allow_html=True,
    )
    lid = st.selectbox(
        "Select Prospect Account",
        [l.id for l in leads],
        format_func=lambda x: next(f"{l.company.name} ({l.classification} · Score {l.score})" for l in leads if l.id == x),
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    l = repo.get_lead(lid)
    r = ResearchResult.model_validate_json(l.research_json)
    dm = DecisionMaker.model_validate_json(l.decision_maker_json)
    needs = [NeedItem.model_validate(x) for x in json.loads(l.needs_json)]
    score = ScoreResult(
        total=l.score,
        classification=l.classification,
        breakdown=json.loads(l.score_breakdown_json),
        rationale=json.loads(l.rationale_json),
    )

    col_editor, col_context = st.columns([2.2, 1.1])

    # Left: Email Editor
    with col_editor:
        btn_c1, btn_c2 = st.columns([1.5, 2])
        with btn_c1:
            if st.button("✨ Generate / Regenerate AI Draft", type="primary", key="btn_regen_outreach"):
                with st.spinner("AI drafting hyper-personalized outreach..."):
                    content = OutreachAgent().run(r, dm, needs, score, repo.get_icp(), demo=demo_mode)
                    repo.save_outreach(l.id, content)
                st.success("Draft updated.")
                st.rerun()

        if l.outreaches:
            o = l.outreaches[-1]
            st.markdown(
                f'''
                <div style="display:flex; justify-content:space-between; align-items:center; margin:12px 0 6px 0;">
                    <span style="font-size:0.85rem; font-weight:750; color:#0f172a;">Subject & Message Body</span>
                    <span>Status: {status_pill(o.status)}</span>
                </div>
                ''',
                unsafe_allow_html=True,
            )
            subj = st.text_input("Subject Line", o.subject, key=f"subject_{o.id}")
            body = st.text_area("Email Content", o.body, height=280, key=f"body_{o.id}")
            
            # Action status toolbar
            act1, act2, act3 = st.columns(3)
            with act1:
                if st.button("✅ Mark Ready", key="btn_ready"):
                    o.subject = subj
                    o.body = body
                    o.status = "ready"
                    repo.s.commit()
                    st.success("Marked ready to send.")
                    st.rerun()
            with act2:
                if st.button("🚀 Mark Sent", key="btn_sent"):
                    o.subject = subj
                    o.body = body
                    o.status = "sent"
                    repo.s.commit()
                    st.success("Recorded as sent.")
                    st.rerun()
            with act3:
                if st.button("⚠️ Needs Review", key="btn_review"):
                    o.subject = subj
                    o.body = body
                    o.status = "review"
                    repo.s.commit()
                    st.warning("Flagged for SDR review.")
                    st.rerun()

            with st.expander("📋 Copy Plaintext Output"):
                st.code(o.body, language=None)
        else:
            st.info("No outreach draft exists for this account yet. Click **Generate / Regenerate AI Draft** to create one.")

    # Right: AI Context Card
    with col_context:
        st.markdown(
            f'''
            <div class="card" style="margin-top:0;">
                <div style="font-size:0.92rem; font-weight:800; color:#0f172a; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
                    <span>🧠 AI Account Context</span>
                    <span>{badge(l.classification)}</span>
                </div>
                
                <div style="margin-bottom:12px;">
                    <span style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Fit Score</span>
                    <div style="font-size:1.4rem; font-weight:800; color:#4f46e5;">{l.score} <span style="font-size:0.85rem; color:#64748b;">/ 100</span></div>
                </div>
                
                <div style="margin-bottom:12px;">
                    <span style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Decision Maker</span>
                    <div style="font-size:0.88rem; font-weight:700; color:#0f172a;">{dm.name}</div>
                    <div style="font-size:0.80rem; color:#475467;">{dm.role}</div>
                </div>
                
                <div style="margin-bottom:12px;">
                    <span style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Primary Pain Point</span>
                    <div style="font-size:0.84rem; color:#334155; line-height:1.4; margin-top:2px;">
                        {needs[0].need if needs else 'Not detected'}
                    </div>
                </div>
                
                <div style="background:#f8faff; border:1px solid #e0e7ff; border-radius:8px; padding:10px; font-size:0.80rem; color:#3730a3;">
                    <b>💡 Messaging Strategy:</b> Lead with specific workflow bottlenecks and reference verified industry evidence.
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
