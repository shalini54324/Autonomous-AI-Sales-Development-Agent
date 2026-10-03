from __future__ import annotations
import re
import streamlit as st
from app.ui.components import title_block
from app.utils.parsers import parse_manual_companies, parse_csv_bytes
from app.schemas.company import DiscoveryCriteria
from app.services.discovery_service import DiscoveryService
from app.pipeline.orchestrator import PipelineOrchestrator
from app.config import settings

PIPELINE_STAGES = {
    "Researching company…": 1,
    "Finding decision makers…": 2,
    "Analyzing business needs…": 3,
    "Calculating lead score…": 4,
    "Saving intelligence…": 5,
    "Generating autonomous outreach…": 5.4,
    "Scheduling follow-up intelligence…": 5.7,
    "Complete": 6,
    "Failed / Partial": 6,
}


def _run(repo, companies, demo, autonomous, auto_classes):
    icp = repo.get_icp()
    if not icp:
        st.error("Configure and save an Ideal Customer Profile (ICP) before running the pipeline.")
        return
    if not companies:
        st.warning("Please select or add at least one company to process.")
        return

    companies = companies[: settings.max_companies_per_run]
    bar = st.progress(0, text="Initializing sales intelligence pipeline…")
    status = st.empty()

    def prog(i, total, name, stage="Processing…"):
        stage_value = PIPELINE_STAGES.get(stage, 1)
        fraction = min(1.0, ((i - 1) + stage_value / 6) / max(1, total))
        bar.progress(fraction, text=f"Processing {i} of {total}: {name} — {stage}")
        status.caption(f"Current stage: {stage}")

    result = PipelineOrchestrator(repo).process_batch(
        companies,
        icp,
        demo=demo,
        autonomous=autonomous,
        auto_classes=set(auto_classes),
        progress=prog,
    )
    bar.progress(1.0, text="Pipeline processing complete")
    if result["failed"]:
        st.warning(
            f"Execution finished with partial outcomes: {result['successful']} succeeded, "
            f"{result['failed']} encountered issues. Detailed reasons are logged in the lead records."
        )
    else:
        st.success(f"Pipeline complete: {result['successful']} companies analyzed and qualified.")


