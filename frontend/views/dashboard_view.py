"""
MindMesh Frontend - Completed Dashboard View Component
"""

import streamlit as st
import streamlit.components.v1 as components


def render_dashboard_view():
    """Render the completed blueprint executive report and section tabs."""
    res = st.session_state.blueprint_result or {}
    run_id = res.get("run_id", "run_unknown")
    html_content = res.get("html") or res.get("result") or ""
    sections = res.get("sections", {})

    st.success(f" Architecture Blueprint Generated & Saved to SQLite DB! (Run ID: `{run_id}`)")

    # Top Action Buttons (Only HTML Download)
    col_btn1, col_btn2, col_btn3 = st.columns([3, 2, 1])
    with col_btn1:
        st.caption(f"Status: {res.get('status', 'completed')} • Stored in SQLite (`backend/db/mindmesh.db`)")
    with col_btn2:
        st.download_button(
            label="Download Official HTML Blueprint (.html)",
            data=html_content,
            file_name=f"mindmesh-blueprint-{run_id}.html",
            mime="text/html",
            use_container_width=True
        )
    with col_btn3:
        if st.button(" New Blueprint", use_container_width=True):
            st.session_state.execution_state = "idle"
            st.session_state.blueprint_result = None
            st.rerun()

    st.markdown("---")

    # Tabbed Interface for Output Visualization
    tab_html, tab_ba, tab_sa, tab_ta, tab_dp = st.tabs([
        " Executive Architecture Blueprint (HTML)",
        " Business Analysis",
        "System Architecture",
        "Tech Stack & Trade-offs",
        " Delivery Roadmap"
    ])

    with tab_html:
        if html_content:
            components.html(html_content, height=850, scrolling=True)
        else:
            st.info("HTML content not available for this run.")

    with tab_ba:
        st.subheader(" Section 1: Business Analysis & Scope")
        ba_sec = sections.get("business_analyst") or "Refer to master report."
        st.markdown(ba_sec)

    with tab_sa:
        st.subheader(" Section 2: Solution Architecture & System Design")
        sa_sec = sections.get("solution_architect") or "Refer to master report."
        st.markdown(sa_sec)

    with tab_ta:
        st.subheader(" Section 3: Technology Stack & Trade-Offs")
        ta_sec = sections.get("technology_advisor") or "Refer to master report."
        st.markdown(ta_sec)

    with tab_dp:
        st.subheader(" Section 4: Implementation Roadmap & Delivery Plan")
        dp_sec = sections.get("delivery_planner") or "Refer to master report."
        st.markdown(dp_sec)
