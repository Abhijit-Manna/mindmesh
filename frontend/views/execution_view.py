"""
MindMesh Frontend - Real-Time Execution View Component
"""

import time
import streamlit as st
from api_client import APIClient
from constants import ARCHITECTURE_INSIGHTS, AGENT_METADATA


def render_execution_view(api_client: APIClient):
    """Render the real-time Server-Sent Events (SSE) animated multi-agent execution view."""
    st.subheader("Multi-Agent Engine Active — Real-Time Execution")
    st.caption("Our autonomous agent team is synthesizing your requirements one by one via live backend streaming.")

    progress_bar = st.progress(5)
    status_placeholder = st.empty()
    agents_cols_placeholder = st.empty()
    terminal_placeholder = st.empty()
    insight_placeholder = st.empty()

    agent_names = [a["name"] for a in AGENT_METADATA]
    agent_icons = [a["icon"] for a in AGENT_METADATA]
    agent_roles = [a["role"] for a in AGENT_METADATA]

    current_active_idx = 0
    completed_agent_indices = set()
    accumulated_logs = []

    def render_agent_cards(active_idx: int, completed_indices: set):
        with agents_cols_placeholder.container():
            cols = st.columns(4)
            for i in range(4):
                with cols[i]:
                    if i in completed_indices:
                        st.markdown(f"""
                        <div class="agent-card completed">
                            <span style="font-size:1.25rem;">✅</span> <b>{agent_names[i]}</b><br/>
                            <span style="font-size:0.78rem; color:#047857;">Completed</span>
                        </div>
                        """, unsafe_allow_html=True)
                    elif i == active_idx:
                        st.markdown(f"""
                        <div class="agent-card active">
                            <span style="font-size:1.25rem;">{agent_icons[i]}</span> <b>{agent_names[i]}</b><br/>
                            <span style="font-size:0.78rem; color:#4f46e5;">Processing...</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="agent-card">
                            <span style="font-size:1.25rem;">⏳</span> <b>{agent_names[i]}</b><br/>
                            <span style="font-size:0.78rem; color:#94a3b8;">Queued</span>
                        </div>
                        """, unsafe_allow_html=True)

    render_agent_cards(0, completed_agent_indices)
    insight_placeholder.markdown(f"<div class='insight-box'>{ARCHITECTURE_INSIGHTS[0]}</div>", unsafe_allow_html=True)

    payload = st.session_state.form_data
    event_stream = api_client.stream_blueprint(payload)

    final_result_data = None
    stream_error = None

    for event in event_stream:
        ev_type = event.get("event")
        msg = event.get("message", "")
        pct = event.get("progress", 10)
        timestamp = time.strftime("%H:%M:%S")

        if ev_type == "init":
            accumulated_logs.append(f"<span class='terminal-time'>[{timestamp}] [System]</span> {msg}")
            progress_bar.progress(pct)
            status_placeholder.markdown("**Pipeline Initialized:** Starting agent sequence...")

        elif ev_type == "agent_start":
            agent_name = event.get("agent", "Agent")
            step = event.get("step", 1)
            current_active_idx = step - 1
            render_agent_cards(current_active_idx, completed_agent_indices)

            accumulated_logs.append(f"<span class='terminal-time'>[{timestamp}] [{agent_name}]</span> {msg}")
            progress_bar.progress(pct)
            status_placeholder.markdown(f"**Current Phase:** {agent_icons[current_active_idx]} `{agent_name}` — *{agent_roles[current_active_idx]}*")

            insight_placeholder.markdown(f"<div class='insight-box'>{ARCHITECTURE_INSIGHTS[current_active_idx % len(ARCHITECTURE_INSIGHTS)]}</div>", unsafe_allow_html=True)

        elif ev_type == "agent_complete":
            agent_name = event.get("agent", "Agent")
            step = event.get("step", 1)
            completed_agent_indices.add(step - 1)
            if step < 4:
                current_active_idx = step
            render_agent_cards(current_active_idx, completed_agent_indices)

            accumulated_logs.append(f"<span class='terminal-time'>[{timestamp}] [{agent_name}]</span> ✅ {msg}")
            progress_bar.progress(pct)

        elif ev_type == "complete":
            progress_bar.progress(100)
            status_placeholder.markdown("**Generation Completed & Saved to SQLite DB!** Compiling executive blueprint...")
            final_result_data = event
            break

        elif ev_type == "error":
            stream_error = event.get("error") or event.get("message") or "Unknown error"
            accumulated_logs.append(f"<span class='terminal-time'>[{timestamp}] [Error]</span> ❌ {stream_error}")
            break

        terminal_html = "<div class='terminal-window'>" + "".join(
            [f"<div class='terminal-line'>{line}</div>" for line in accumulated_logs[-8:]]
        ) + "</div>"
        terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)

    if final_result_data:
        st.session_state.blueprint_result = final_result_data
        st.session_state.execution_state = "completed"
        time.sleep(0.8)
        st.rerun()
    elif stream_error:
        st.session_state.error_message = stream_error
        st.session_state.execution_state = "error"
        time.sleep(0.8)
        st.rerun()
    else:
        st.session_state.error_message = "Stream ended unexpectedly without complete signal."
        st.session_state.execution_state = "error"
        st.rerun()
