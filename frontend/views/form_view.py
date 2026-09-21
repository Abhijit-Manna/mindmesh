"""
MindMesh Frontend - Form View Component
"""

import time
from urllib.parse import quote

import streamlit as st
from constants import (
    PRESET_TEMPLATES,
    TECH_STACK_OPTIONS,
    CLOUD_OPTIONS,
)


def render_form_view():
    """Render the initial project parameters input form."""
    st.markdown("<div id='define-solution-parameters'></div>", unsafe_allow_html=True)
    st.subheader("Define Solution Parameters")
    st.caption("Select a preset template or configure your custom technical parameters.")

    # Preset Quick-Fill Buttons
    cols_preset = st.columns(3)
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

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # Main Parameters Form
    with st.form("blueprint_request_form"):
        business_idea = st.text_area(
            "1. Business Idea & Functional Scope *",
            value=st.session_state.form_data.get("business_idea") or "",
            placeholder="Describe your product concept, target users, primary features, and core business workflow...",
            height=125,
            help="Required: Minimum 20 characters describing your application idea."
        )

        col1, col2 = st.columns(2)
        with col1:
            cur_tech = st.session_state.form_data.get("technology_preference")
            tech_idx = TECH_STACK_OPTIONS.index(cur_tech) if cur_tech in TECH_STACK_OPTIONS else 0
            technology_preference = st.selectbox(
                "2. Technology Stack *",
                options=TECH_STACK_OPTIONS,
                index=tech_idx,
                help="Select your architectural ecosystem preference."
            )

            cur_cloud = st.session_state.form_data.get("cloud_preference")
            cloud_idx = CLOUD_OPTIONS.index(cur_cloud) if cur_cloud in CLOUD_OPTIONS else 0
            cloud_preference = st.selectbox(
                "3. Cloud Infrastructure *",
                options=CLOUD_OPTIONS,
                index=cloud_idx,
                help="Select primary hosting provider."
            )

            cur_traffic = st.session_state.form_data.get("expected_daily_traffic")
            expected_daily_traffic = st.text_input(
                "4. Expected Daily Traffic & Scale *",
                value=cur_traffic or "",
                placeholder="Example: 50,000 daily users, peak 2,500 requests/sec",
                help="Describe expected daily users, requests per second, or peak concurrency."
            )

        with col2:
            delivery_timeline_months = st.number_input(
                "5. Target Delivery Timeline (Months) *",
                min_value=1,
                max_value=36,
                value=int(st.session_state.form_data.get("delivery_timeline_months") or 4),
                step=1,
                help="Whole number of months to target MVP launch."
            )
            cur_country = st.session_state.form_data.get("data_hosting_country")
            cur_country = st.session_state.form_data.get("data_hosting_country")
            data_hosting_country = st.text_input(
                "6. Data Hosting Region / Jurisdiction *",
                value=cur_country or "",
                placeholder="Example: India, United States, or EU/Germany",
                help="Enter the country, region, or data-residency requirement."
            )

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("Generate Architecture Blueprint", type="primary", use_container_width=True)

    # Attach interactive button loading spinner on click
    spinner_script = """
    <script>
    const attachButtonSpinner = () => {
        try {
            const doc = window.parent.document;
            const btn = doc.querySelector('[data-testid="stFormSubmitButton"] button');
            if (btn && !btn.dataset.hasSpinner) {
                btn.dataset.hasSpinner = "true";
                btn.addEventListener('click', () => {
                    const textContainer = btn.querySelector('p') || btn.querySelector('span') || btn;
                    if (textContainer && !textContainer.querySelector('.btn-spinner-icon')) {
                        const spinner = document.createElement('span');
                        spinner.className = 'btn-spinner-icon';
                        spinner.setAttribute('style', 'display:inline-block; width:13px; height:13px; border:2px solid rgba(255,255,255,0.35); border-top-color:#ffffff; border-radius:50%; margin-right:8px; animation:spin 0.6s linear infinite; vertical-align:-1px;');
                        textContainer.prepend(spinner);
                    }
                });
            }
        } catch (e) {}
    };
    attachButtonSpinner();
    setInterval(attachButtonSpinner, 400);
    </script>
    """
    st.iframe(
        src=f"data:text/html;charset=utf-8,{quote(spinner_script)}",
        height=1,
        width="content",
    )

    if submit_btn:
        errors = []
        if not business_idea or len(business_idea.strip()) < 15:
            errors.append("Please provide a detailed business idea (at least 15 characters).")
        if technology_preference == "-- Select Technology Stack --":
            errors.append("Please select a Technology Stack.")
        if cloud_preference == "-- Select Cloud Infrastructure --":
            errors.append("Please select a Cloud Infrastructure preference.")
        if expected_daily_traffic == "-- Select Expected Daily Traffic --":
            errors.append("Please select Expected Daily Traffic.")
        if data_hosting_country == "-- Select Data Hosting Region --":
            errors.append("Please select a Data Hosting Region.")

        if errors:
            for err in errors:
                st.error(f"{err}")
        else:
            st.session_state.form_data = {
                "business_idea": business_idea.strip(),
                "technology_preference": technology_preference,
                "cloud_preference": cloud_preference,
                "expected_daily_traffic": expected_daily_traffic,
                "delivery_timeline_months": int(delivery_timeline_months),
                "data_hosting_country": data_hosting_country
            }
            with st.spinner("Loading architecture synthesis engine..."):
                time.sleep(0.3)
                st.session_state.execution_state = "running"
                st.rerun()
