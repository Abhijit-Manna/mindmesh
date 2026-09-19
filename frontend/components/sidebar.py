"""
MindMesh Frontend - Sidebar Recent History Component
"""

import time
import urllib.parse
import streamlit as st
from api_client import APIClient


def render_sidebar_history(api_client: APIClient, is_healthy: bool):
    """Render the recent blueprints history sidebar."""
    with st.sidebar:
        st.markdown("### 📚 Recent Blueprints")
        st.caption("Saved architecture blueprints from SQLite database")

        if is_healthy:
            success, list_data, err = api_client.list_blueprints()
            history_list = list_data.get("history", [])
            run_ids = list_data.get("run_ids", [])

            if history_list or run_ids:
                items = history_list if history_list else [{"run_id": r, "business_idea": f"Architecture Blueprint ({r})", "created_at": ""} for r in run_ids]

                for item in items[:20]:
                    r_id = item.get("run_id", "")
                    created = item.get("created_at", "")

                    # Clean human-readable business idea title
                    raw_idea = item.get("business_idea") or ""
                    clean_idea = urllib.parse.unquote(raw_idea).strip()

                    if clean_idea and not clean_idea.startswith("Blueprint Run"):
                        first_phrase = clean_idea.split("\n")[0].split(". ")[0].strip()
                        display_title = first_phrase if len(first_phrase) <= 60 else f"{first_phrase[:57]}..."
                    else:
                        display_title = f"Architecture Blueprint ({r_id[:8]})"

                    cloud = item.get("cloud_preference") or ""
                    tech = item.get("technology_preference") or ""
                    tag_text = cloud if cloud and cloud != "No Preference" else (tech.split("(")[0].strip() if tech else "Blueprint")

                    with st.container():
                        st.markdown(f"""
                        <div class="sidebar-history-card">
                            <div class="history-title">💡 {display_title}</div>
                            <div class="history-meta">
                                <span>🕒 {created or 'Recent'}</span>
                                <span style="color:#818cf8; font-weight:600; font-size:0.75rem;">{tag_text}</span>
                            </div>
                            <div style="font-size:0.72rem; color:#64748b; font-family:monospace;">ID: {r_id}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        c1, c2 = st.columns([3, 1])
                        with c1:
                            if st.button("👁️ Load", key=f"sb_load_{r_id}", use_container_width=True):
                                g_success, g_data, g_err = api_client.get_blueprint(r_id)
                                if g_success:
                                    st.session_state.blueprint_result = g_data
                                    st.session_state.execution_state = "completed"
                                    st.rerun()
                                else:
                                    st.error(g_err)
                        with c2:
                            if st.button("🗑️", key=f"sb_del_{r_id}", help="Delete blueprint", use_container_width=True):
                                d_success, _, d_err = api_client.delete_blueprint(r_id)
                                if d_success:
                                    st.toast(f"Deleted blueprint {r_id}")
                                    time.sleep(0.3)
                                    st.rerun()

                        st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)
            else:
                st.info("No saved blueprints yet.\nGenerate your first blueprint to see history here.")
        else:
            st.warning("🟡 Backend offline. Start backend to access SQLite history.")
