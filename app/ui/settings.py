from __future__ import annotations
import streamlit as st
from app.ui.components import title_block, badge
from app.config import settings


def render(repo):
    title_block(
        "Agent Settings & Safety Guardrails",
        "Runtime parameters, qualification thresholds, LLM configuration, and data integrity policies.",
        badge_text="SYSTEM SETTINGS",
    )

    # Card 1: Runtime & Model Architecture
    st.markdown(
        f'''
        <div class="card">
            <div style="font-size:0.95rem; font-weight:750; color:#0f172a; margin-bottom:12px;">
                🤖 AI Model & Runtime Infrastructure
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 14px;">
                    <span style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">OpenAI API Status</span>
                    <div style="font-size:0.92rem; font-weight:700; color:#0f172a; margin-top:2px;">
                        {'🟢 Active & Connected' if settings.live_ai_available else '🟣 Standalone Demo Mode (Offline)'}
                    </div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 14px;">
                    <span style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Configured Model</span>
                    <div style="font-size:0.92rem; font-weight:700; color:#0f172a; margin-top:2px;">
                        {settings.openai_model}
                    </div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 14px;">
                    <span style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Database URI</span>
                    <div style="font-size:0.85rem; font-weight:600; color:#0f172a; margin-top:2px; word-break:break-all;">
                        {settings.database_url}
                    </div>
                </div>
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 14px;">
                    <span style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase;">Batch Throughput Cap</span>
                    <div style="font-size:0.92rem; font-weight:700; color:#0f172a; margin-top:2px;">
                        {settings.max_companies_per_run} companies / run
                    </div>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # Card 2: Qualification Thresholds
    st.markdown(
        '''
        <div class="card">
            <div style="font-size:0.95rem; font-weight:750; color:#0f172a; margin-bottom:6px;">
                🎯 Lead Score Classification Thresholds
            </div>
            <div style="font-size:0.82rem; color:#64748b; margin-bottom:14px;">
                Prospects scoring above these minimum scores will be assigned into corresponding priority tiers.
            </div>
        ''',
        unsafe_allow_html=True,
    )
    current = repo.get_thresholds()
    c1, c2, c3 = st.columns(3)
    hot = c1.number_input("🔥 HOT Minimum Score", 0, 100, value=current["HOT"])
    high = c2.number_input("⚡ HIGH PRIORITY Minimum Score", 0, 100, value=current["HIGH PRIORITY"])
    warm = c3.number_input("🌤️ WARM Minimum Score", 0, 100, value=current["WARM"])

    if st.button("💾 Save Threshold Settings", type="primary"):
        try:
            repo.save_thresholds(int(hot), int(high), int(warm))
            st.success("Lead qualification thresholds saved and active.")
        except Exception as e:
            st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)

    # Card 3: Security & Privacy Guardrails
    st.markdown(
        '''
        <div class="card" style="background:#f8faff; border-color:#e0e7ff;">
            <div style="font-size:0.92rem; font-weight:750; color:#3730a3; margin-bottom:4px;">
                🛡️ Enterprise Privacy & Key Security Guardrails
            </div>
            <div style="font-size:0.84rem; color:#4338ca; line-height:1.5;">
                • API keys are strictly loaded from local environment files (<code>.env</code>) and are never logged, echoed, or persisted in the database.<br>
                • Scraped public business intelligence is cached with TTL to avoid redundant network queries and minimize model token consumption.<br>
                • Autonomous actions respect strict priority filters and require human review whenever confidence criteria are ambiguous.
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
