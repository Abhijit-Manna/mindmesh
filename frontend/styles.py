"""
MindMesh Frontend - Global CSS Styling (Pure Light Mode Design System)
"""

__all__ = ["get_custom_css", "CUSTOM_CSS"]


LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ─── Global Light Theme Tokens ─── */
:root {
    --bg-primary: #f8fafc;
    --bg-surface: #ffffff;
    --bg-card: #ffffff;
    --border-color: #e2e8f0;
    --border-hover: #cbd5e1;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --accent-black: #18181b;
    --accent-black-hover: #27272a;
    --accent-emerald: #059669;
}

/* App Background & Base Typography */
.stApp {
    background: #f8fafc !important;
    color: #0f172a !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

/* ─── Sidebar Pure Light Styling ─── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #0f172a !important;
}

section[data-testid="stSidebar"] .stCaption p {
    color: #64748b !important;
}

/* Sidebar History Card — Completely Light, No Dark Hover */
.sidebar-history-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px;
    padding: 11px 13px;
    margin-bottom: 8px;
    transition: border-color 0.15s ease, background-color 0.15s ease;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.sidebar-history-card:hover {
    border-color: #cbd5e1 !important;
    background: #f8fafc !important;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04) !important;
    transform: none !important;
}

.history-title {
    font-size: 0.86rem;
    font-weight: 600;
    color: #0f172a !important;
    line-height: 1.35;
    margin-bottom: 4px;
}

.history-meta {
    font-size: 0.74rem;
    color: #64748b !important;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}

.history-tag {
    color: #0f172a !important;
    font-weight: 600;
    font-size: 0.72rem;
    background: #f1f5f9 !important;
    padding: 2px 7px;
    border-radius: 9999px;
    border: 1px solid #e2e8f0 !important;
}

/* Sidebar Action Buttons */
section[data-testid="stSidebar"] div[data-testid="stButton"] button {
    font-weight: 500 !important;
    font-size: 0.80rem !important;
    padding: 5px 8px !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease !important;
    transform: none !important;
}

/* Sidebar Open Button (Primary) — Solid Black, Crisp White Text */
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"],
section[data-testid="stSidebar"] div[data-testid="stButton"] button[data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] div[data-testid="column"]:first-child div[data-testid="stButton"] button {
    background: #18181b !important;
    border: 1px solid #18181b !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.15) !important;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] p,
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] span,
section[data-testid="stSidebar"] div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] p,
section[data-testid="stSidebar"] div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] span,
section[data-testid="stSidebar"] div[data-testid="column"]:first-child div[data-testid="stButton"] button p,
section[data-testid="stSidebar"] div[data-testid="column"]:first-child div[data-testid="stButton"] button span {
    color: #ffffff !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"]:hover,
section[data-testid="stSidebar"] div[data-testid="stButton"] button[data-testid="stBaseButton-primary"]:hover,
section[data-testid="stSidebar"] div[data-testid="column"]:first-child div[data-testid="stButton"] button:hover {
    background: #27272a !important;
    border-color: #27272a !important;
    color: #ffffff !important;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25) !important;
}

/* Sidebar Delete Button (Secondary) — Clean Light */
section[data-testid="stSidebar"] div[data-testid="column"]:last-child div[data-testid="stButton"] button,
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"],
section[data-testid="stSidebar"] div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"] {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #475569 !important;
}

section[data-testid="stSidebar"] div[data-testid="column"]:last-child div[data-testid="stButton"] button:hover,
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"]:hover,
section[data-testid="stSidebar"] div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"]:hover {
    background: #f1f5f9 !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
    box-shadow: none !important;
}

/* ─── Main Container ─── */
.main .block-container {
    max-width: 760px;
    padding-top: 36px;
    padding-bottom: 60px;
    padding-left: 2rem;
    padding-right: 2rem;
    margin: 0 auto;
}

/* ─── Hero Section ─── */
.hero-section {
    padding: 24px 0 20px 0;
    margin-bottom: 24px;
}

.hero-eyebrow {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #64748b !important;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.hero-title {
    font-family: 'Newsreader', Georgia, 'Times New Roman', serif !important;
    font-size: 3.1rem !important;
    font-weight: 500 !important;
    color: #0f172a !important;
    line-height: 1.1 !important;
    letter-spacing: -0.025em !important;
    margin: 0 0 14px 0 !important;
}

.hero-subtitle {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-size: 1.02rem !important;
    color: #475569 !important;
    line-height: 1.6 !important;
    margin: 0 0 18px 0 !important;
    max-width: 620px;
    font-weight: 400;
}

.hero-actions {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-top: 18px;
}

/* Hero CTA Button — Solid Black, No Blue */
.hero-cta-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 9px 22px;
    background: #18181b !important;
    color: #ffffff !important;
    border-radius: 9999px;
    font-family: 'Inter', sans-serif;
    font-size: 0.90rem;
    font-weight: 600;
    text-decoration: none !important;
    border: none;
    cursor: pointer;
    transition: background-color 0.15s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.hero-cta-btn:hover {
    background: #27272a !important;
    color: #ffffff !important;
    transform: none !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.hero-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
    color: #64748b !important;
}

