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
Design a rigorous, production-ready high-level System Architecture for the
solution defined by the Business Analyst.

The Business Analyst deliverable is the authoritative business requirements
baseline. Use it as the source for business scope, user journeys, functional
requirements, NFRs, business rules, MVP boundaries, dependencies, and risks.

================ USER CONSTRAINTS ================

Technology Preference:
{technology_preference}

Cloud Infrastructure Preference:
{cloud_preference}

Expected Daily Traffic:
{expected_daily_traffic}

Delivery Timeline:
{delivery_timeline_months} months

Data Hosting Country / Region:
{data_hosting_country}

================ PREFERENCE SENSITIVITY RULE ================
The user’s stated technology, cloud, traffic, and residency preferences are
binding architectural constraints. If these inputs change even slightly, the
architecture, trade-offs, topology, security boundaries, and deployment model
must reflect that change. Do not treat cloud or technology preference as a
header-only field; make it visible in the design choices, operational trade-offs,
and implementation assumptions.

================ ARCHITECTURE OBJECTIVE ================

Translate the approved requirements into an implementable architecture.

The architecture must balance:
- business requirements
- MVP scope
- expected scale
- security and privacy
- reliability and resilience
- integration complexity
- data residency
- operational simplicity
- delivery timeline

Do not blindly choose the most complex architecture.
Do not introduce unnecessary distributed systems, services, or infrastructure.

Technology selection belongs primarily to the Technology Advisor. You may
describe technology-independent architectural capabilities and patterns, but
do not turn this task into a vendor/product selection exercise.

================ REQUIRED ANALYSIS ================

1. ARCHITECTURAL OBJECTIVE & PRINCIPLES

Explain:
- what the architecture must enable
- the most important architectural constraints
- the principles guiding the design
- what is intentionally optimized for the MVP
- what is deliberately deferred

2. ARCHITECTURE STYLE DECISION

Evaluate the viable architectural styles for this problem, such as:
- modular monolith
- service-oriented / modular services
- event-driven architecture
- microservices where justified

Compare relevant alternatives against the actual requirements using factors such
as:
- delivery speed
- engineering complexity
- operational burden
- scalability
- reliability
- security
- maintainability
- integration complexity
- team capability
- long-term evolution

Then document the selected architectural style and why it fits this project.

Do not manufacture alternatives that are not relevant.

3. COMPONENT TOPOLOGY

Define the major logical components and their responsibilities.

Use:

| Component | Responsibility | Inputs | Outputs | Dependencies | Trust / Data Boundary |

Explain why each major component exists and which requirements it supports.

Do not create components merely for organizational decoration.

4. END-TO-END REQUEST & DATA FLOWS

Describe the important runtime flows step by step.

Cover relevant:
- user-to-system requests
- API flows
- synchronous interactions
- asynchronous processing
- external integrations
- failure paths
- retries
- idempotency
- timeout handling
- long-running/background work

For important flows, explain:
1. trigger
2. entry point
3. components involved
4. data movement
5. persistence
6. downstream effects
7. response / completion behavior
8. failure and recovery behavior

5. DATA ARCHITECTURE & CONSISTENCY

Define the logical data architecture.

Explain:
- major data domains / entities
- ownership boundaries
- authoritative source of each important data set
- transactional boundaries
- consistency expectations
- read/write patterns
- caching requirements
- synchronization requirements
- auditability
- retention / deletion implications
- backup and recovery implications

Keep this implementation-independent where concrete database choices are
not yet required.

6. SECURITY & TRUST BOUNDARIES

Design the security architecture around the actual requirements.

Cover relevant:
- identity and authentication
- authorization
- service-to-service trust
- privileged access
- secret handling
- encryption boundaries
- sensitive-data protection
- audit logging
- threat boundaries
- least privilege
- abuse / fraud controls where relevant

Make security controls concrete enough for the Technology Advisor and Delivery
Planner to implement later.

7. DATA RESIDENCY & REGULATORY ARCHITECTURE

For the specified hosting country / region, explain:
- which data must remain within the jurisdiction
- where processing may occur
- what architectural boundaries are needed
- implications for backups, logs, analytics, integrations, and disaster recovery
- unresolved legal/compliance questions

Do not invent regulations. When a regulatory conclusion requires verification,
identify it as a research item or assumption.

8. SCALABILITY & CAPACITY DESIGN

