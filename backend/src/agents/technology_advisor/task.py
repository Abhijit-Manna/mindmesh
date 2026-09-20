from crewai import Task
from typing import Optional
from .agent import create_technology_advisor


def create_technology_advisor_task(
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
    ba_task: Task,
    sa_task: Task,
    relevant_experience: Optional[str] = None,
) -> Task:
    agent = create_technology_advisor()

    description = f"""
Conduct an exhaustive Technology Stack Selection and Architectural Trade-off Analysis.

================ USER CONSTRAINTS ================
Technology Preference: {technology_preference}
Cloud Infrastructure Preference: {cloud_preference}
Expected Daily Traffic: {expected_daily_traffic}
Delivery Timeline: {delivery_timeline_months} months
Data Hosting Country / Region: {data_hosting_country}

================ RELEVANT PAST EXPERIENCE ================

{relevant_experience or "No relevant previous experience is available."}

Use previous experiences as reference when evaluating technology
choices and trade-offs.

Do not blindly copy previous technology decisions.
The current user's constraints, the Business Analyst requirements,
and the Solution Architect's design take priority.

If a previous experience conflicts with the current project,
discard that experience and reason from the current requirements.

Pay particular attention to previously successful technology choices,
rejected alternatives, evaluator feedback, and lessons learned.

================ DELIVERABLES REQUIRED ================
1. Authoritative Recommended Technology Stack Matrix (Layer, Technology, Version, Rationale)
2. In-Depth Comparative Trade-Off Analysis (Compare chosen Backend, Database, and Queue against 2 viable alternatives each)
3. Open-Source vs. Enterprise Strategy & Licensing Compliance (MIT, Apache 2.0, vendor lock-in analysis)
4. Database & Storage Architecture (Schema design considerations, caching tier, queue architecture)
5. Cloud Services Mapping on {cloud_preference} (Compute, Managed DB, Cache, Object Storage, Network)
6. Developer Toolchain & Quality Tooling (Testing, Linting, OpenAPI)
7. Technology Trade-offs, Scalability Limits & Risk Mitigation

Ensure 100% adherence to {cloud_preference} and {data_hosting_country}. Provide rich, detailed Markdown tables and in-depth technical analysis.
"""

    return Task(
        description=description,
        expected_output=(
            "An authoritative, highly detailed Technology Stack Specification and Trade-off Analysis "
            "containing stack matrices, comparative evaluations against alternatives, database and caching architecture, "
            "and concrete cloud service mappings."
        ),
        agent=agent,
        context=[ba_task, sa_task]
    )