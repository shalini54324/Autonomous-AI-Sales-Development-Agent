from __future__ import annotations

CSS = r'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --bg-canvas: #f8fafc;
    --bg-surface: #ffffff;
    --bg-subtle: #f1f5f9;
    --border-subtle: #e2e8f0;
    --border-strong: #cbd5e1;
    --text-primary: #0f172a;
    --text-secondary: #334155;
    --text-muted: #64748b;
    --indigo: #4f46e5;
    --indigo-subtle: #eef2ff;
    --violet: #7c3aed;
    --violet-subtle: #f5f3ff;
    --sky: #0284c7;
    --sky-subtle: #e0f2fe;
    --teal: #0d9488;
    --teal-subtle: #ccfbf1;
    --coral: #f43f5e;
    --coral-subtle: #ffe4e6;
    --amber: #d97706;
    --amber-subtle: #fef3c7;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.05);
    --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.05);
    --shadow-lg: 0 8px 24px rgba(15, 23, 42, 0.06);
}

/* Global resets & typography */
html, body, [class*="css"] {
    font-family: var(--font-sans);
    color: var(--text-primary) !important;
}

.stApp {
    background-color: var(--bg-canvas) !important;
    color: var(--text-primary) !important;
}

/* Clean up Streamlit chrome */
#MainMenu, footer, header {
    visibility: hidden;
    height: 0;
}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1480px !important;
}

/* Sidebar Styling & High-Contrast Fix */
[data-testid="stSidebar"] {
    background-color: #f4f6fa !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary);
}

[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown h2 {
    color: var(--text-primary) !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}

[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] p {
    color: var(--text-secondary) !important;
}

/* Sidebar Radio Navigation */
[data-testid="stSidebar"] [data-testid="stRadio"] {
    background: transparent;
    padding: 0;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 4px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: transparent;
    border-radius: var(--radius-md);
    padding: 8px 12px !important;
    margin: 2px 0;
    transition: all 0.15s ease-in-out;
    cursor: pointer;
    border: 1px solid transparent;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #e9ecf3 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #eef2ff !important;
    border: 1px solid #c7d2fe !important;
    border-left: 4px solid var(--indigo) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p,
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
    color: var(--indigo) !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    color: var(--text-primary) !important;
    font-size: 0.90rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

/* Sidebar Status Cards */
.sidebar-card {
    background: #ffffff;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 12px 14px;
    margin: 10px 0;
    box-shadow: var(--shadow-sm);
}

.sidebar-card-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    margin-bottom: 4px;
}

.sidebar-card-value {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Compact Header Banner */
.header-banner {
    background: linear-gradient(135deg, #ffffff 0%, #f8faff 60%, #f5f3ff 100%);
    border: 1px solid #e0e7ff;
    border-radius: var(--radius-lg);
    padding: 18px 24px;
    margin-bottom: 22px;
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.header-banner-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    background: #eef2ff;
    color: var(--indigo);
    border: 1px solid #c7d2fe;
    width: fit-content;
}

.header-banner h1 {
    font-size: 1.55rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    margin: 4px 0 2px 0 !important;
    letter-spacing: -0.025em;
}

.header-banner p {
    font-size: 0.90rem !important;
    color: var(--text-secondary) !important;
    margin: 0 !important;
}

/* Distinct KPI Cards */
.kpi-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 16px 18px;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
}

.kpi-sky::before { background: var(--sky); }
.kpi-teal::before { background: var(--teal); }
.kpi-coral::before { background: var(--coral); }
.kpi-violet::before { background: var(--violet); }

.kpi-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}

.kpi-title {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-muted);
}

.kpi-icon-pill {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}

.kpi-sky .kpi-icon-pill { background: var(--sky-subtle); color: var(--sky); }
.kpi-teal .kpi-icon-pill { background: var(--teal-subtle); color: var(--teal); }
.kpi-coral .kpi-icon-pill { background: var(--coral-subtle); color: var(--coral); }
.kpi-violet .kpi-icon-pill { background: var(--violet-subtle); color: var(--violet); }

.kpi-val {
    font-size: 2.1rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.1;
    margin-bottom: 6px;
    letter-spacing: -0.02em;
}

.kpi-footer {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-secondary);
}

