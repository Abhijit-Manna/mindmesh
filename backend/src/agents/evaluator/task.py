from typing import Dict, Any
from crewai import Task

from .agent import create_evaluator


def create_evaluator_task(
    agent_role: str,
    agent_output: str,
    user_constraints: Dict[str, Any],
    threshold: float = 0.70,
) -> Task:
    agent = create_evaluator()

    description = f"""
Audit the deliverable produced by the '{agent_role}' against the user's explicit constraints and role requirements.

================ USER CONSTRAINTS ================
Business Idea: {user_constraints.get('business_idea', 'N/A')}
Technology Preference: {user_constraints.get('technology_preference', 'N/A')}
Cloud Preference: {user_constraints.get('cloud_preference', 'N/A')}
Expected Daily Traffic: {user_constraints.get('expected_daily_traffic', 'N/A')}
Delivery Timeline: {user_constraints.get('delivery_timeline_months', 'N/A')} months
Data Hosting Country: {user_constraints.get('data_hosting_country', 'N/A')}

================ DELIVERABLE TO AUDIT ({agent_role}) ================
{agent_output.strip()}

================ INSTRUCTIONS ================
1. Evaluate completeness, constraint adherence, grounding, and realism.
2. Calculate an overall score between 0.00 and 1.00.
3. Compare against acceptance threshold: {threshold:.2f}.
4. Return your evaluation strictly in the JSON format requested in your backstory.
"""

    return Task(
        description=description,
        expected_output="Valid JSON string containing score, passed, summary, strengths, critique, and remediation_guidance.",
        agent=agent,
    )