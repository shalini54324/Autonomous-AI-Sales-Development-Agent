from __future__ import annotations
import json
import streamlit as st

def title_block(title: str, subtitle: str, badge_text: str = "AI SALES INTELLIGENCE") -> None:
    st.markdown(
        f'''
        <div class="header-banner">
            <div class="header-banner-badge">✦ {badge_text}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        ''',
        unsafe_allow_html=True,
    )

def badge(classification: str) -> str:
    cls_map = {
        "HOT": "hot",
        "HIGH PRIORITY": "high",
        "WARM": "warm",
        "LOW": "low"
    }
    cls = cls_map.get(classification.upper() if classification else "", "low")
    return f'<span class="pill {cls}">{classification}</span>'

def status_pill(status: str) -> str:
    s = (status or "").lower()
    if s in {"ready", "completed", "success"}:
        cls = "ready"
    elif s in {"sent"}:
        cls = "sent"
    elif s in {"review", "partial", "needs review"}:
        cls = "review"
    elif s in {"failed"}:
        cls = "hot"
    else:
        cls = "low"
    return f'<span class="pill {cls}">{status}</span>'

def render_kpis(items: list) -> None:
    """
    Renders distinct colored KPI cards.
    Items can be:
    - (label, value, hint)
    - (label, value, hint, accent, icon)
    """
    defaults = [
        ("sky", "🏢"),
        ("teal", "🎯"),
        ("coral", "🔥"),
        ("violet", "✉️"),
    ]
    
    html = ['<div class="kpi-container">']
    for idx, item in enumerate(items):
        label = item[0]
        value = item[1]
        hint = item[2]
        accent = item[3] if len(item) > 3 else defaults[idx % len(defaults)][0]
        icon = item[4] if len(item) > 4 else defaults[idx % len(defaults)][1]
        
        card_html = f'''
        <div class="kpi-card kpi-{accent}">
            <div class="kpi-top-row">
                <span class="kpi-title">{label}</span>
                <span class="kpi-icon-pill">{icon}</span>
            </div>
            <div class="kpi-val">{value}</div>
            <div class="kpi-footer">{hint}</div>
        </div>
        '''
        html.append(card_html)
    html.append('</div>')
    st.markdown("".join(html), unsafe_allow_html=True)

def render_pipeline_stages(stages: list[tuple[str, int, str]]) -> None:
    """
    Renders a visual multi-stage pipeline.
    stages format: [("Stage Name", count, icon), ...]
    """
    html = [
        '<div class="pipeline-card">',
        '  <div class="pipeline-header">',
        '    <span class="pipeline-title">⚡ Autonomous Pipeline Progression</span>',
        '    <span class="header-banner-badge">Real-Time Funnel</span>',
        '  </div>',
        '  <div class="pipeline-flow">'
    ]
    for idx, item in enumerate(stages):
        name = item[0]
        count = item[1]
        icon = item[2] if len(item) > 2 else "•"
        active_cls = " pipeline-step-active" if count > 0 else ""
        step_html = f'''
        <div class="pipeline-step{active_cls}">
            <div class="pipeline-step-top">
                <span class="pipeline-step-num">STAGE 0{idx+1}</span>
                <span>{icon}</span>
            </div>
            <div class="pipeline-step-count">{count}</div>
            <div class="pipeline-step-name">{name}</div>
        </div>
        '''
        html.append(step_html)
        if idx < len(stages) - 1:
            html.append('<div class="pipeline-arrow">→</div>')
    html.append('  </div>')
    html.append('</div>')
    st.markdown("".join(html), unsafe_allow_html=True)

def parse_json(text: str, default):
    try:
        return json.loads(text)
    except Exception:
        return default