/* Multi-stage Visual Pipeline */
.pipeline-card {
    background: #ffffff;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 18px 22px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-sm);
}

.pipeline-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}

.pipeline-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-primary);
}

.pipeline-flow {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
}

.pipeline-step {
    flex: 1;
    background: #f8faff;
    border: 1px solid #e0e7ff;
    border-radius: var(--radius-md);
    padding: 10px 14px;
    position: relative;
    transition: all 0.15s ease;
}

.pipeline-step:hover {
    border-color: #c7d2fe;
    background: #eef2ff;
}

.pipeline-step-active {
    background: #ffffff;
    border: 1.5px solid var(--indigo);
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.1);
}

.pipeline-step-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
}

.pipeline-step-num {
    font-size: 0.72rem;
    font-weight: 800;
    color: var(--text-muted);
}

.pipeline-step-count {
    font-size: 1.1rem;
    font-weight: 800;
    color: var(--text-primary);
}

.pipeline-step-name {
    font-size: 0.80rem;
    font-weight: 700;
    color: var(--text-secondary);
}

.pipeline-arrow {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 700;
    flex-shrink: 0;
}

/* General Cards & Containers */
.card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 18px 20px;
    margin: 8px 0 16px;
    box-shadow: var(--shadow-sm);
}

.card-compact {
    padding: 14px 16px;
}

/* Badges & Pills */
.pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 750;
    letter-spacing: 0.02em;
    border: 1px solid transparent;
}

.pill.hot {
    background: #ffe4e6;
    color: #e11d48;
    border-color: #fecdd3;
}

.pill.high {
    background: #fef3c7;
    color: #b45309;
    border-color: #fde68a;
}

.pill.warm {
    background: #f3e8ff;
    color: #7c3aed;
    border-color: #e9d5ff;
}

.pill.low {
    background: #f1f5f9;
    color: #475467;
    border-color: #e2e8f0;
}

.pill.ready {
    background: #ecfdf5;
    color: #047857;
    border-color: #a7f3d0;
}

.pill.sent {
    background: #e0f2fe;
    color: #0369a1;
    border-color: #bae6fd;
}

.pill.review {
    background: #fff7ed;
    color: #c2410c;
    border-color: #ffedd5;
}

.pill.ai {
    background: #eef2ff;
    color: var(--indigo);
    border-color: #c7d2fe;
}

/* Activity Timeline Step */
.activity-step {
    border-left: 3px solid var(--indigo);
    padding: 8px 14px;
    margin: 8px 0;
    background: #ffffff;
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    border-top: 1px solid var(--border-subtle);
    border-right: 1px solid var(--border-subtle);
    border-bottom: 1px solid var(--border-subtle);
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}

.activity-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-primary);
}

.activity-desc {
    font-size: 0.80rem;
    color: var(--text-secondary);
    margin-top: 2px;
}

/* Buttons */
div.stButton > button {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border-strong) !important;
    color: var(--text-primary) !important;
    background: #ffffff !important;
    font-weight: 700 !important;
    min-height: 40px !important;
    transition: all 0.15s ease !important;
    box-shadow: var(--shadow-sm) !important;
}

div.stButton > button:hover {
    border-color: #94a3b8 !important;
    background: #f8fafc !important;
}

div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 2px 6px rgba(79, 70, 229, 0.3) !important;
}

div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="baseButton-primary"]:hover {
    opacity: 0.94 !important;
    box-shadow: 0 4px 10px rgba(79, 70, 229, 0.4) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background-color: transparent;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-md) var(--radius-md) 0 0;
    padding: 8px 16px;
    font-weight: 700;
    color: var(--text-muted);
}

.stTabs [aria-selected="true"] {
    color: var(--indigo) !important;
    border-bottom: 2px solid var(--indigo) !important;
    background-color: transparent;
}

/* Inputs, textareas, number inputs */
div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"] {
    border-radius: var(--radius-md) !important;
    border-color: var(--border-strong) !important;
}

input, textarea, select {
    color: var(--text-primary) !important;
}

/* Custom form card */
.form-card {
    background: #ffffff;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: var(--shadow-sm);
}

.form-card-title {
    font-size: 1rem;
    font-weight: 750;
    color: var(--text-primary);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Streamlit Dataframe custom wrapper */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}
</style>
'''
