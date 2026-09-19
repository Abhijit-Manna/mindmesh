from crewai import Task

from .agent import create_devops_architect


def create_devops_architect_task(
    cloud_preference: str,
    data_hosting_country: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    ba_task: Task,
    sa_task: Task,
    ta_task: Task,
) -> Task:
    agent = create_devops_architect()

    description = f"""
Design a comprehensive, production-grade Cloud Infrastructure, CI/CD Pipeline, and Deployment Architecture.

================ CONSTRAINTS ================
Target Cloud Preference: {cloud_preference}
Data Hosting Country / Region: {data_hosting_country}
Expected Daily Traffic: {expected_daily_traffic}
Delivery Timeline: {delivery_timeline_months} months

================ DELIVERABLES REQUIRED ================
1. Cloud Infrastructure & Hosting Topology (Compute sizing, VPC/Subnet network segregation on {cloud_preference})
2. Infrastructure as Code (IaC) Framework & Modular Architecture (Terraform structure, state locking, environment segregation)
3. End-to-End Automated CI/CD Pipeline Workflow (Step-by-step pipeline: Lint -> SAST/Security -> Test -> Container Build -> Staging -> Prod)
4. Zero-Downtime Deployment & Database Migration Strategy (Blue/Green or Canary routing, expand/contract schema migration)
5. Comprehensive SRE Observability & Monitoring Baseline (Logging, Metrics, APM Tracing, Alerting thresholds table)
6. Backup, Disaster Recovery & High Availability Runbook (RTO, RPO, Automated snapshot schedules for {data_hosting_country})

Build directly upon the Solution Architect's topology and the Technology Advisor's stack choices. Provide rich, highly actionable engineering specifications.
"""

    return Task(
        description=description,
        expected_output=(
            "A comprehensive DevOps, Cloud Infrastructure, and SRE Engineering specification containing "
            "network and hosting topologies, Terraform modular architectures, step-by-step CI/CD automation pipelines, "
            "zero-downtime deployment strategies, and observability baselines."
        ),
        agent=agent,
        context=[ba_task, sa_task, ta_task],
    )