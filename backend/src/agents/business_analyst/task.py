from crewai import Task

from .agent import create_business_analyst


def create_business_analyst_task(
    business_idea: str,
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
) -> Task:
    agent = create_business_analyst()

    description = f"""
Perform a rigorous Business Analysis and Requirements Specification for this initiative.

================ USER INPUTS ================

Business Idea:
{business_idea}

Technology Preference:
{technology_preference}

Cloud Preference:
{cloud_preference}

Expected Daily Traffic:
{expected_daily_traffic}

Delivery Timeline:
{delivery_timeline_months} months

Data Hosting Country / Region:
{data_hosting_country}

================ ANALYSIS OBJECTIVE ================

Translate the business idea and constraints into an implementation-independent
requirements baseline that downstream architecture, technology, and delivery
teams can use without having to rediscover the business problem.

Research the business/domain context when useful. Distinguish:
- user-provided facts
- researched facts
- reasonable assumptions
- unresolved questions

Do not invent unsupported facts.

================ REQUIRED DELIVERABLES ================

1. EXECUTIVE BUSINESS PROBLEM & VALUE

Explain:
- the problem being solved
- why it matters
- who experiences the problem
- proposed business value
- expected outcomes
- measurable success indicators / KPIs

2. BUSINESS CONTEXT & STAKEHOLDERS

Explain the relevant business/domain context and identify the important
stakeholders and user groups.

Use a table such as:

| Stakeholder / Persona | Goals & Needs | Pain Points | Key Responsibilities | System Interactions |

Include the primary users plus important operational, business, compliance,
or administrative stakeholders where relevant.

3. USER JOURNEYS & BUSINESS WORKFLOWS

Describe the most important end-to-end user journeys.

For each important journey, explain:
- trigger
- actor
- major steps
- business decisions/rules
- expected outcome
- important exceptions or failure cases

Use tables or structured flows where they improve clarity.

4. FUNCTIONAL REQUIREMENTS

Create a detailed requirements matrix.

Use:

| ID | Capability / Requirement | Business Purpose | User / Actor | Description | Priority | Acceptance Criteria | Dependencies |

Requirements must be concrete enough for downstream teams to understand what
the system must enable.

Include important business rules, validation rules, permissions, workflows,
notifications, approvals, reporting, integrations, and exception handling when
relevant.

Do not collapse major capabilities into vague one-line feature names.

5. NON-FUNCTIONAL REQUIREMENTS

Define the important NFRs using measurable targets where the inputs support them.

Cover relevant areas including:
- performance and latency
- throughput / concurrency
- availability
- scalability
- security
- privacy
- compliance
- data residency / sovereignty
- auditability
- backup / recovery expectations
- observability
- usability / accessibility where relevant

Derive scale-related targets from the stated traffic constraint when possible,
but do not fabricate false precision.

Clearly distinguish:
- explicit user constraints
- derived engineering targets
- assumptions requiring validation

6. MVP SCOPE BOUNDARY

Define a defensible MVP boundary that fits the stated delivery timeline.

Use:

| Capability | MVP / Deferred / Out of Scope | Why | Business Value | Timeline / Dependency Implication |

Explain:
- what must be included
- what can be deferred
- what should remain out of scope
- what scope decisions are driven by the timeline
- what prerequisites could change the MVP boundary

Do not silently treat the entire business idea as MVP scope.

7. BUSINESS / PRODUCT APPROACH COMPARISONS

Where meaningful, compare viable business or product approaches before
settling on the recommended direction.

Examples:
- build vs. partner
- centralized vs. delegated operating model
- phased rollout vs. broad initial launch
- manual fallback vs. full automation
- narrow MVP vs. broad MVP

For each comparison, explain:
- approach
- benefits
- drawbacks
- operational implications
- delivery implications
- conditions under which it makes sense

Do not manufacture alternatives merely to create a comparison.

8. BUSINESS DATA & INFORMATION NEEDS

Identify:
- important business entities
- important data captured/generated
- ownership of business data
- data relationships
- retention needs
- reporting / analytics needs
- audit requirements
- sensitive or regulated information

Remain implementation-independent. Do not choose databases or technologies.

9. INTEGRATIONS & EXTERNAL DEPENDENCIES

Identify important:
- third-party systems
- partner dependencies
- regulatory/compliance dependencies
- external data sources
- identity/payment/communication integrations where relevant
- contractual or operational dependencies

For each important dependency, explain why it matters and what happens if it
is unavailable or delayed.

10. ASSUMPTIONS, CONSTRAINTS & RISKS

Use:

| ID | Assumption / Constraint / Risk | Category | Impact | Likelihood | Mitigation / Response |

Cover meaningful business, scope, adoption, operational, regulatory, data,
integration, and timeline risks.

11. OPEN DISCOVERY QUESTIONS

Identify the unresolved questions that could materially affect:
- business scope
- MVP
- requirements
- compliance
- integrations
- user workflows
- delivery feasibility

Prioritize the questions that should be answered before engineering commitments
are finalized.

12. DOWNSTREAM HANDOFF

Conclude with the key decisions and constraints that the Solution Architect,
Technology Advisor, and Delivery Planner must preserve.

Explicitly surface:
- mandatory requirements
- critical NFRs
- important business rules
- MVP boundaries
- important dependencies
- major risks
- unresolved decisions

================ AUTHORING RULES ================

Write a detailed, professional requirements document.

Prefer:
- concrete explanations over generic language
- tables where they improve traceability
- explicit acceptance criteria
- measurable requirements where justified
- clear separation between facts, assumptions, and open questions

Do NOT:
- choose programming languages
- choose frameworks
- choose databases
- choose cloud services
- design the system architecture
- invent unsupported regulatory requirements
- invent precise metrics without a basis

The result must be detailed enough that an architect and delivery planner can
use it as a reliable business baseline without reconstructing the analysis.
"""

    return Task(
        description=description,
        expected_output=(
            "A rigorous, enterprise-grade Business Analysis and Requirements Specification "
            "covering business problem and value, business context, stakeholders/personas, "
            "important user journeys, detailed functional requirements with acceptance "
            "criteria and priorities, quantified NFRs, a defensible MVP boundary, meaningful "
            "business/product approach comparisons, business data needs, integrations and "
            "dependencies, risks, assumptions, open discovery questions, and a clear "
            "downstream handoff. The document must remain implementation-independent and "
            "must distinguish facts, assumptions, and unresolved questions."
        ),
        agent=agent,
    )