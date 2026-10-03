from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.config import settings
from app.database.db import get_session, init_db
from app.database.repositories import Repository
from app.ui.styles import CSS
from app.ui import (
    dashboard,
    discovery,
    leads,
    lead_detail,
    outreach,
    followups,
    icp,
    settings as settings_page,
    pipeline_runs,
)

st.set_page_config(
    page_title="SalesPilot AI — Autonomous Sales Development Agent",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)
init_db()

if "page" not in st.session_state:
    st.session_state.page = "Overview"

session = get_session()
repo = Repository(session)

PAGE_MAP = {
    "Overview": "📊  Overview",
    "Discovery": "🔍  Discovery",
    "Leads": "👥  Leads CRM",
    "Lead Detail": "🎯  Lead Detail",
    "Outreach": "✉️  Outreach",
    "Follow-Ups": "⏱️  Follow-Ups",
    "Pipeline Runs": "⚡  Pipeline Runs",
    "ICP Configuration": "⚙️  ICP Configuration",
    "Settings": "🛠️  Settings",
}
REVERSE_PAGE_MAP = {v: k for k, v in PAGE_MAP.items()}

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 4px 0 16px 0;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:1.4rem; color:#4f46e5; font-weight:800;">✦</span>
                <span style="font-size:1.25rem; color:#0f172a; font-weight:800; letter-spacing:-0.02em;">SalesPilot AI</span>
            </div>
            <div style="font-size:0.78rem; color:#64748b; font-weight:600; margin-top:2px;">
                Autonomous Sales Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_labels = list(PAGE_MAP.values())
    curr_key = st.session_state.page
    curr_label = PAGE_MAP.get(curr_key, nav_labels[0])
    curr_idx = nav_labels.index(curr_label) if curr_label in nav_labels else 0

    selected_label = st.radio(
        "Navigation",
        nav_labels,
        index=curr_idx,
        label_visibility="collapsed",
    )
    selected_key = REVERSE_PAGE_MAP.get(selected_label, "Overview")
    if selected_key != st.session_state.page:
        st.session_state.page = selected_key
        st.rerun()

    st.markdown("<hr style='border:0; border-top:1px solid #e2e8f0; margin:16px 0;'>", unsafe_allow_html=True)

    live = settings.live_ai_available
    auto_active = st.session_state.get("autonomous_active", False)

    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="sidebar-card-label">OpenAI Connection</div>
            <div class="sidebar-card-value">
                {"<span style='color:#10b981;font-size:1rem;'>●</span> " + settings.openai_model if live else "<span style='color:#8b5cf6;font-size:1rem;'>●</span> Demo-Ready (Offline)"}
            </div>
        </div>
        <div class="sidebar-card">
            <div class="sidebar-card-label">System Mode</div>
            <div class="sidebar-card-value">
                {"<span style='color:#0284c7;font-size:1rem;'>●</span> Live Pipeline" if live else "<span style='color:#d97706;font-size:1rem;'>●</span> Demo / Sandbox"}
            </div>
        </div>
        <div class="sidebar-card">
            <div class="sidebar-card-label">Autonomous Agent</div>
            <div class="sidebar-card-value">
                {"<span style='color:#10b981;font-size:1rem;'>●</span> Active" if auto_active else "<span style='color:#64748b;font-size:1rem;'>●</span> Standby / Manual"}
            </div>
        </div>
        <div style="font-size:0.74rem; color:#94a3b8; font-weight:600; text-align:center; margin-top:12px;">
            SalesPilot AI Engine v{settings.app_version}
        </div>
        """,
        unsafe_allow_html=True,
    )

try:
    page = st.session_state.page
    if page == "Overview":
        dashboard.render(repo)
    elif page == "Discovery":
        discovery.render(repo, force_demo=settings.force_demo_mode)
    elif page == "Leads":
        leads.render(repo)
    elif page == "Lead Detail":
        lead_detail.render(repo, demo_mode=not settings.live_ai_available)
    elif page == "Outreach":
        outreach.render(repo, demo_mode=not settings.live_ai_available)
    elif page == "Follow-Ups":
        followups.render(repo)
    elif page == "Pipeline Runs":
        pipeline_runs.render(repo)
    elif page == "ICP Configuration":
        icp.render(repo)
    elif page == "Settings":
        settings_page.render(repo)
finally:
    session.close()
