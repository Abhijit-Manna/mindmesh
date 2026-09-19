import asyncio
import time
from typing import AsyncGenerator, Dict, Any, Optional
from crewai import Crew, Process

from src.agents.business_analyst.task import create_business_analyst_task
from src.agents.solution_architect.task import create_solution_architect_task
from src.agents.technology_advisor.task import create_technology_advisor_task
from src.agents.delivery_planner.task import create_delivery_planner_task
from src.utils.html_converter import markdown_to_html


def build_master_blueprint(
    inputs: Dict[str, Any],
    ba_output: str,
    sa_output: str,
    ta_output: str,
    dp_output: str,
    run_id: str = "run_master"
) -> str:
    """
    Synthesize the individual agent outputs into a unified, executive-grade Master Blueprint.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    
    blueprint_md = f"""# MindMesh AI — Enterprise Solution Blueprint

> **System Blueprint ID:** `{run_id}`  
> **Generation Timestamp:** `{timestamp}`  
> **Target Cloud:** `{inputs.get('cloud_preference', 'N/A')}` | **Tech Stack:** `{inputs.get('technology_preference', 'N/A')}`  
> **Expected Scale:** `{inputs.get('expected_daily_traffic', 'N/A')}` | **Target Timeline:** `{inputs.get('delivery_timeline_months', 6)} Months` | **Residency:** `{inputs.get('data_hosting_country', 'N/A')}`

---

## Executive Summary & Problem Scope
**Business Idea:**
{inputs.get('business_idea', '').strip()}

---

## Section 1: Business Analysis & Functional Requirements
*Synthesized by Business Analyst Agent*

{ba_output.strip()}

---

## Section 2: High-Level Solution Architecture
*Synthesized by Solution Architect Agent*

{sa_output.strip()}

---

## Section 3: Technology Stack & Architectural Trade-Offs
*Synthesized by Technology Advisor Agent*

{ta_output.strip()}

---

## Section 4: Implementation Roadmap & Delivery Plan
*Synthesized by Delivery Planner Agent*

{dp_output.strip()}

