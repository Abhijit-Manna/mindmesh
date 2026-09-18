from crewai import Task

from .agent import create_business_analyst


def create_business_analyst_task(
    business_idea: str,
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
) -> Task:
    """
    Create the Business Analyst task using the user's
    business requirements and constraints.
    """

    agent = create_business_analyst()

    description = f"""
Analyze the following business request and produce the
Business Analyst output according to the required contract.

BUSINESS IDEA:
{business_idea}

TECHNOLOGY PREFERENCE:
{technology_preference}

CLOUD PREFERENCE:
{cloud_preference}

EXPECTED DAILY TRAFFIC:
{expected_daily_traffic}

DELIVERY TIMELINE:
{delivery_timeline_months} months

DATA HOSTING COUNTRY:
{data_hosting_country}

Use these inputs as explicit business constraints.

Identify:
- Users and stakeholders
- Functional requirements
- Non-functional requirements
- MVP scope
- Future scope
- Assumptions
- Constraints
- Risks
- Open questions
- Priority rationale

Do not select specific technologies or make technology recommendations.
The Technology Advisor will handle technology selection later.

Return the result in the required structured Business Analyst format.
"""

    return Task(
        description=description,
        expected_output=(
            "A structured Business Analyst output containing users and "
            "stakeholders, functional requirements, non-functional "
            "requirements, MVP scope, future scope, assumptions, "
            "constraints, risks, open questions, and sources."
        ),
        agent=agent,
    )