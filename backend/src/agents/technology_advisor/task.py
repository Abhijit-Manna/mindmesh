from crewai import Task

from .agent import create_technology_advisor


def create_technology_advisor_task(
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
    ba_task: Task,
    sa_task: Task,
) -> Task:

    agent = create_technology_advisor()

    description = f"""
Recommend the technology stack for the system.

The Business Analyst and Solution Architect outputs
will be provided as task context.

Use both outputs when making technology recommendations.

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

Recommend:

- Backend technology
- Frontend technology
- Database
- Cache
- Authentication
- APIs
- Messaging/event system if required
- Infrastructure
- Cloud services
- Monitoring
- Logging
- Testing
- Deployment

For each recommendation explain:

1. What it is
2. Why it is suitable
3. Which requirement it addresses
4. Any important trade-offs

Keep the recommended stack practical for the MVP.

Return a structured Technology Advisor output.
"""

    return Task(
        description=description,
        expected_output=(
            "A structured technology stack with recommendations, "
            "justifications, requirement mappings, and trade-offs."
        ),
        agent=agent,
        context=[ba_task, sa_task],
    )