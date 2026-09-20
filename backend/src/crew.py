"""
MindMesh Multi-Agent Engine — Crew & Pipeline Module

Provides:
- `create_crew`: Standard sequential CrewAI crew definition with all specialist agents.
- Backward-compatible re-exports for pipeline execution, evaluation gates, and master blueprint synthesis.
"""

from typing import Any, Dict
from crewai import Crew, Process

from src.agents.business_analyst.task import create_business_analyst_task
from src.agents.solution_architect.task import create_solution_architect_task
from src.agents.technology_advisor.task import create_technology_advisor_task
from src.agents.delivery_planner.task import create_delivery_planner_task
from src.agents.report_writer.task import create_report_writer_task

# Re-exports for modular separation and backward compatibility
from src.evaluation import parse_evaluation_json, evaluate_agent_output
from src.blueprint_builder import build_master_blueprint
from src.pipeline import run_agents_step_by_step

__all__ = [
    "create_crew",
    "run_agents_step_by_step",
    "build_master_blueprint",
    "evaluate_agent_output",
    "parse_evaluation_json",
]


def create_crew(
    business_idea: str,
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
) -> Crew:
    """
    Create a standard CrewAI sequential crew assembling all specialized architecture agents.
    
    Agent pipeline sequence:
    1. Business Analyst (Scope, functional & non-functional requirements)
    2. Solution Architect (High-level architecture, components, data flows)
    3. Technology Advisor (Tech stack selection & architectural trade-offs)
    4. Delivery Planner (Implementation roadmap, milestones & risks)
    5. Report Writer (Executive architecture synthesis & blueprint compilation)
    """
    inputs: Dict[str, Any] = {
        "business_idea": business_idea,
        "technology_preference": technology_preference,
        "cloud_preference": cloud_preference,
        "expected_daily_traffic": expected_daily_traffic,
        "delivery_timeline_months": delivery_timeline_months,
        "data_hosting_country": data_hosting_country,
    }

    # 1. Business Analyst task
    ba_task = create_business_analyst_task(
        business_idea=business_idea,
        technology_preference=technology_preference,
        cloud_preference=cloud_preference,
        expected_daily_traffic=expected_daily_traffic,
        delivery_timeline_months=delivery_timeline_months,
        data_hosting_country=data_hosting_country,
    )

    # 2. Solution Architect task
    sa_task = create_solution_architect_task(
        technology_preference=technology_preference,
        cloud_preference=cloud_preference,
        expected_daily_traffic=expected_daily_traffic,
        delivery_timeline_months=delivery_timeline_months,
        data_hosting_country=data_hosting_country,
        ba_task=ba_task,
    )

    # 3. Technology Advisor task
    ta_task = create_technology_advisor_task(
        technology_preference=technology_preference,
        cloud_preference=cloud_preference,
        expected_daily_traffic=expected_daily_traffic,
        delivery_timeline_months=delivery_timeline_months,
        data_hosting_country=data_hosting_country,
        ba_task=ba_task,
        sa_task=sa_task,
    )

    # 4. Delivery Planner task
    dp_task = create_delivery_planner_task(
        delivery_timeline_months=delivery_timeline_months,
        ba_task=ba_task,
        sa_task=sa_task,
        ta_task=ta_task,
    )

    # 5. Report Writer task
    rw_task = create_report_writer_task(
        inputs=inputs,
        ba_task=ba_task,
        sa_task=sa_task,
        ta_task=ta_task,
        dp_task=dp_task,
    )

    crew = Crew(
        agents=[
            ba_task.agent,
            sa_task.agent,
            ta_task.agent,
            dp_task.agent,
            rw_task.agent,
        ],
        tasks=[
            ba_task,
            sa_task,
            ta_task,
            dp_task,
            rw_task,
        ],
        process=Process.sequential,
        verbose=True,
    )

    return crew