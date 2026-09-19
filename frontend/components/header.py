"""
MindMesh Frontend - Hero Header Component (Ideogram-style)
"""

import streamlit as st


def render_hero_header(is_healthy: bool):
    """Render clean Ideogram-style hero — eyebrow, serif headline, subtitle, Try now pill button."""
    status_dot = "●" if is_healthy else "○"
    status_text = "System active" if is_healthy else "Backend offline"
    status_color = "#10b981" if is_healthy else "#ef4444"

    st.markdown(f"""
    <div class="hero-section">
        <div class="hero-eyebrow">MINDMESH ARCHITECT</div>
        <h1 class="hero-title">One reference idea.<br/>Endless consistent architectures.</h1>
        <p class="hero-subtitle">
            Provide a concept and generate production-grade system architecture, multi-agent evaluation, technology trade-offs, and delivery roadmaps. Precision engineering across every run.
        </p>
        <div class="hero-actions">
            <a href="#define-solution-parameters" class="hero-cta-btn">Try now</a>
            <div class="hero-status">
                <span style="color:{status_color}; font-size:0.75rem;">{status_dot}</span>
                <span>{status_text}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

