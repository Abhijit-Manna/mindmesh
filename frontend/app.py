"""
MindMesh — AI System Blueprint Generator (Streamlit Frontend)

Modular Entry Point coordinating:
- Custom dark tech design system (styles.py)
- Top Hero Section & Brand Header (components/header.py)
- Recent Blueprints History Sidebar (components/sidebar.py)
- Multi-step views: Form View, Real-Time Execution View, Dashboard View
"""

import streamlit as st

from api_client import APIClient
from styles import CUSTOM_CSS
from components.header import render_hero_header
from components.sidebar import render_sidebar_history
from views.form_view import render_form_view
from views.execution_view import render_execution_view
from views.dashboard_view import render_dashboard_view

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="MindMesh — AI Architecture Blueprint Engine",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Session State Initialization ---
if "execution_state" not in st.session_state:
    st.session_state.execution_state = "idle"  # idle, running, completed, error
if "blueprint_result" not in st.session_state:
    st.session_state.blueprint_result = None
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if "error_message" not in st.session_state:
    st.session_state.error_message = ""
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "business_idea": "",
        "technology_preference": None,
        "cloud_preference": None,
        "expected_daily_traffic": None,
        "delivery_timeline_months": 4,
        "data_hosting_country": None
    }

# API Client & Health Check
api_client = APIClient(base_url=st.session_state.api_url)
is_healthy, health_msg = api_client.check_health()

# Render Global Header and Sidebar
render_sidebar_history(api_client, is_healthy)
render_hero_header(is_healthy)

# --- Main Application State Router ---
if st.session_state.execution_state == "idle":
    render_form_view()

elif st.session_state.execution_state == "running":
    render_execution_view(api_client)

elif st.session_state.execution_state == "completed":
    render_dashboard_view()

elif st.session_state.execution_state == "error":
    st.error("❌ Blueprint Generation Failed")
    st.warning(f"Error details: {st.session_state.error_message}")
    st.info("💡 Ensure backend is running (`uv run fastapi dev main.py`) and API keys in backend `.env` are valid.")

    if st.button("⬅️ Return to Parameters Form"):
        st.session_state.execution_state = "idle"
        st.rerun()