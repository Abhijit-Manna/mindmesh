"""
MindMesh Frontend - Completed Dashboard View Component
"""

import re
from urllib.parse import quote

import streamlit as st


def extract_sections_from_markdown(md_text: str) -> dict:
    """Fallback client-side section extractor from synthesized master blueprint markdown."""
    if not md_text:
        return {}

    sections = {
        "business_analyst": "",
        "solution_architect": "",
        "technology_advisor": "",
        "delivery_planner": ""
    }

    patterns = {
        "business_analyst": r"##\s*Section 1:[^\n]*\n(.*?)(?=\n##\s*Section 2:|\Z)",
        "solution_architect": r"##\s*Section 2:[^\n]*\n(.*?)(?=\n##\s*Section 3:|\Z)",
        "technology_advisor": r"##\s*Section 3:[^\n]*\n(.*?)(?=\n##\s*Section 4:|\Z)",
        "delivery_planner": r"##\s*Section 4:[^\n]*\n(.*?)(?=\n---\s*\n\*MindMesh|\Z)"
    }

    for key, pat in patterns.items():
        m = re.search(pat, md_text, re.DOTALL | re.IGNORECASE)
        if m:
            content = m.group(1).strip()
            content = re.sub(r"\n---\s*$", "", content).strip()
            content = re.sub(r"^\*Synthesized by[^\n]*\*\s*\n*", "", content, flags=re.IGNORECASE).strip()
            sections[key] = content

    # Fallback keyword matching
    if not sections["business_analyst"]:
        m = re.search(r"(?:###?\s*Business Analysis[^\n]*\n)(.*?)(?=(?:###?\s*(?:High-Level\s*)?Solution Architecture)|\Z)", md_text, re.DOTALL | re.IGNORECASE)
        if m:
            sections["business_analyst"] = m.group(1).strip()

    if not sections["solution_architect"]:
        m = re.search(r"(?:###?\s*(?:High-Level\s*)?Solution Architecture[^\n]*\n)(.*?)(?=(?:###?\s*Technology Stack)|\Z)", md_text, re.DOTALL | re.IGNORECASE)
        if m:
            sections["solution_architect"] = m.group(1).strip()

    if not sections["technology_advisor"]:
        m = re.search(r"(?:###?\s*Technology Stack[^\n]*\n)(.*?)(?=(?:###?\s*Implementation Roadmap|###?\s*Delivery Plan)|\Z)", md_text, re.DOTALL | re.IGNORECASE)
        if m:
            sections["technology_advisor"] = m.group(1).strip()

    if not sections["delivery_planner"]:
        m = re.search(r"(?:###?\s*(?:Implementation Roadmap|Delivery Plan)[^\n]*\n)(.*?)(?=\n---\s*\n\*MindMesh|\Z)", md_text, re.DOTALL | re.IGNORECASE)
        if m:
            sections["delivery_planner"] = m.group(1).strip()

    return sections


def render_dashboard_view():
    """Render the completed blueprint executive report and section tabs."""
    res = st.session_state.blueprint_result or {}
    run_id = res.get("run_id", "run_unknown")
    html_content = res.get("html") or res.get("result") or ""
    markdown_content = res.get("markdown") or ""

    # Parse sections if missing in response
    sections = res.get("sections") or {}
    if not sections or not any(sections.values()):
        sections = extract_sections_from_markdown(markdown_content)

    st.success(f" Architecture Blueprint Generated & Saved to SQLite DB! (Run ID: `{run_id}`)")

    # Top Action Buttons
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
        if st.button("✨ New Blueprint", use_container_width=True):
            st.session_state.execution_state = "idle"
            st.session_state.blueprint_result = None
            st.session_state.form_data = {
                "business_idea": "",
                "technology_preference": None,
                "cloud_preference": None,
                "expected_daily_traffic": None,
                "delivery_timeline_months": 4,
                "data_hosting_country": None
            }
            st.rerun()

    st.markdown("---")

    # Tabbed Interface for Output Visualization
    tab_html, tab_ba, tab_sa, tab_ta, tab_dp = st.tabs([
        " Executive Architecture Blueprint (HTML)",
        " Business Analysis",
        " System Architecture",
        " Tech Stack & Trade-offs",
        " Delivery Roadmap"
    ])

    with tab_html:
        if html_content:
            display_html = html_content.replace('class="dark-theme"', '').replace("class='dark-theme'", '')
            st.iframe(
                src=f"data:text/html;charset=utf-8,{quote(display_html)}",
                height=850,
            )
        else:
            st.info("HTML content not available for this run.")

    with tab_ba:
        st.subheader(" Section 1: Business Analysis & Functional Requirements")
        ba_sec = sections.get("business_analyst")
        if ba_sec and ba_sec.strip():
            st.markdown(ba_sec)
        elif markdown_content:
            st.markdown(markdown_content)
        else:
            st.info("Business Analysis details are compiling or not available.")

    with tab_sa:
        st.subheader(" Section 2: High-Level Solution Architecture & System Design")
        sa_sec = sections.get("solution_architect")
        if sa_sec and sa_sec.strip():
            st.markdown(sa_sec)
        elif markdown_content:
            st.markdown(markdown_content)
        else:
            st.info("Solution Architecture details are compiling or not available.")

    with tab_ta:
        st.subheader(" Section 3: Technology Stack & Architectural Trade-Offs")
        ta_sec = sections.get("technology_advisor")
        if ta_sec and ta_sec.strip():
            st.markdown(ta_sec)
        elif markdown_content:
            st.markdown(markdown_content)
        else:
            st.info("Technology recommendations are compiling or not available.")

    with tab_dp:
        st.subheader(" Section 4: Implementation Roadmap & Delivery Plan")
        dp_sec = sections.get("delivery_planner")
        if dp_sec and dp_sec.strip():
            st.markdown(dp_sec)
        elif markdown_content:
            st.markdown(markdown_content)
        else:
            st.info("Delivery Roadmap details are compiling or not available.")
