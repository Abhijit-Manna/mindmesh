from crewai import Task

from .agent import create_solution_architect


def create_solution_architect_task(
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
    ba_task: Task,
) -> Task:
    agent = create_solution_architect()

    description = f"""
Design the high-level architecture for the following system.
The Business Analyst output will be provided as task context.
Use the BA output as the source of business requirements.

================ USER CONSTRAINTS ================

Technology Preference:
{technology_preference}

Cloud Preference:
{cloud_preference}

Expected Daily Traffic:
{expected_daily_traffic}

Delivery Timeline:
{delivery_timeline_months} months

Data Hosting Country:
{data_hosting_country}

================ REQUIRED ANALYSIS ================

Identify:

- Major system components
- Responsibilities of each component
- Communication between components
- Main data flows
- External integrations
- Security considerations
- Scalability considerations
- Reliability considerations
- MVP architecture
- Future architecture improvements

Keep the architecture realistic for the requested timeline.

Return a structured Solution Architect output.
"""

    return Task(
        description=description,
        expected_output=(
            "A structured high-level architecture containing system "
            "components, responsibilities, communication flows, "
            "data flows, integrations, security, scalability, "
            "reliability, and MVP/future architecture."
        ),
        agent=agent,
        context=[ba_task]
    )