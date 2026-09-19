"""
MindMesh Frontend - Global CSS Styling & Visual Theme
"""

CUSTOM_CSS = """
<style>
/* Global Dark Tech Design System */
:root {
    --bg-primary: #0b0f19;
    --bg-card: #151c2c;
    --accent-indigo: #6366f1;
    --accent-cyan: #06b6d4;
    --accent-emerald: #10b981;
    --border-color: rgba(255, 255, 255, 0.08);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
}

.stApp {
    background-color: #0d1117;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #090d16 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-history-card {
    background: #131b2e;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
}

.sidebar-history-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    background: #18223a;
}

.history-title {
    font-size: 0.92rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1.35;
    margin-bottom: 6px;
}

.history-meta {
    font-size: 0.76rem;
    color: #94a3b8;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

/* Main Container Proportions */
.main .block-container {
    max-width: 900px;
    padding-top: 24px;
    padding-bottom: 60px;
    margin: 0 auto;
}

/* Hero Section Card */
.hero-header-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95));
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 18px;
    padding: 24px 30px;
    margin-bottom: 24px;
    box-shadow: 0 12px 30px -5px rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    gap: 20px;
}

.hero-logo-container {
    flex-shrink: 0;
    width: 80px;
    height: 80px;
    border-radius: 16px;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 25px rgba(99, 102, 241, 0.3);
    overflow: hidden;
}

.hero-logo-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 16px;
}

.hero-text-container {
    flex-grow: 1;
}

.hero-title {
    margin: 0;
    font-size: 1.95rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff, #c7d2fe, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    margin: 4px 0 0 0;
    color: #94a3b8;
    font-size: 0.93rem;
    line-height: 1.45;
}

.hero-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 8px;
}

.status-online {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-offline {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Agent Execution Cards */
.agent-card {
    background: #161e2e;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 14px 16px;
    transition: all 0.3s ease;
    margin-bottom: 12px;
    min-height: 85px;
}

.agent-card.active {
    border-color: #6366f1;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(15, 23, 42, 0.9));
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.35);
    animation: pulse-border 1.8s infinite ease-in-out;
}

.agent-card.completed {
    border-color: #10b981;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(15, 23, 42, 0.9));
}

@keyframes pulse-border {
    0% { border-color: rgba(99, 102, 241, 0.4); }
    50% { border-color: rgba(99, 102, 241, 1); box-shadow: 0 0 25px rgba(99, 102, 241, 0.5); }
    100% { border-color: rgba(99, 102, 241, 0.4); }
}

/* Terminal Log Viewport */
.terminal-window {
    background-color: #090d16;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 16px 20px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 0.86rem;
    color: #38bdf8;
    height: 220px;
    overflow-y: auto;
    margin-top: 14px;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.6);
}

.terminal-line {
    margin-bottom: 6px;
    line-height: 1.45;
}

.terminal-time {
    color: #64748b;
    margin-right: 8px;
}

/* Insight Callout Box */
.insight-box {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(99, 102, 241, 0.12));
    border-left: 4px solid #06b6d4;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 14px 0;
    font-size: 0.92rem;
    color: #cbd5e1;
}
</style>
"""
