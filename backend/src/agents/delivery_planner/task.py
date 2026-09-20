from crewai import Task
from typing import Optional
from .agent import create_delivery_planner


def create_delivery_planner_task(
    delivery_timeline_months: int,
    ba_task: Task,
    sa_task: Task,
    ta_task: Task,
    relevant_experience: Optional[str] = None,
) -> Task:
    agent = create_delivery_planner()

    context_tasks = [ba_task, sa_task, ta_task]

    description = f"""
Create an exhaustive, production-ready Implementation and Delivery Plan for the system.

The Business Analyst, Solution Architect, and Technology Advisor deliverables
are provided as upstream context.

================ HARD CONSTRAINTS ================
Hard Delivery Timeline: {delivery_timeline_months} months (DO NOT EXCEED).
All MVP milestones, integration, and security testing must be completed within this window.

================ RELEVANT PAST EXPERIENCE ================

{relevant_experience or "No relevant previous experience is available."}

Use previous delivery experiences as reference material when planning
the current project.

Do not blindly copy previous timelines, staffing models, milestones,
or risk assumptions.

The current project's delivery timeline and all upstream Business
Analysis, Architecture, and Technology decisions take priority.

Pay particular attention to previously successful delivery patterns,
known delivery risks, evaluator feedback, and lessons learned.

================ DELIVERABLES REQUIRED ================
1. Delivery Methodology & Governance Framework (Scrum cadence, sprint structure, definition of done)
2. Comprehensive Workstreams & Epic Breakdown (Detailed table with Epics, Owners, and Durations)
3. Staffing Model & Team Topology (Roles, FTE allocations, skill profiles, and workstream alignment)
4. Milestone Schedule with Strict Entry & Exit Criteria (Months 1 through {delivery_timeline_months})
5. Critical Path Analysis & Pre-requisite Dependencies
6. Comprehensive Testing, QA & Load Testing Strategy (Targeting expected traffic load, security hardening)
7. Exhaustive Delivery Risk Register & Mitigation Strategy (Likelihood, Impact, Risk Score, Contingencies)
8. Post-MVP Evolution Roadmap

Build upon all upstream technical choices. Provide actionable, highly structured Markdown tables and deep operational planning.
"""

    return Task(
        description=description,
        expected_output=(
            "An exhaustive Delivery and Implementation Plan containing agile governance models, "
            "workstream breakdowns, staffing matrices, phase-by-phase milestone roadmaps with exit criteria, "
            "testing strategies, and a comprehensive risk register."
        ),
        agent=agent,
        context=context_tasks,
    )