Evaluate the stated traffic and scale requirements.

Explain:
- expected load characteristics
- likely bottlenecks
- horizontal vs. vertical scaling needs
- stateless/stateful boundaries
- caching strategy
- asynchronous workload isolation
- database scaling considerations
- rate limiting / backpressure where relevant
- capacity risks

Avoid unsupported precision. Use calculations only where the input supports
them.

9. RESILIENCE, FAILURE & RECOVERY

Define:
- single points of failure
- graceful degradation
- retry strategy
- timeout strategy
- circuit-breaking where justified
- queue/backlog handling
- failure isolation
- health checks
- failover
- backup/recovery expectations
- recovery considerations

Explain what happens when critical dependencies fail.

10. INTEGRATION ARCHITECTURE

For important external systems, define:
- integration boundary
- protocol/interface type where known
- data exchanged
- ownership
- synchronous vs asynchronous behavior
- authentication/trust model
- failure handling
- retry/idempotency expectations
- dependency risks

Do not invent integrations that are not supported by the Business Analyst
requirements.

11. DEPLOYMENT TOPOLOGY

Describe the logical deployment model across:
- development
- test/staging
- production

Explain:
- application boundaries
- network/security boundaries
- external services
- configuration/secrets
- observability
- scaling boundaries
- deployment dependencies
- environment isolation

Keep concrete cloud-product mapping for the Technology Advisor unless already
required by user constraints.

12. ARCHITECTURE TRADE-OFFS & DEFERRED PATTERNS

Explicitly document important trade-offs.

For each major architectural decision, explain:
- decision
- reason
- benefit
- cost / drawback
- requirement supported
- risk introduced
- mitigation

Also document architecture patterns deliberately NOT used for the MVP and why.

Examples may include:
- unnecessary microservices
- service mesh
- excessive event choreography
- multi-region active-active
- polyglot persistence
- premature platform engineering

Only mention patterns that are relevant to the actual solution.

13. ARCHITECTURE VALIDATION

Challenge the proposed architecture before finalizing it.

Check it against:
- Business Analyst requirements
- MVP scope
- traffic / scale
- delivery timeline
- security requirements
- data residency
- integration complexity
- operational burden
- team feasibility

Identify contradictions, bottlenecks, missing dependencies, and assumptions.

Where something cannot be resolved from the current requirements, state the
open question instead of inventing an answer.

================ AUTHORITATIVE MERMAID DIAGRAM ================

Produce exactly ONE high-level authoritative architecture diagram.

Requirements:
- valid Mermaid syntax
- must start with `flowchart TD`
- show the major logical components
- show important relationships and major data/request flows
- remain consistent with the written architecture
- do not use ASCII art
- do not generate an image

The Mermaid diagram represents the authoritative system topology.

================ AUTHORING RULES ================

The architecture document must be detailed and decision-oriented.

Explain the "what, why, and how" of important architectural choices.

Do not:
- choose specific programming languages unless explicitly required
- choose specific databases or vendors as the primary task
- redesign the business scope
- ignore the stated timeline
- invent unsupported requirements
- add complexity without justification

Prefer concrete architecture explanations, responsibility tables, flow
descriptions, and explicit trade-offs over generic architecture vocabulary.
Do not produce a short summary; the architecture must be materially detailed so
that the Technology Advisor and Delivery Planner can implement it without
reconstructing design decisions.

The final architecture must be realistic for the stated MVP and should provide a
clear foundation for the Technology Advisor and Delivery Planner.
"""

    return Task(
        description=description,
        expected_output=(
            "A rigorous System Architecture Blueprint covering architectural "
            "style and trade-offs, component topology and responsibilities, "
            "step-by-step request and data flows, logical data architecture and "
            "consistency, security and trust boundaries, data residency, "
            "scalability and resilience, integration architecture, deployment "
            "topology, deferred architecture patterns, validation findings, "
            "and exactly one valid authoritative Mermaid flowchart TD diagram. "
            "This should be a substantial, implementation-ready architecture, not a brief "
            "summary. The architecture must be traceable to the Business Analyst "
            "requirements and realistic for the stated traffic and delivery "
            "timeline. It must explicitly reflect the user’s technology, cloud, "
            "data residency, and scale preferences, and any change in those inputs "
            "must change the architecture reasoning and trade-offs accordingly."
        ),
        agent=agent,
        context=[ba_task],
    )