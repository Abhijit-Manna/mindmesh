from crewai import Task

from .agent import create_delivery_planner


def create_delivery_planner_task(
    business_analyst_output: str,
    solution_architect_output: str,
    technology_advisor_output: str,
    delivery_timeline_months: int,
) -> Task:

    agent = create_delivery_planner()

    description = f"""
Create the implementation and delivery plan for the system.

================ BUSINESS ANALYST OUTPUT ================

{business_analyst_output}

================ SOLUTION ARCHITECT OUTPUT ================

{solution_architect_output}

================ TECHNOLOGY ADVISOR OUTPUT ================

{technology_advisor_output}

================ DELIVERY CONSTRAINT ================

Maximum Delivery Timeline:
{delivery_timeline_months} months

================ REQUIRED OUTPUT ================

Create a delivery plan containing:

1. Delivery overview

2. Business/MVP scope and priorities

3. Implementation workstreams

For each workstream include:
- Name
- Expected outcomes
- Dependencies
- Months

4. Team and roles

For each role include:
- Role
- Responsibilities

5. Milestones

For each milestone include:
- Name
- Target month
- Exit criteria

6. Dependencies and prerequisites

7. Effort and complexity assessment

8. Testing and quality activities

9. Integration activities

10. Deployment and release activities

11. Delivery risks

12. Risk mitigations

13. Future evolution

================ IMPORTANT ================

The delivery timeline is a hard constraint.

All MVP milestones must fit within:
{delivery_timeline_months} months.

Do not extend the timeline.

If the proposed scope cannot fit within the timeline,
identify the scope conflict and explain what should be
deferred to future scope.

Return a structured Delivery Planner output.
"""

    return Task(
        description=description,
        expected_output=(
            "A structured delivery plan containing workstreams, "
            "team roles, milestones, dependencies, effort, "
            "testing, deployment, risks, mitigations, and "
            "future evolution."
        ),
        agent=agent,
    )