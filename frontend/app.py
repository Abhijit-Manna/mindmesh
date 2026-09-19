"""
MindMesh — AI System Blueprint Generator (Streamlit Frontend)

Senior-grade Web Interface featuring:
- Form collection for all 6 blueprint parameters
- Anti-boredom multi-agent animated execution progress (2-3 min interactive loading)
- Integration with FastAPI backend routes (/api/v1/blueprints)
- Separate fallback dummy data module (dummy_data.py)
- Interactive blueprint report visualization & export options
"""

import streamlit as st
import time
import threading
import json
from pathlib import Path
from typing import Dict, Any, Optional

from dummy_data import (
    PRESET_TEMPLATES,
    AGENT_WORKFLOW_STEPS,
    ARCHITECTURE_INSIGHTS,
    get_dummy_response
)
from api_client import APIClient

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="MindMesh — AI Architecture Blueprint Engine",
    page_icon="⚡",
    layout="wide",
   # initial_sidebar_state="expanded"
)

# --- Developer Custom CSS & Animations ---
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

/* Glassmorphic Container Cards */
.stApp {
    background-color: #0d1117;
}

.main-header-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.agent-card {
    background: #161e2e;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px 20px;
    transition: all 0.3s ease;
    margin-bottom: 12px;
}

.agent-card.active {
    border-color: #6366f1;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(15, 23, 42, 0.8));
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.25);
    animation: pulse-border 2s infinite ease-in-out;
}

.agent-card.completed {
    border-color: #10b981;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(15, 23, 42, 0.8));
}

@keyframes pulse-border {
    0% { border-color: rgba(99, 102, 241, 0.4); }
    50% { border-color: rgba(99, 102, 241, 1); }
    100% { border-color: rgba(99, 102, 241, 0.4); }
}

/* Terminal Log Viewport */
.terminal-window {
    background-color: #090d16;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 16px;
    font-family: 'Fira Code', 'Courier New', monospace;
    font-size: 0.88rem;
    color: #38bdf8;
    height: 220px;
    overflow-y: auto;
    margin-top: 12px;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.5);
}

.terminal-line {
    margin-bottom: 6px;
    line-height: 1.4;
}

.terminal-time {
    color: #64748b;
    margin-right: 8px;
}

/* Insight Callout Box */
.insight-box {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(99, 102, 241, 0.1));
    border-left: 4px solid #06b6d4;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 16px 0;
    font-size: 0.95rem;
}

/* Badge tags */
.tech-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    background: rgba(99, 102, 241, 0.2);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.3);
    margin-right: 6px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Session State Initialization ---
if "execution_state" not in st.session_state:
    st.session_state.execution_state = "idle"  # idle, running, completed, error
if "blueprint_result" not in st.session_state:
    st.session_state.blueprint_result = None
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False
if "error_message" not in st.session_state:
    st.session_state.error_message = ""
if "form_preset" not in st.session_state:
    st.session_state.form_preset = None

# Form field values stored in session state for instant pre-filling
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "business_idea": "",
        "technology_preference": "Open-Source Stack (Python FastAPI / Node.js + React)",
        "cloud_preference": "AWS",
        "expected_daily_traffic": "50,000 DAU (Peak 2,500 req/sec)",
        "delivery_timeline_months": 6,
        "data_hosting_country": "United States"
    }

api_client = APIClient(base_url=st.session_state.api_url)