---
*MindMesh Multi-Agent Engine • Autonomous Architecture Blueprinting*
"""
    return blueprint_md


def create_crew(
    business_idea: str,
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
) -> Crew:
    """
    Create standard CrewAI sequential crew.
    """
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
    sa_task = create_solution_architect_task(
        technology_preference=technology_preference,
        cloud_preference=cloud_preference,
        expected_daily_traffic=expected_daily_traffic,
        delivery_timeline_months=delivery_timeline_months,
        data_hosting_country=data_hosting_country,
        ba_task=ba_task,
    )

    # 3. Create Technology Advisor task
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
    dp_task = create_delivery_planner_task(
        delivery_timeline_months=delivery_timeline_months,
        ba_task=ba_task,
        sa_task=sa_task,
        ta_task=ta_task,
    )

    # 5. Create Crew
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


async def run_agents_step_by_step(
    inputs: Dict[str, Any],
    run_id: str
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Executes agents one by one sequentially, yielding real-time SSE event dictionaries.
    """
    business_idea = inputs.get("business_idea", "")
    technology_preference = inputs.get("technology_preference", "")
    cloud_preference = inputs.get("cloud_preference", "")
    expected_daily_traffic = inputs.get("expected_daily_traffic", "")
    delivery_timeline_months = int(inputs.get("delivery_timeline_months", 6))
    data_hosting_country = inputs.get("data_hosting_country", "")

    yield {
        "event": "init",
        "run_id": run_id,
        "message": "Initialized autonomous multi-agent pipeline.",
        "progress": 5
    }

    # -------------------------------------------------------------
    # STEP 1: BUSINESS ANALYST
    # -------------------------------------------------------------
    yield {
        "event": "agent_start",
        "agent": "Business Analyst",
        "step": 1,
        "total": 4,
        "role": "Requirements & MVP Scope Analyst",
        "message": "Analyzing business idea, identifying stakeholders, non-functional requirements, and core MVP scope...",
        "progress": 10
    }

    ba_task = create_business_analyst_task(
        business_idea=business_idea,
        technology_preference=technology_preference,
        cloud_preference=cloud_preference,
        expected_daily_traffic=expected_daily_traffic,
        delivery_timeline_months=delivery_timeline_months,
        data_hosting_country=data_hosting_country,
    )

    # Execute BA
    ba_crew = Crew(agents=[ba_task.agent], tasks=[ba_task], verbose=True)
    ba_res = await asyncio.to_thread(ba_crew.kickoff)
    ba_output = ba_res.raw if hasattr(ba_res, "raw") else str(ba_res)

    yield {
        "event": "agent_complete",
        "agent": "Business Analyst",
        "step": 1,
        "total": 4,
        "output": ba_output,
        "message": "Business analysis and functional requirements established.",
        "progress": 30
    }

    # -------------------------------------------------------------
    # STEP 2: SOLUTION ARCHITECT
    # -------------------------------------------------------------
    yield {
        "event": "agent_start",
        "agent": "Solution Architect",
        "step": 2,
        "total": 4,
        "role": "System & Component Architect",
        "message": "Designing component interaction diagrams, data flows, scalability patterns, and security perimeter...",
        "progress": 35
    }

    sa_task = create_solution_architect_task(
        technology_preference=technology_preference,
        cloud_preference=cloud_preference,
        expected_daily_traffic=expected_daily_traffic,
        delivery_timeline_months=delivery_timeline_months,
        data_hosting_country=data_hosting_country,
        ba_task=ba_task,
    )

    sa_crew = Crew(agents=[sa_task.agent], tasks=[sa_task], verbose=True)
    sa_res = await asyncio.to_thread(sa_crew.kickoff)
    sa_output = sa_res.raw if hasattr(sa_res, "raw") else str(sa_res)

    yield {
        "event": "agent_complete",
        "agent": "Solution Architect",
        "step": 2,
        "total": 4,
        "output": sa_output,
        "message": "High-level architecture and system components finalized.",
        "progress": 55
    }

    # -------------------------------------------------------------
    # STEP 3: TECHNOLOGY ADVISOR
    # -------------------------------------------------------------
    yield {
        "event": "agent_start",
        "agent": "Technology Advisor",
        "step": 3,
        "total": 4,
        "role": "Technology Stack & Cloud Advisor",
        "message": "Evaluating technology stack trade-offs, databases, cloud infrastructure, and CI/CD pipelines...",
        "progress": 60
    }

    ta_task = create_technology_advisor_task(
        technology_preference=technology_preference,
        cloud_preference=cloud_preference,
        expected_daily_traffic=expected_daily_traffic,
        delivery_timeline_months=delivery_timeline_months,
        data_hosting_country=data_hosting_country,
        ba_task=ba_task,
        sa_task=sa_task,
    )

    ta_crew = Crew(agents=[ta_task.agent], tasks=[ta_task], verbose=True)
    ta_res = await asyncio.to_thread(ta_crew.kickoff)
    ta_output = ta_res.raw if hasattr(ta_res, "raw") else str(ta_res)

    yield {
        "event": "agent_complete",
        "agent": "Technology Advisor",
        "step": 3,
        "total": 4,
        "output": ta_output,
        "message": "Technology recommendations and trade-off analysis completed.",
        "progress": 80
    }

    # -------------------------------------------------------------
    # STEP 4: DELIVERY PLANNER
    # -------------------------------------------------------------
    yield {
        "event": "agent_start",
        "agent": "Delivery Planner",
        "step": 4,
        "total": 4,
        "role": "Delivery Roadmap & Milestones Planner",
        "message": "Synthesizing delivery workstreams, sprint milestones, team allocation, and risk mitigations...",
        "progress": 85
    }

    dp_task = create_delivery_planner_task(
        delivery_timeline_months=delivery_timeline_months,
        ba_task=ba_task,
        sa_task=sa_task,
        ta_task=ta_task,
    )

    dp_crew = Crew(agents=[dp_task.agent], tasks=[dp_task], verbose=True)
    dp_res = await asyncio.to_thread(dp_crew.kickoff)
    dp_output = dp_res.raw if hasattr(dp_res, "raw") else str(dp_res)

    yield {
        "event": "agent_complete",
        "agent": "Delivery Planner",
        "step": 4,
        "total": 4,
        "output": dp_output,
        "message": "Delivery roadmap, milestones, and risk register complete.",
        "progress": 95
    }

    # -------------------------------------------------------------
    # SYNTHESIZE MASTER BLUEPRINT
    # -------------------------------------------------------------
    master_md = build_master_blueprint(
        inputs=inputs,
        ba_output=ba_output,
        sa_output=sa_output,
        ta_output=ta_output,
        dp_output=dp_output,
        run_id=run_id
    )

    master_html = markdown_to_html(master_md, title=f"MindMesh Blueprint - {run_id}")

    yield {
        "event": "complete",
        "run_id": run_id,
        "status": "completed",
        "progress": 100,
        "markdown": master_md,
        "html": master_html,
        "sections": {
            "business_analyst": ba_output,
            "solution_architect": sa_output,
            "technology_advisor": ta_output,
            "delivery_planner": dp_output,
        }
    }