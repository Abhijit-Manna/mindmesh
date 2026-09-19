"""
MindMesh Frontend - Hero Header Component
"""

import os
import base64
import streamlit as st


def resolve_logo_b64() -> str:
    """Resolve and base64-encode the MindMesh logo image."""
    frontend_dir = os.path.dirname(os.path.dirname(__file__))
    target_png = os.path.join(frontend_dir, "logo.png")
    target_jpg = os.path.join(frontend_dir, "logo.jpg")

    for img_path in [target_png, target_jpg]:
        if os.path.exists(img_path):
            try:
                with open(img_path, "rb") as img_f:
                    return base64.b64encode(img_f.read()).decode("utf-8")
            except Exception:
                pass
    return ""


def render_hero_header(is_healthy: bool):
    """Render the top Hero Section with glowing logo and backend status."""
    logo_b64 = resolve_logo_b64()
    status_class = "status-online" if is_healthy else "status-offline"
    status_text = "🟢 Live Backend Connected" if is_healthy else "🔴 Backend Offline"
    logo_img_html = f'<img src="data:image/jpeg;base64,{logo_b64}" alt="MindMesh Logo" />' if logo_b64 else '<span style="font-size:2.6rem;">⚡</span>'

    st.markdown(f"""
    <div class="hero-header-card">
        <div class="hero-logo-container">
            {logo_img_html}
        </div>
        <div class="hero-text-container">
            <h1 class="hero-title">MindMesh — SolutionForge AI</h1>
            <p class="hero-subtitle">
                Autonomous Multi-Agent Solution Architecture Engine powered by CrewAI & Gemini. Synthesize business visions into executive blueprints in real-time.
            </p>
            <span class="hero-status-pill {status_class}">{status_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
