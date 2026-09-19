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
Design a comprehensive, production-grade System Architecture Blueprint based on the Business Analyst requirements.

================ USER CONSTRAINTS ================
Technology Preference: {technology_preference}
Cloud Infrastructure Preference: {cloud_preference}
Expected Daily Traffic: {expected_daily_traffic}
Delivery Timeline: {delivery_timeline_months} months
Data Hosting Country / Region: {data_hosting_country}

================ DELIVERABLES REQUIRED ================
1. Architectural Style & Design Rationale (Modular Monolith / Microservices / Event-Driven)
2. Core Component Topology & Responsibility Matrix (Table format)
3. Step-by-Step Data Flow & Request Lifecycles (Synchronous APIs & Asynchronous pipelines)
4. Storage, Cache & Data Consistency Model
5. Security Perimeter, IAM & Data Residency Controls (for {data_hosting_country})
6. Resilience, Scalability & Failover Patterns (handling {expected_daily_traffic})
7. Detailed High-Level ASCII System Architecture Diagram (clear, clean text diagram)
8. Over-Engineering Safeguards & Deferred Architecture Patterns

Build strictly upon the Business Analyst's requirements. Maintain high technical depth and architectural clarity.
"""

    return Task(
        description=description,
        expected_output=(
            "A comprehensive System Architecture Blueprint containing detailed component topologies, "
            "step-by-step data flows, security and data residency controls, resilience patterns, "
            "and a clear ASCII system architecture diagram."
        ),
        agent=agent,
        context=[ba_task]
    )