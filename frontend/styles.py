"""
MindMesh Frontend - Global CSS Styling & Visual Theme (Light Mode)
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..700&display=swap');

/* Global Light Design System */
:root {
    --bg-primary: #f8fafc;
    --bg-card: #ffffff;
    --accent-indigo: #6366f1;
    --accent-violet: #7c3aed;
    --accent-cyan: #0891b2;
    --accent-emerald: #059669;
    --border-color: rgba(99, 102, 241, 0.15);
    --text-primary: #1e293b;
    --text-secondary: #64748b;
}

/* Global App Background */
.stApp {
    background: #f8fafc !important;
    font-family: 'Inter', sans-serif;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

section[data-testid="stSidebar"] * {
    color: #1e293b !important;
}

section[data-testid="stSidebar"] .stCaption p {
    color: #64748b !important;
}

.sidebar-history-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    transition: all 0.15s ease;
}

.sidebar-history-card:hover {
    border-color: rgba(99, 102, 241, 0.35);
    background: #f5f3ff;
}

.history-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #1e293b;
    line-height: 1.35;
    margin-bottom: 4px;
}

.history-meta {
    font-size: 0.74rem;
    color: #64748b;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

/* Main Container — narrower & focused */
.main .block-container {
    max-width: 720px;
    padding-top: 40px;
    padding-bottom: 60px;
    padding-left: 2rem;
    padding-right: 2rem;
    margin: 0 auto;
}

/* ── Ideogram-Style Hero Section ── */
.hero-section {
    padding: 28px 0 24px 0;
    margin-bottom: 24px;
}

.hero-eyebrow {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #64748b;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.hero-title {
    font-family: 'Newsreader', Georgia, 'Times New Roman', serif !important;
    font-size: 3.3rem !important;
    font-weight: 500 !important;
    color: #111827 !important;
    line-height: 1.08 !important;
    letter-spacing: -0.025em !important;
    margin: 0 0 16px 0 !important;
}

.hero-subtitle {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-size: 1.05rem !important;
    color: #475569 !important;
    line-height: 1.62 !important;
    margin: 0 0 18px 0 !important;
    max-width: 600px;
    font-weight: 400;
}

.hero-actions {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-top: 20px;
}

.hero-cta-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 10px 24px;
    background: #18181b !important;
    color: #ffffff !important;
    border-radius: 9999px;
    font-family: 'Inter', sans-serif;
    font-size: 0.92rem;
    font-weight: 600;
    text-decoration: none !important;
    border: none;
    cursor: pointer;
    transition: all 0.15s ease;
}

.hero-cta-btn:hover {
    background: #27272a !important;
    color: #ffffff !important;
    transform: translateY(-1px);
}

.hero-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
    color: #64748b;
}

/* ── Agent Execution Cards ── */
.agent-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 18px;
    transition: all 0.3s ease;
    margin-bottom: 12px;
    min-height: 85px;
    color: #1e293b;
}

.agent-card b {
    color: #1e293b;
}

.agent-card.active {
    border-color: #6366f1;
    background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, #ffffff 100%);
    box-shadow: 0 0 0 3px rgba(99,102,241,0.10), 0 4px 16px rgba(99,102,241,0.12);
    animation: pulse-border-light 1.8s infinite ease-in-out;
}

.agent-card.completed {
    border-color: #059669;
    background: linear-gradient(135deg, rgba(5,150,105,0.05) 0%, #ffffff 100%);
}

@keyframes pulse-border-light {
    0%   { box-shadow: 0 0 0 2px rgba(99,102,241,0.12), 0 4px 16px rgba(99,102,241,0.08); }
    50%  { box-shadow: 0 0 0 4px rgba(99,102,241,0.25), 0 6px 22px rgba(99,102,241,0.18); }
    100% { box-shadow: 0 0 0 2px rgba(99,102,241,0.12), 0 4px 16px rgba(99,102,241,0.08); }
}

/* Terminal Log Viewport */
.terminal-window {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px 20px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 0.84rem;
    color: #3730a3;
    height: 220px;
    overflow-y: auto;
    margin-top: 14px;
}

.terminal-line {
    margin-bottom: 6px;
    line-height: 1.5;
}

.terminal-time {
    color: #94a3b8;
    margin-right: 8px;
    font-weight: 500;
}

/* Insight Callout Box */
.insight-box {
    background: #f0f9ff;
    border-left: 3px solid #6366f1;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 14px 0;
    font-size: 0.90rem;
    color: #374151;
}

/* Form Card Wrapper — clean border, no shadow */
.form-card-wrapper {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 28px 28px 20px 28px;
    margin-top: 8px;
    position: relative;
    overflow: hidden;
}

.form-card-wrapper::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #7c3aed, #0891b2);
    border-radius: 16px 16px 0 0;
}

/* Generate Button Click Animation */
[data-testid="stFormSubmitButton"] button,
[data-testid="stFormSubmitButton"] button:focus {
    transition: all 0.18s cubic-bezier(0.4,0,0.2,1) !important;
    position: relative;
    overflow: hidden;
}

[data-testid="stFormSubmitButton"] button:active {
    transform: scale(0.97) translateY(1px) !important;
    filter: brightness(0.93);
}

[data-testid="stFormSubmitButton"] button::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center, rgba(255,255,255,0.3) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
    border-radius: inherit;
    pointer-events: none;
}

[data-testid="stFormSubmitButton"] button:active::after {
    opacity: 1;
    animation: btn-ripple 0.4s ease-out forwards;
}

@keyframes btn-ripple {
    0%   { transform: scale(0.5); opacity: 0.6; }
    100% { transform: scale(2.5); opacity: 0; }
}
</style>
"""
