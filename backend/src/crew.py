from crewai import Crew, Process

from backend.src.agents.business_analyst.task import create_business_analyst_task
from backend.src.agents.solution_architect.task import create_solution_architect_task
from backend.src.agents.technology_advisor.task import create_technology_advisor_task
from backend.src.agents.delivery_planner.task import create_delivery_planner_task


def create_crew(
    business_idea: str,
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
):

    # 1. Create Business Analyst task
    ba_task = create_business_analyst_task(
        business_idea=business_idea,
        technology_preference=technology_preference,
        cloud_preference=cloud_preference,
        expected_daily_traffic=expected_daily_traffic,
        delivery_timeline_months=delivery_timeline_months,
        data_hosting_country=data_hosting_country,
    )

    # 2. Create Solution Architect task
    # SA receives BA output through context
    sa_task = create_solution_architect_task(
        technology_preference=technology_preference,
        cloud_preference=cloud_preference,
        expected_daily_traffic=expected_daily_traffic,
        delivery_timeline_months=delivery_timeline_months,
        data_hosting_country=data_hosting_country,
        ba_task=ba_task,
    )

    # 3. Create Technology Advisor task
    # TA receives BA + SA outputs through context
    ta_task = create_technology_advisor_task(
        technology_preference=technology_preference,
        cloud_preference=cloud_preference,
        expected_daily_traffic=expected_daily_traffic,
        delivery_timeline_months=delivery_timeline_months,
        data_hosting_country=data_hosting_country,
        ba_task=ba_task,
        sa_task=sa_task,
    )

    # 4. Create Delivery Planner task
    # DP receives BA + SA + TA outputs through context
    dp_task = create_delivery_planner_task(
        delivery_timeline_months=delivery_timeline_months,
        ba_task=ba_task,
        sa_task=sa_task,
        ta_task=ta_task,
    )

    # 5. Create the Crew
    crew = Crew(
        agents=[
            ba_task.agent,
            sa_task.agent,
            ta_task.agent,
            dp_task.agent,
        ],
        tasks=[
            ba_task,
            sa_task,
            ta_task,
            dp_task,
        ],
        process=Process.sequential,
        verbose=True,
    )

    return crew