def _pick_key(i: int, name: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    return f"disc_pick_{i}_{safe}"


def _reset_discovery_selection(found, value=True):
    for i, c in enumerate(found):
        st.session_state[_pick_key(i, c.company_name)] = value


def render(repo, force_demo=False):
    title_block(
        "Prospect Discovery Engine",
        "Source accounts via AI discovery, bulk CSV import, manual entry, or sample demo profiles. All sources flow into the central intelligence pipeline.",
        badge_text="LEAD DISCOVERY",
    )

    # Autonomous Mode Configuration Bar
    st.markdown(
        '''
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px 18px; margin-bottom:18px; box-shadow:0 1px 3px rgba(15,23,42,0.04);">
            <div style="font-size:0.85rem; font-weight:750; color:#0f172a; margin-bottom:6px;">
                ⚙️ Autonomous Pipeline Settings
            </div>
            <div style="font-size:0.80rem; color:#64748b; margin-bottom:10px;">
                When active, the AI automatically drafts personalized outreach emails and follow-up schedules for high-scoring prospects without manual review.
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    
    cfg_col1, cfg_col2 = st.columns([1, 2])
    with cfg_col1:
        auto = st.toggle(
            "Enable Autonomous Mode",
            value=st.session_state.get("autonomous_active", False),
            help="Automatically triggers outreach and follow-up generation for qualified priorities.",
        )
        st.session_state["autonomous_active"] = auto
    with cfg_col2:
        auto_classes = st.multiselect(
            "Auto-process tiers",
            ["HOT", "HIGH PRIORITY", "WARM", "LOW"],
            default=["HOT", "HIGH PRIORITY"],
            disabled=not auto,
            help="Select which lead tiers trigger automated outreach drafting.",
        )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI Discovery", "✍️ Manual Entry", "📁 CSV Upload", "🧪 Demo Mode"])

    # TAB 1: AI Discovery
    with tab1:
        icp = repo.get_icp()
        st.markdown(
            '<div style="font-size:0.92rem; font-weight:700; color:#0f172a; margin-bottom:12px;">'
            'Target Discovery Parameters</div>',
            unsafe_allow_html=True,
        )
        c1, c2, c3, c4 = st.columns([1.5, 1.5, 2, 1.2])
        industry = c1.text_input(
            "Target Industry", value=icp.target_industry if icp else "SaaS", key="disc_ind"
        )
        location = c2.text_input(
            "Location / Region", value=icp.target_location if icp else "Global", key="disc_loc"
        )
        with c3:
            s_col1, s_col2 = st.columns(2)
            min_e = s_col1.number_input(
                "Min Employees", 1, 100000, value=icp.min_employees if icp else 50, key="disc_min"
            )
            max_e = s_col2.number_input(
                "Max Employees", 1, 100000, value=icp.max_employees if icp else 500, key="disc_max"
            )
        count = c4.number_input("Count", 1, 25, value=5, key="disc_count")

        if st.button("🔍 Discover Candidates", type="primary", key="btn_disc_candidates"):
            try:
                criteria = DiscoveryCriteria(
                    industry=industry,
                    location=location,
                    min_employees=int(min_e),
                    max_employees=int(max_e),
                    count=int(count),
                )
                service = DiscoveryService()
                use_demo = force_demo or not service.ai.available
                found = (
                    service.discover_demo(criteria)
                    if use_demo
                    else service.discover_live(criteria)
                )
                st.session_state.discovered = found
                st.session_state.discovered_demo = use_demo
                _reset_discovery_selection(found, True)
                st.success(f"Discovered {len(found)} candidate prospects matching your criteria.")
            except Exception as e:
                st.error(f"Discovery error: {e}")

        found = st.session_state.get("discovered", [])
        if found:
            st.markdown("<hr style='border:0; border-top:1px solid #e2e8f0; margin:16px 0;'>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:0.95rem; font-weight:750; color:#0f172a; margin-bottom:4px;">'
                'Discovered Candidates</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Review and select prospects below to send into the research and scoring pipeline."
            )
            a, b, _ = st.columns([1, 1, 4])
            if a.button("Select All", key="disc_select_all"):
                _reset_discovery_selection(found, True)
                st.rerun()
            if b.button("Deselect All", key="disc_deselect_all"):
                _reset_discovery_selection(found, False)
                st.rerun()

            selected = []
            for i, c in enumerate(found):
                key = _pick_key(i, c.company_name)
                if key not in st.session_state:
                    st.session_state[key] = True
                
                cols = st.columns([0.06, 0.32, 0.24, 0.18, 0.20])
                pick = cols[0].checkbox("", key=key, label_visibility="collapsed")
                cols[1].markdown(f"**{c.company_name}**")
                cols[2].caption(f"🌐 {c.website or 'Website unavailable'}")
                cols[3].caption(f"📍 {c.location or 'Location unknown'}")
                cols[4].caption(f"ℹ️ {c.source_note or 'AI Generated'}")
                if pick:
                    selected.append(c)

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            run_col1, run_col2 = st.columns([1.5, 3])
            with run_col1:
                if st.button(f"⚡ Run Pipeline for {len(selected)} Selected", type="primary", key="run_disc", disabled=len(selected)==0):
                    _run(
                        repo,
                        selected,
                        bool(st.session_state.get("discovered_demo")),
                        auto,
                        auto_classes,
                    )

    # TAB 2: Manual Entry
    with tab2:
        st.markdown(
            '<div style="font-size:0.92rem; font-weight:700; color:#0f172a; margin-bottom:8px;">'
            'Direct Prospect Input</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Paste comma-separated entries (`Company, URL`) or structured company profile blocks."
        )
        text = st.text_area(
            "Paste Company Data",
            height=200,
            placeholder=(
                "HubSpot, https://www.hubspot.com\n\n"
                "Company Name: Snowflake\nWebsite: https://www.snowflake.com\n"
                "Industry: Data & Cloud\nLocation: USA\nEmployees: 6000"
            ),
        )
        companies, errors = parse_manual_companies(text)
        if text:
            st.markdown("**Parsed Candidates Preview:**")
            st.dataframe(
                [c.model_dump() for c in companies],
                use_container_width=True,
                hide_index=True,
            )
            for e in errors:
                st.warning(f"Formatting note: {e}")
        
        if st.button("⚡ Run Pipeline on Manual Entries", type="primary", disabled=not companies):
            _run(
                repo,
                companies,
                force_demo or not settings.live_ai_available,
                auto,
                auto_classes,
            )

    # TAB 3: CSV Upload
    with tab3:
        st.markdown(
            '<div style="font-size:0.92rem; font-weight:700; color:#0f172a; margin-bottom:8px;">'
            'Bulk CSV Prospect Ingestion</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "CSV should contain columns: `company_name`, `website`, and optionally `industry`, `location`, `employee_count`."
        )
        up = st.file_uploader("Choose CSV File", type=["csv"])
        companies = []
        if up:
            companies, errors = parse_csv_bytes(up.getvalue())
            st.markdown(f"**Parsed {len(companies)} valid prospects from CSV:**")
            st.dataframe(
                [c.model_dump() for c in companies],
                use_container_width=True,
                hide_index=True,
            )
            for e in errors:
                st.warning(e)
        if st.button("⚡ Ingest & Process CSV Prospects", type="primary", disabled=not companies):
            _run(
                repo,
                companies,
                force_demo or not settings.live_ai_available,
                auto,
                auto_classes,
            )

    # TAB 4: Demo Mode
    with tab4:
        st.markdown(
            '''
            <div style="background:#f5f3ff; border:1px solid #ddd6fe; border-radius:12px; padding:16px 20px; margin-bottom:16px;">
                <div style="font-size:0.95rem; font-weight:800; color:#5b21b6; margin-bottom:4px;">
                    🧪 Demo Mode Sandbox
                </div>
                <div style="font-size:0.85rem; color:#4c1d95; line-height:1.5;">
                    Demo Mode loads a curated set of fictional B2B companies containing diverse firmographics and fit levels. 
                    This enables testing the end-to-end intelligence engine, scoring algorithms, and autonomous outreach generation without consuming live search or OpenAI credits.
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        if st.button("🚀 Load & Run 5 Demo Prospects", type="primary"):
            icp = repo.get_icp()
            if not icp:
                st.error("Please configure and save an ICP in ICP Configuration before running.")
            else:
                criteria = DiscoveryCriteria(
                    industry=icp.target_industry,
                    location=icp.target_location,
                    min_employees=icp.min_employees,
                    max_employees=icp.max_employees,
                    count=5,
                )
                _run(repo, DiscoveryService().discover_demo(criteria), True, auto, auto_classes)
