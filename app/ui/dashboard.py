from __future__ import annotations
import json
import streamlit as st
from app.ui.components import title_block, render_kpis, render_pipeline_stages, badge, status_pill

def render(repo) -> None:
    title_block(
        "Executive Sales Intelligence",
        "Real-time pipeline performance, lead qualification quality, and autonomous SDR execution.",
        badge_text="PIPELINE OVERVIEW",
    )
    
    leads = repo.list_leads()
    outs = repo.list_outreaches()
    fups = repo.list_followups()
    runs = repo.list_runs()
    
    # 4 Distinct Accent KPI Cards
    render_kpis([
        ("Companies", len({l.company_id for l in leads}), "Researched accounts", "sky", "🏢"),
        ("Qualified", sum(l.score >= 50 for l in leads), "Score ≥ 50 / 100", "teal", "🎯"),
        ("Priority", sum(l.classification in {"HOT", "HIGH PRIORITY"} for l in leads), "HOT & HIGH Priority", "coral", "🔥"),
        ("Outreach", len(outs), "Personalized drafts", "violet", "✉️"),
    ])
    
    # Multi-Stage Visual Pipeline
    stages = [
        ("Research", len(leads), "🏢"),
        ("Qualified", sum(l.score >= 50 for l in leads), "🎯"),
        ("Priority", sum(l.classification in {"HOT", "HIGH PRIORITY"} for l in leads), "🔥"),
        ("Outreach", len(outs), "✉️"),
        ("Follow-Up", len(fups), "⏱️"),
    ]
    render_pipeline_stages(stages)
    
    # Main split layout
    col_left, col_right = st.columns([1.3, 1.0])
    
    with col_left:
        # Lead Quality Breakdown
        st.markdown(
            '<div style="font-size:1.05rem; font-weight:750; color:#0f172a; margin-bottom:8px;">'
            '📊 Lead Quality Distribution</div>',
            unsafe_allow_html=True,
        )
        total_leads = max(1, len(leads))
        hot_cnt = sum(l.classification == "HOT" for l in leads)
        high_cnt = sum(l.classification == "HIGH PRIORITY" for l in leads)
        warm_cnt = sum(l.classification == "WARM" for l in leads)
        low_cnt = sum(l.classification == "LOW" for l in leads)
        
        q_cols = st.columns(4)
        with q_cols[0]:
            st.markdown(
                f'<div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:10px; padding:10px 12px; text-align:center;">'
                f'<div style="font-size:0.75rem; font-weight:700; color:#be123c;">HOT</div>'
                f'<div style="font-size:1.4rem; font-weight:800; color:#9f1239;">{hot_cnt}</div>'
                f'<div style="font-size:0.72rem; color:#64748b;">{int(hot_cnt/total_leads*100) if leads else 0}%</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with q_cols[1]:
            st.markdown(
                f'<div style="background:#fffbeb; border:1px solid #fde68a; border-radius:10px; padding:10px 12px; text-align:center;">'
                f'<div style="font-size:0.75rem; font-weight:700; color:#b45309;">HIGH</div>'
                f'<div style="font-size:1.4rem; font-weight:800; color:#92400e;">{high_cnt}</div>'
                f'<div style="font-size:0.72rem; color:#64748b;">{int(high_cnt/total_leads*100) if leads else 0}%</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with q_cols[2]:
            st.markdown(
                f'<div style="background:#faf5ff; border:1px solid #e9d5ff; border-radius:10px; padding:10px 12px; text-align:center;">'
                f'<div style="font-size:0.75rem; font-weight:700; color:#6b21a8;">WARM</div>'
                f'<div style="font-size:1.4rem; font-weight:800; color:#581c87;">{warm_cnt}</div>'
                f'<div style="font-size:0.72rem; color:#64748b;">{int(warm_cnt/total_leads*100) if leads else 0}%</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with q_cols[3]:
            st.markdown(
                f'<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; text-align:center;">'
                f'<div style="font-size:0.75rem; font-weight:700; color:#475467;">LOW</div>'
                f'<div style="font-size:1.4rem; font-weight:800; color:#334155;">{low_cnt}</div>'
                f'<div style="font-size:0.72rem; color:#64748b;">{int(low_cnt/total_leads*100) if leads else 0}%</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        
        # Priority Leads section
        st.markdown(
            '<div style="font-size:1.05rem; font-weight:750; color:#0f172a; margin-bottom:10px;">'
            '🔥 Priority Prospect Queue</div>',
            unsafe_allow_html=True,
        )
        priority_leads = [l for l in leads if l.classification in {"HOT", "HIGH PRIORITY"}]
        if not priority_leads:
            st.info("No priority leads yet. Go to **Discovery** to run prospective companies through the AI pipeline.")
        else:
            for l in priority_leads[:5]:
                try:
                    dm = json.loads(l.decision_maker_json)
                    dm_text = f"{dm.get('name', 'Contact')} ({dm.get('role', 'Executive')})"
                except Exception:
                    dm_text = "Executive Contact"
                
                try:
                    needs = json.loads(l.needs_json)
                    need_preview = needs[0].get("need", "") if needs else ""
                except Exception:
                    need_preview = ""
                    
                st.markdown(
                    f'''
                    <div class="card card-compact" style="margin: 6px 0 10px 0;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                            <span style="font-size:0.95rem; font-weight:800; color:#0f172a;">{l.company.name}</span>
                            <div>{badge(l.classification)} &nbsp; <span style="font-weight:750; color:#4f46e5; font-size:0.88rem;">{l.score}/100</span></div>
                        </div>
                        <div style="font-size:0.80rem; color:#475467; margin-bottom:4px;">
                            <span>🏢 {l.company.industry or 'Technology'}</span> &nbsp;•&nbsp; 
                            <span>👤 {dm_text}</span>
                        </div>
                        {f'<div style="font-size:0.78rem; color:#64748b; background:#f8fafc; padding:4px 8px; border-radius:6px; border:1px solid #f1f5f9;"><b>Key Need:</b> {need_preview}</div>' if need_preview else ''}
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )
    
    with col_right:
        st.markdown(
            '<div style="font-size:1.05rem; font-weight:750; color:#0f172a; margin-bottom:10px;">'
            '⚡ Recent AI Agent Activity</div>',
            unsafe_allow_html=True,
        )
        acts = repo.list_activity(6)
        if not acts:
            st.caption("AI agent activity and audit events will appear here after pipeline execution.")
        else:
            for a in acts:
                event_name = a.event_type.replace("_", " ").title()
                st.markdown(
                    f'''
                    <div class="activity-step">
                        <div class="activity-title">{event_name}</div>
                        <div class="activity-desc">{a.message}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )

    # Recent Pipeline Runs Table
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1.05rem; font-weight:750; color:#0f172a; margin-bottom:8px;">'
        '📋 Recent Pipeline Execution History</div>',
        unsafe_allow_html=True,
    )
    if runs:
        run_data = [
            {
                "Run ID": f"#{r.id}",
                "Mode": r.mode.title(),
                "Submitted": r.companies_submitted,
                "Successful": r.companies_successful,
                "Failed": r.companies_failed,
                "Priority Leads": r.priority_leads,
                "Outreach Generated": r.outreach_generated,
                "Autonomous": "Yes" if r.autonomous else "No",
                "Started": r.started_at.strftime("%Y-%m-%d %H:%M"),
            }
            for r in runs[:8]
        ]
        st.dataframe(run_data, use_container_width=True, hide_index=True)
    else:
        st.caption("No pipeline runs recorded yet. Start discovery to trigger the autonomous workflow.")
