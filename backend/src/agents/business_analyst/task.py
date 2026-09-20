from crewai import Task
from typing import Optional
from .agent import create_business_analyst


def create_business_analyst_task(
    business_idea: str,
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
    relevant_experience: Optional[str] = None,
) -> Task:
    agent = create_business_analyst()

    description = f"""
Perform an exhaustive Business Analysis and Requirements Specification for the following initiative:

================ BUSINESS PROBLEM & INPUTS ================
Business Idea:
{business_idea}

Technology Preference: {technology_preference}
Cloud Preference: {cloud_preference}
Expected Daily Traffic: {expected_daily_traffic}
Delivery Timeline: {delivery_timeline_months} months
Data Hosting Country: {data_hosting_country}

================ RELEVANT PAST EXPERIENCE ================

{relevant_experience or "No relevant previous experience is available."}

Use this previous experience only as reference material.
Do not blindly copy previous decisions.
The current user's requirements and constraints always take priority.
If previous experience conflicts with the current requirements, follow
the current requirements and explain the appropriate reasoning.

================ DELIVERABLES REQUIRED ================
1. Executive Problem Definition & Value Proposition
2. Stakeholder & Persona Analysis Table (at least 3-4 distinct personas)
3. Exhaustive Functional Requirements Matrix (minimum 8-12 numbered FRs with Acceptance Criteria & MoSCoW priorities)
4. Quantified Non-Functional Requirements (P99 Latency, SLA, Scalability, Compliance for {data_hosting_country})
5. MVP Scope Boundary vs. Deferred Future Scope
6. Assumptions & Risk Matrix (with Severity, Likelihood, and Mitigations)
7. Key Open Discovery Questions

Format the deliverable with professional Markdown tables, structured sections, and detailed analytical depth.
Do NOT specify implementation technologies (languages, frameworks, DBs).
"""

    return Task(
        description=description,
        expected_output=(
            "An exhaustive, enterprise-grade Business Analysis document containing detailed stakeholder personas, "
            "a numbered functional requirements matrix with acceptance criteria, quantified NFRs, "
            "a rigorous MVP scope boundary, and a structured risk register."
        ),
        agent=agent,
    )