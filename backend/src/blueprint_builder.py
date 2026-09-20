import time
from typing import Any, Dict


def build_master_blueprint(
    inputs: Dict[str, Any],
    ba_output: str,
    sa_output: str,
    ta_output: str,
    dp_output: str,
    do_output: str = "",
    rw_output: str = "",
    run_id: str = "run_master",
) -> str:
    """
    Synthesize all individual specialist agent deliverables and executive synthesis
    into an exhaustive, publication-grade Enterprise Solution Blueprint.
    Preserves all technical depth, tables, diagrams, and trade-off analyses.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    # Format Executive Synthesis section from Report Writer if present
    executive_synthesis_section = ""
    if rw_output.strip():
        executive_synthesis_section = f"""
---

## Executive Architecture Synthesis & System Topology
*Synthesized by Lead Solution Consultant & Technical Writer*

{rw_output.strip()}
"""

    # Format DevOps section if present
    devops_section = ""
    if do_output.strip():
        devops_section = f"""
---

## Section 4: DevOps, Cloud Infrastructure & Deployment Architecture
*Synthesized by DevOps Architect Agent*

{do_output.strip()}
"""

    blueprint_md = f"""# MindMesh AI — Enterprise Solution Blueprint

> **System Blueprint ID:** `{run_id}`  
> **Generation Timestamp:** `{timestamp}`  
> **Target Cloud:** `{inputs.get('cloud_preference', 'N/A')}` | **Tech Stack:** `{inputs.get('technology_preference', 'N/A')}`  
> **Expected Scale:** `{inputs.get('expected_daily_traffic', 'N/A')}` | **Target Timeline:** `{inputs.get('delivery_timeline_months', 6)} Months` | **Residency:** `{inputs.get('data_hosting_country', 'N/A')}`

---

## Executive Problem Scope & Objectives
**Business Idea / Problem Statement:**
{inputs.get('business_idea', '').strip()}
{executive_synthesis_section}
---

## Section 1: Business Analysis & Functional Requirements
*Synthesized by Business Analyst Agent*

{ba_output.strip()}

---

## Section 2: High-Level Solution Architecture & Component Design
*Synthesized by Solution Architect Agent*

{sa_output.strip()}

---

## Section 3: Technology Stack & Architectural Trade-Offs
*Synthesized by Technology Advisor Agent*

{ta_output.strip()}
{devops_section}
---

## Section 5: Implementation Roadmap & Delivery Plan
*Synthesized by Delivery Planner Agent*

{dp_output.strip()}

---
*MindMesh Multi-Agent Engine • Autonomous Architecture Blueprinting*
"""
    return blueprint_md