/* ─── Preset Quick-Fill Buttons ─── */
div[data-testid="stHorizontalBlock"] button {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #1e293b !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    padding: 8px 12px !important;
    transition: background-color 0.15s ease, border-color 0.15s ease !important;
    box-shadow: none !important;
    transform: none !important;
}

div[data-testid="stHorizontalBlock"] button:hover {
    background: #f8fafc !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ─── Form Container & Inputs ─── */
div[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 24px !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04) !important;
}

div[data-testid="stForm"] label,
div[data-testid="stForm"] p,
div[data-testid="stForm"] span {
    color: #0f172a !important;
}

div[data-testid="stForm"] input,
div[data-testid="stForm"] textarea,
div[data-testid="stForm"] div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border-color: #cbd5e1 !important;
    border-radius: 6px !important;
}

div[data-testid="stForm"] input:focus,
div[data-testid="stForm"] textarea:focus {
    border-color: #0f172a !important;
    box-shadow: 0 0 0 1px #0f172a !important;
}

/* Dropdown Menu Popover */
ul[data-baseweb="menu"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

li[data-baseweb="menu-item"] {
    background-color: #ffffff !important;
    color: #0f172a !important;
}

li[data-baseweb="menu-item"]:hover {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
}

/* ─── Button Spinner Animation ─── */
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Form Submit Button & All Primary Buttons — Solid Black, Crisp White Text */
[data-testid="stFormSubmitButton"] button,
button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: #18181b !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 11px 22px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
    transition: background-color 0.15s ease !important;
    transform: none !important;
    position: relative !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

[data-testid="stFormSubmitButton"] button p,
[data-testid="stFormSubmitButton"] button span,
[data-testid="stFormSubmitButton"] button div,
button[kind="primary"] p,
button[kind="primary"] span,
button[kind="primary"] div {
    color: #ffffff !important;
    font-weight: 600 !important;
}

[data-testid="stFormSubmitButton"] button:hover,
button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    background: #27272a !important;
    color: #ffffff !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    transform: none !important;
}

[data-testid="stFormSubmitButton"] button:active,
button[kind="primary"]:active {
    background: #09090b !important;
    color: #ffffff !important;
}

/* Instant CSS spinner inside button on click / active */
[data-testid="stFormSubmitButton"] button:active::before {
    content: "" !important;
    display: inline-block !important;
    width: 14px !important;
    height: 14px !important;
    margin-right: 10px !important;
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    border-top-color: #ffffff !important;
    border-radius: 50% !important;
    animation: spin 0.6s linear infinite !important;
    vertical-align: middle !important;
}

/* ─── Professional Loading States & Spinners ─── */
[data-testid="stSpinner"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 12px !important;
    padding: 16px 22px !important;
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04) !important;
    margin: 18px 0 !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.90rem !important;
    font-weight: 500 !important;
}

[data-testid="stSpinner"] > div {
    border-color: #0f172a transparent transparent transparent !important;
    width: 18px !important;
    height: 18px !important;
    border-width: 2px !important;
}

[data-testid="stStatusWidget"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    color: #0f172a !important;
}

/* ─── Agent Execution Cards (Completely Light, Hover Removed) ─── */
.agent-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    min-height: 80px;
    color: #0f172a !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    transition: none !important;
    cursor: default !important;
}

.agent-card b {
    color: #0f172a !important;
}

.agent-card.active {
    border-color: #0f172a !important;
    background: #f8fafc !important;
    box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.08) !important;
}

.agent-card.completed {
    border-color: #059669 !important;
    background: #ecfdf5 !important;
}

/* Explicitly Remove All Hover Effects on Agent Cards */
.agent-card:hover,
.agent-card.active:hover,
.agent-card.completed:hover {
    transform: none !important;
    box-shadow: none !important;
    cursor: default !important;
}
.agent-card.active:hover {
    box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.08) !important;
}

/* Terminal Log Viewport */
.terminal-window {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 0.82rem;
    color: #1e293b !important;
    height: 220px;
    overflow-y: auto;
    margin-top: 14px;
}

.terminal-line {
    margin-bottom: 5px;
    line-height: 1.5;
}

.terminal-time {
    color: #64748b !important;
    margin-right: 8px;
    font-weight: 500;
}

/* Insight Callout Box */
.insight-box {
    background: #f8fafc !important;
    border-left: 3px solid #0f172a !important;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 14px 0;
    font-size: 0.88rem;
    color: #1e293b !important;
}

/* ─── Dashboard View Tabs: Hover Effect Completely Removed, No Red ─── */
div[data-testid="stTabs"] {
    border-bottom: 1px solid #e2e8f0 !important;
}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px !important;
    border-bottom: 1px solid #e2e8f0 !important;
}

