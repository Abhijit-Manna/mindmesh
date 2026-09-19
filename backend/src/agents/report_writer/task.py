from typing import Dict, Any, List, Optional
from crewai import Task

from .agent import create_report_writer


def create_report_writer_task(
    inputs: Dict[str, Any],
    ba_task: Task,
    sa_task: Task,
    ta_task: Task,
    dp_task: Task,
    do_task: Optional[Task] = None,
) -> Task:
    agent = create_report_writer()

    context_tasks = [ba_task, sa_task, ta_task, dp_task]
    if do_task:
        context_tasks.insert(3, do_task)

    description = f"""
Perform an Executive Architecture Synthesis and Cross-Discipline Harmonization for the entire solution.

================ USER CONSTRAINTS ================
Business Problem / Idea:
{inputs.get('business_idea', '').strip()}

Technology Preference: {inputs.get('technology_preference', 'N/A')}
Cloud Preference: {inputs.get('cloud_preference', 'N/A')}
Expected Daily Traffic: {inputs.get('expected_daily_traffic', 'N/A')}
Delivery Timeline: {inputs.get('delivery_timeline_months', 6)} Months
Data Hosting Country: {inputs.get('data_hosting_country', 'N/A')}

================ SPECIALIST DELIVERABLES ================
The complete deliverables of the Business Analyst, Solution Architect, Technology Advisor, DevOps Architect, and Delivery Planner are provided as task context.

================ DELIVERABLES REQUIRED ================
1. Executive Solution Overview & Strategic Business Value Narrative
2. Comprehensive Multi-Tier ASCII System Architecture Topology Diagram (Must be detailed, showing edge, gateway, services, caches, databases, queues, and third-party integrations)
3. Cross-Discipline Technical Consistency & Harmonization Audit
4. Data Residency, Security & Regulatory Compliance Verification (for {inputs.get('data_hosting_country', 'N/A')})
5. Total Cost of Ownership (TCO) & Cloud Sizing Recommendations

Provide deep, publication-grade analytical commentary and a clear ASCII architecture diagram.
"""

    return Task(
        description=description,
        expected_output=(
            "An executive-level Architectural Synthesis and Governance document containing "
            "an extensive multi-tier ASCII architecture diagram, technical consistency review, "
            "data residency verification, and TCO optimization strategies."
        ),
        agent=agent,
        context=context_tasks,
    )