from crewai import Task
from typing import Optional
from .agent import create_solution_architect


def create_solution_architect_task(
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
    ba_task: Task,
    relevant_experience: Optional[str] = None,
) -> Task:
    agent = create_solution_architect()

    description = f"""
Design a comprehensive, production-grade System Architecture Blueprint based on the Business Analyst requirements.

================ USER CONSTRAINTS ================
Technology Preference: {technology_preference}
Cloud Infrastructure Preference: {cloud_preference}
Expected Daily Traffic: {expected_daily_traffic}
Delivery Timeline: {delivery_timeline_months} months
Data Hosting Country / Region: {data_hosting_country}

================ RELEVANT PAST EXPERIENCE ================

{relevant_experience or "No relevant previous experience is available."}

Use these previous experiences as reference material for architectural
reasoning. Do not blindly copy a previous architecture.

The current user's requirements and constraints always take priority.
If a previous experience conflicts with the Business Analyst requirements
or current user constraints, do not follow it.

================ DELIVERABLES REQUIRED ================
1. Architectural Style & Design Rationale (Modular Monolith / Microservices / Event-Driven)
2. Core Component Topology & Responsibility Matrix (Table format)
3. Step-by-Step Data Flow & Request Lifecycles (Synchronous APIs & Asynchronous pipelines)
4. Storage, Cache & Data Consistency Model
5. Security Perimeter, IAM & Data Residency Controls (for {data_hosting_country})
6. Resilience, Scalability & Failover Patterns (handling {expected_daily_traffic})
7. Detailed High-Level Mermaid System Architecture Diagram
   - Use valid Mermaid syntax.
   - Start with `flowchart TD`.
   - Show the major components and their connections.
   - Show important request/data flows.
      - Keep the diagram consistent with the architecture.
   - Revalidate every Mermaid node and connection yourself; do not copy Mermaid syntax from past experiences without checking it.
   - Quote node labels that contain parentheses, brackets, colons, slashes, hyphens, or other special characters.
   - Example: use `Redis["Redis (In-Memory Cache)"]` instead of `Redis[Redis (In-Memory Cache)]`.
   - Do NOT generate ASCII art.
   - Do NOT generate an image.
   - Return valid Mermaid syntax for this section.
8. Over-Engineering Safeguards & Deferred Architecture Patterns

Build strictly upon the Business Analyst's requirements. Maintain high technical depth and architectural clarity.
"""

    return Task(
        description=description,
        expected_output=(
            "A comprehensive System Architecture Blueprint containing detailed component topologies, "
            "step-by-step data flows, security and data residency controls, resilience patterns, "
            "and a valid Mermaid architecture diagram using flowchart TD syntax."
        ),
        agent=agent,
        context=[ba_task]
    )