/* Base Tab Style */
div[data-testid="stTabs"] button[role="tab"],
div[data-testid="stTabs"] [data-baseweb="tab"] {
    color: #64748b !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.90rem !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
    padding: 10px 16px !important;
    transition: none !important;
    box-shadow: none !important;
    outline: none !important;
}

div[data-testid="stTabs"] button[role="tab"] p,
div[data-testid="stTabs"] button[role="tab"] span,
div[data-testid="stTabs"] button[role="tab"] div,
div[data-testid="stTabs"] [data-baseweb="tab"] p,
div[data-testid="stTabs"] [data-baseweb="tab"] span {
    color: #64748b !important;
    font-weight: 500 !important;
    transition: none !important;
}

/* REMOVE ALL HOVER EFFECTS FROM ALL TABS (No Red, No Change) */
div[data-testid="stTabs"] button[role="tab"]:hover,
div[data-testid="stTabs"] [data-baseweb="tab"]:hover,
div[data-testid="stTabs"] button[role="tab"]:focus,
div[data-testid="stTabs"] [data-baseweb="tab"]:focus {
    color: #64748b !important;
    background: transparent !important;
    border-bottom-color: transparent !important;
    box-shadow: none !important;
    transform: none !important;
}

div[data-testid="stTabs"] button[role="tab"]:hover p,
div[data-testid="stTabs"] button[role="tab"]:hover span,
div[data-testid="stTabs"] button[role="tab"]:hover div,
div[data-testid="stTabs"] [data-baseweb="tab"]:hover p,
div[data-testid="stTabs"] [data-baseweb="tab"]:hover span,
div[data-testid="stTabs"] button[role="tab"]:focus p,
div[data-testid="stTabs"] button[role="tab"]:focus span,
div[data-testid="stTabs"] [data-baseweb="tab"]:focus p,
div[data-testid="stTabs"] [data-baseweb="tab"]:focus span {
    color: #64748b !important;
}

/* Active / Selected Tab — Crisp Black, No Red */
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    color: #0f172a !important;
    border-bottom: 2px solid #0f172a !important;
    font-weight: 600 !important;
    background: transparent !important;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p,
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] span,
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] div,
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] p,
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] span {
    color: #0f172a !important;
    font-weight: 600 !important;
}

/* Selected Tab on Hover — Stays Solid Black, Never Red */
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]:hover,
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"]:hover {
    color: #0f172a !important;
    border-bottom: 2px solid #0f172a !important;
    background: transparent !important;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]:hover p,
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]:hover span,
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"]:hover p,
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"]:hover span {
    color: #0f172a !important;
}

/* BaseWeb Highlight Line & Borders — Never Red */
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: #0f172a !important;
}

div[data-testid="stTabs"] [data-baseweb="tab-border"] {
    background-color: #e2e8f0 !important;
}

/* Action & Download Buttons */
div[data-testid="stDownloadButton"] button {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: background-color 0.15s ease, border-color 0.15s ease !important;
    transform: none !important;
    box-shadow: none !important;
}

div[data-testid="stDownloadButton"] button:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
    transform: none !important;
    box-shadow: none !important;
}

div[data-testid="stColumn"] div[data-testid="stButton"] button {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: background-color 0.15s ease, border-color 0.15s ease !important;
    transform: none !important;
    box-shadow: none !important;
}

div[data-testid="stColumn"] div[data-testid="stButton"] button:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Tables in Light Mode */
.main table {
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    background: #ffffff;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}

.main th {
    background: #f8fafc;
    color: #0f172a;
    font-weight: 600;
    text-align: left;
    padding: 10px 14px;
    border: 1px solid #e2e8f0;
}

.main td {
    padding: 10px 14px;
    border: 1px solid #e2e8f0;
    color: #334155;
}

.main tr:nth-child(even) td {
    background: #f8fafc;
}

.main tr:hover td {
    background: #f1f5f9;
}

/* Code & Pre in Light Mode */
.main code {
    background: #f1f5f9 !important;
    color: #0f172a !important;
    padding: 2px 6px;
    border-radius: 4px;
}

.main pre {
    background: #f8fafc !important;
    color: #0f172a !important;
    padding: 16px;
    border-radius: 8px;
    border: 1px solid #e2e8f0 !important;
}

.main pre code {
    background: transparent !important;
    color: inherit !important;
}

.main blockquote {
    background: #f8fafc !important;
    border-left: 3px solid #0f172a !important;
    border-radius: 6px;
    padding: 12px 18px !important;
    margin: 16px 0 !important;
    color: #334155 !important;
}

.main hr {
    border: none !important;
    border-top: 1px solid #e2e8f0 !important;
    margin: 28px 0 !important;
}
</style>
"""


def get_custom_css(theme: str = "Light") -> str:
    """Return pure light mode CSS stylesheet."""
    return LIGHT_CSS


# Default stylesheet export
CUSTOM_CSS = LIGHT_CSS