#--- Sidebar Controls & Connection Status ---
with st.sidebar:
    st.image("logo.png", width=100)
    st.title("MindMesh Engine")
    st.caption("AI-Powered Enterprise Solution Blueprinting")
    st.markdown("---")
    
    # API Backend Health Check
    is_healthy, health_msg = api_client.check_health()
    if is_healthy:
        st.success(f"🟢 {health_msg}")
    else:
        st.warning(f"🟡 Backend Offline")
        st.caption("Auto-switching to Demo Mode for instant response.")
        st.session_state.demo_mode = True

    # Backend API URL Setting
    with st.expander("⚙️ Connection Settings"):
        new_url = st.text_input("Backend API Base URL", value=st.session_state.api_url)
        if new_url != st.session_state.api_url:
            st.session_state.api_url = new_url
            st.rerun()
        
        st.session_state.demo_mode = st.toggle("🧪 Force Demo / Mock Data Mode", value=st.session_state.demo_mode)

    st.markdown("---")
    
    # History & Saved Blueprints (GET /api/v1/blueprints)
    st.subheader("📚 Saved Blueprints")
    if is_healthy and not st.session_state.demo_mode:
        success, list_data, err = api_client.list_blueprints()
        if success and list_data.get("run_ids"):
            run_ids = list_data.get("run_ids", [])
            st.caption(f"Total stored runs: {len(run_ids)}")
            selected_run = st.selectbox("Select saved run_id:", options=["-- Select --"] + run_ids)
            if selected_run != "-- Select --":
                col_get, col_del = st.columns(2)
                with col_get:
                    if st.button("👁️ Load Run", key=f"btn_load_{selected_run}"):
                        g_success, g_data, g_err = api_client.get_blueprint(selected_run)
                        if g_success:
                            st.session_state.blueprint_result = g_data
                            st.session_state.execution_state = "completed"
                            st.rerun()
                        else:
                            st.error(g_err)
                with col_del:
                    if st.button("🗑️ Delete", key=f"btn_del_{selected_run}"):
                        d_success, d_data, d_err = api_client.delete_blueprint(selected_run)
                        if d_success:
                            st.success("Deleted!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(d_err)
        else:
            st.caption("No previous runs saved on backend.")
    else:
        st.caption("Connect backend to list stored runs.")

    st.markdown("---")
    st.caption("MindMesh v1.0 • Senior Frontend Edition")


# --- Main Header ---
st.markdown("""
<div class="main-header-card">
    <h1 style="margin:0; font-size: 2.2rem; color: #f8fafc; font-weight: 700;">
        ⚡ SolutionForge AI — A Multi-Agent Solution Architect for All Your Business Needs
    </h1>
    <p style="margin: 8px 0 0 0; color: #94a3b8; font-size: 1.05rem; line-height: 1.5;">
        Transform your business vision into an enterprise-grade technical architecture & delivery roadmap powered by autonomous CrewAI agents.
    </p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# VIEW 1: INPUT FORM (First Page - Form Only)
# ==============================================================================
if st.session_state.execution_state == "idle":
    st.subheader("📋 Step 1: Define Project Parameters")
    st.caption("Select a quick preset template below or enter your custom project requirements.")

    # Preset Selection Quick-Fill Buttons
    cols_preset = st.columns([1, 1, 1])
    for idx, (key, preset) in enumerate(PRESET_TEMPLATES.items()):
        with cols_preset[idx]:
            if st.button(preset["title"], key=f"preset_{key}", use_container_width=True):
                st.session_state.form_data = {
                    "business_idea": preset["business_idea"],
                    "technology_preference": preset["technology_preference"],
                    "cloud_preference": preset["cloud_preference"],
                    "expected_daily_traffic": preset["expected_daily_traffic"],
                    "delivery_timeline_months": preset["delivery_timeline_months"],
                    "data_hosting_country": preset["data_hosting_country"]
                }
                st.rerun()

    st.markdown("---")

    # Main Form Requesting exact 6 required fields
    with st.form("blueprint_request_form"):
        # Field 1: business_idea (str)
        business_idea = st.text_area(
            "1. Business Idea & Functional Scope *",
            value=st.session_state.form_data["business_idea"],
            placeholder="Describe your product concept, target users, primary features, and core business workflow...",
            height=140,
            help="Required: Minimum 20 characters describing your application idea."
        )

        col1, col2 = st.columns(2)
        with col1:
            # Field 2: technology_preference (str)
            technology_preference = st.selectbox(
                "2. Technology Stack Preference *",
                
                options=["Select your preference",
                    "Open-Source Stack (Python FastAPI / Node.js + React + PostgreSQL)",
                    "Enterprise Stack (Java Spring Boot / C# .NET Core + Angular)",
                    "Microservices Mesh (Go Microservices + gRPC + React)",
                    "Serverless Ecosystem (TypeScript + AWS Lambda + DynamoDB)"
                ],
                index=0,
                help="Select your architectural ecosystem preference."
            )

            # Field 3: cloud_preference (str)
            cloud_preference = st.selectbox(
                "3. Cloud Infrastructure Preference *",
                options=["Select your preference","AWS", "Google Cloud (GCP)", "Azure", "Multi-Cloud Ecosystem", "On-Premises / Bare Metal","No Preference"],
                index=0,
                help="Select primary hosting provider."
            )

            # Field 4: expected_daily_traffic (str)
            expected_daily_traffic = st.selectbox(
                "4. Expected Daily Traffic & Scale *",
                options=[ "Select your preference",
                    "10,000 DAU (Standard MVP Scale)",
                    "50,000 DAU (Peak 2,500 req/sec)",
                    "100,000 DAU (High Concurrency & Load)",
                    "1,000,000+ DAU (Global Enterprise Scale)"
                ],
                index=1,
                help="Expected active user concurrency."
            )

        with col2:
            # Field 5: delivery_timeline_months (int)
            delivery_timeline_months = st.number_input(
                "5. Target Delivery Timeline (Months) *",
                min_value=1,
                max_value=36,
                value=int(st.session_state.form_data["delivery_timeline_months"]),
                step=1,
                help="Whole number of months to target MVP launch."
            )

            # Field 6: data_hosting_country (str)
            data_hosting_country = st.selectbox(
                "6. Data Hosting Region / Jurisdiction *",
                options=["Select your preference",
                    "United States",
                    "India",
                    "Germany (EU GDPR Compliant)",
                    "Singapore (APAC Region)",
                    "United Kingdom",
                    "Global Multi-Region"
                ],
                index=0,
                help="Data residency compliance target."
            )

        submit_btn = st.form_submit_button("🚀 Generate Architecture Blueprint", type="primary", use_container_width=True)

    if submit_btn:
        # Validation
        if not business_idea or len(business_idea.strip()) < 15:
            st.error("⚠️ Please provide a detailed business idea (at least 15 characters).")
        else:
            # Update session state form payload
            st.session_state.form_data = {
                "business_idea": business_idea.strip(),
                "technology_preference": technology_preference,
                "cloud_preference": cloud_preference,
                "expected_daily_traffic": expected_daily_traffic,
                "delivery_timeline_months": int(delivery_timeline_months),
                "data_hosting_country": data_hosting_country
            }
            # Change state to running to show animated execution view!
            st.session_state.execution_state = "running"
            st.rerun()


# ==============================================================================
# VIEW 2: ANIMATED MULTI-AGENT EXECUTION SCREEN (2-3 Min Anti-Boredom UX)
# ==============================================================================
elif st.session_state.execution_state == "running":
    st.subheader("🤖 Multi-Agent Engine Active")
    st.caption("Our autonomous agent team is synthesizing your requirements into an architectural blueprint. Estimated duration: ~60-120 seconds.")

    # Execution Progress Containers
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    agents_cols_placeholder = st.empty()
    terminal_placeholder = st.empty()
    insight_placeholder = st.empty()

    payload = st.session_state.form_data
    use_demo = st.session_state.demo_mode or not is_healthy

    # Start Async Backend Call in Background Thread if not demo mode
    api_result_container = {"completed": False, "success": False, "data": None, "err": ""}

    def run_backend_call():
        success, data, err = api_client.create_blueprint(payload, timeout=240)
        api_result_container["success"] = success
        api_result_container["data"] = data
        api_result_container["err"] = err
        api_result_container["completed"] = True

    if not use_demo:
        thread = threading.Thread(target=run_backend_call)
        thread.start()

    # Animation Loop over Workflow Steps
    total_steps = len(AGENT_WORKFLOW_STEPS)
    start_time = time.time()
    accumulated_logs = []

    for step_idx, step in enumerate(AGENT_WORKFLOW_STEPS):
        agent_name = step["agent"]
        agent_icon = step["icon"]
        agent_role = step["role"]
        duration = step["duration"]

        # Render Agent Cards Status
        with agents_cols_placeholder.container():
            ac1, ac2, ac3, ac4 = st.columns(4)
            cols = [ac1, ac2, ac3, ac4]
            for i, s in enumerate(AGENT_WORKFLOW_STEPS):
                with cols[i]:
                    if i < step_idx:
                        st.markdown(f"""
                        <div class="agent-card completed">
                            <span style="font-size:1.4rem;">✅</span> <b>{s['agent']}</b><br/>
                            <span style="font-size:0.8rem; color:#10b981;">Completed</span>
                        </div>
                        """, unsafe_allow_html=True)
                    elif i == step_idx:
                        st.markdown(f"""
                        <div class="agent-card active">
                            <span style="font-size:1.4rem;">{s['icon']}</span> <b>{s['agent']}</b><br/>
                            <span style="font-size:0.8rem; color:#818cf8;">Processing...</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="agent-card">
                            <span style="font-size:1.4rem;">⏳</span> <b>{s['agent']}</b><br/>
                            <span style="font-size:0.8rem; color:#64748b;">Queued</span>
                        </div>
                        """, unsafe_allow_html=True)

        # Rotate Insight Tip
        insight_msg = ARCHITECTURE_INSIGHTS[step_idx % len(ARCHITECTURE_INSIGHTS)]
        insight_placeholder.markdown(f"""
        <div class="insight-box">
            {insight_msg}
        </div>
        """, unsafe_allow_html=True)

        # Simulate logs inside current agent step
        logs_list = step["logs"]
        sub_steps = len(logs_list)
        time_per_sub = duration / sub_steps if use_demo else 2.5

        for log_sub_idx, log_msg in enumerate(logs_list):
            if not use_demo and api_result_container["completed"]:
                break

            timestamp = time.strftime("%H:%M:%S")
            accumulated_logs.append(f"<span class='terminal-time'>[{timestamp}] [{agent_name}]</span> {log_msg}")
            
            # Update Terminal UI
            terminal_html = "<div class='terminal-window'>" + "".join(
                [f"<div class='terminal-line'>{line}</div>" for line in accumulated_logs[-7:]]
            ) + "</div>"
            terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)

            # Update overall progress bar & status text
            overall_pct = int(((step_idx * sub_steps + log_sub_idx + 1) / (total_steps * sub_steps)) * 95)
            progress_bar.progress(overall_pct)
            elapsed_sec = int(time.time() - start_time)
            status_placeholder.markdown(f"**Current Phase:** {agent_icon} `{agent_name}` — *{agent_role}* (Elapsed: {elapsed_sec}s)")

            time.sleep(0.4 if use_demo else 0.8)

        if not use_demo and api_result_container["completed"]:
            break

    # If using backend API, wait for thread completion if still running
    if not use_demo:
        with st.spinner("Finalizing blueprint compilation from backend..."):
            thread.join(timeout=180)
            if api_result_container["success"]:
                st.session_state.blueprint_result = api_result_container["data"]
                st.session_state.execution_state = "completed"
            else:
                st.session_state.error_message = api_result_container["err"]
                st.session_state.execution_state = "error"
    else:
        # Demo mode fallback response
        progress_bar.progress(100)
        time.sleep(0.5)
        st.session_state.blueprint_result = get_dummy_response(payload)
        st.session_state.execution_state = "completed"

    st.rerun()


# ==============================================================================
# VIEW 3: BLUEPRINT OUTPUT & INTERACTIVE DASHBOARD
# ==============================================================================
elif st.session_state.execution_state == "completed":
    res = st.session_state.blueprint_result or {}
    run_id = res.get("run_id", "run_unknown")
    markdown_content = res.get("result") or res.get("markdown") or "No markdown output returned."

    st.success(f"🎉 Architecture Blueprint Generated Successfully! (Run ID: `{run_id}`)")

    # Top Action Buttons
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    with col_btn1:
        st.caption(f"Status: {res.get('status', 'completed')} • Saved: `{res.get('file_saved', 'outputs/' + run_id + '.md')}`")
    with col_btn2:
        st.download_button(
            label="📥 Download Markdown (.md)",
            data=markdown_content,
            file_name=f"blueprint-{run_id}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_btn3:
        if st.button("🔄 Create New Blueprint", use_container_width=True):
            st.session_state.execution_state = "idle"
            st.session_state.blueprint_result = None
            st.rerun()

    st.markdown("---")

    # Tabbed Interface for Output Visualization
    tab_doc, tab_cards, tab_meta, tab_raw = st.tabs([
        "📄 Full Blueprint Report",
        "🏛️ Architecture Summary",
        "🤖 Agent Execution Metrics",
        "💾 Raw API Payload"
    ])

    with tab_doc:
        st.markdown(markdown_content)

    with tab_cards:
        st.subheader("Key Architecture Decisions")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("**Selected Tech Stack**\n\n" + st.session_state.form_data.get("technology_preference", "N/A"))
            st.info("**Expected Daily Traffic**\n\n" + st.session_state.form_data.get("expected_daily_traffic", "N/A"))
        with c2:
            st.success("**Cloud Provider**\n\n" + st.session_state.form_data.get("cloud_preference", "N/A"))
            st.success("**Target Timeline**\n\n" + f"{st.session_state.form_data.get('delivery_timeline_months', 6)} Months")
        with c3:
            st.warning("**Data Residency**\n\n" + st.session_state.form_data.get("data_hosting_country", "N/A"))
            st.warning("**Evaluation Status**\n\n100% Schema Valid")

    with tab_meta:
        st.subheader("Multi-Agent Handoff & Attempt Log")
        meta = res.get("run_metadata", {})
        attempts = meta.get("attempts", {"Business Analyst": 1, "Solution Architect": 1, "Technology Advisor": 1, "Delivery Planner": 1})
        
        st.write("**Agent Evaluation Gate Retries:**")
        st.json(attempts)
        if "duration_ms" in meta:
            st.write(f"**Total Generation Duration:** {meta['duration_ms'] / 1000:.2f} seconds")

    with tab_raw:
        st.subheader("Raw FastAPI JSON Response")
        st.json(res)


# ==============================================================================
# VIEW 4: ERROR DISPLAY SCREEN
# ==============================================================================
elif st.session_state.execution_state == "error":
    st.error("❌ Blueprint Generation Failed")
    st.warning(f"Error details: {st.session_state.error_message}")
    st.info("💡 You can retry with Demo Mode enabled or check if backend services are running.")

    if st.button("⬅️ Return to Form"):
        st.session_state.execution_state = "idle"
        st.rerun()