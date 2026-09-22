from typing import Dict, Any

from crewai import Task

from .agent import create_evaluator


def create_evaluator_task(
    agent_role: str,
    agent_output: str,
    user_constraints: Dict[str, Any],
    threshold: float = 0.70,
    upstream_context: str = "",
) -> Task:
    agent = create_evaluator()

    normalized_role = str(agent_role or "").strip().lower()

    role_guidance = {
        "business analyst": """
Evaluate the Business Analyst deliverable against its requirements-analysis
responsibilities.

Check:
- business problem and value
- stakeholders/personas
- user journeys
- functional requirements
- acceptance criteria
- NFRs
- MVP boundary
- business rules/data needs
- dependencies
- assumptions and risks
- open questions
- downstream handoff

Fail a Business Analyst output when it collapses into a short executive summary
without the required requirements depth, traceability, acceptance criteria,
assumptions, and MVP boundary detail.

Do not penalize the BA for not selecting implementation technologies.
""",

        "solution architect": """
Evaluate the Solution Architect deliverable against its architecture
responsibilities.

Check:
- architectural rationale
- requirements-to-architecture traceability
- architecture style
- component boundaries/responsibilities
- request/data flows
- data boundaries and consistency
- security/trust boundaries
- scalability/resilience
- integrations
- deployment topology
- architecture trade-offs
- deferred architecture patterns
- one valid authoritative Mermaid architecture diagram

Fail a Solution Architect output when it is little more than a diagram or a brief
summary without detailed component responsibilities, flows, security, resilience,
trade-offs, and deployment rationale.

Do not require concrete vendor/product selections.
""",

        "technology advisor": """
Evaluate the Technology Advisor deliverable against its technology-selection
responsibilities.

Check:
- authoritative technology stack
- architecture-to-technology fit
- backend/application choices
- database/cache/messaging
- cloud mapping
- security/observability tooling
- alternatives and trade-offs
- licensing/vendor considerations
- scalability/performance
- developer toolchain
- technology risks
- final decisions

Fail a Technology Advisor output when it reduces to a short list of tools without
real rationale, trade-offs, architecture fit, or operational implications.

The technology stack must implement the approved architecture rather than
silently redesigning it. Any mismatch with the user's explicitly stated
technology preference, cloud preference, data residency, or traffic assumptions
should be treated as a material deficiency.
""",

        "delivery planner": """
Evaluate the Delivery Planner deliverable against its delivery responsibilities.

Check:
- delivery methodology/governance
- MVP-to-work mapping
- implementation workstreams
- concrete activities
- staffing and role allocation
- staffing feasibility
- phase plan
- sprint/iteration sequencing
- dependencies
- critical path
- effort/complexity
- testing and QA
- security/production readiness
- deployment/go-live
- delivery risks
- post-MVP evolution

Fail a Delivery Planner output when it is only a high-level roadmap with no
real workstreams, dependencies, staffing logic, quality gates, or production
readiness plan.

The plan must fit within the hard delivery timeline. A plan that ignores the
user’s stated technology, cloud, traffic, or residency preferences should be
scored down as a constraint-violation, even if it is otherwise polished.
""",

        "report writer": """
Evaluate the Report Writer against the final Enterprise Solution Blueprint
requirements.

Check:
- all 14 core sections are present
- sections are substantively developed
- important upstream requirements are preserved
- architecture decisions are preserved
- technology decisions and trade-offs are preserved
- workstreams are concrete
- staffing and role distribution are meaningful
- timeline and sequencing are realistic
- dependencies and critical path are meaningful
- effort/complexity is explained
- testing is execution-oriented
- security and production readiness are substantive
- deployment/release is substantive
- risks have meaningful mitigation/contingency
- future evolution is meaningful
- assumptions/open questions are explicit
- architecture prose explains components, flows, data, security, resilience,
  integrations, and deployment
- exactly one authoritative architecture diagram is retained
- supporting diagrams, when present, are useful and non-competing
- the final document is a coherent integrated proposal rather than a compressed
  summary of the specialist reports

Do not reward brevity merely because the document is concise.
Do not allow important upstream detail to be discarded merely to shorten the
document.
Do not invent unsupported decisions or facts.
""",
    }.get(
        normalized_role,
        """
Evaluate the deliverable against the responsibilities implied by the stated
agent role, the user constraints, and the general quality standard.
""",
    )

    description = f"""
Evaluate the following deliverable produced by:

AGENT ROLE:
{agent_role}

================ USER CONSTRAINTS ================

Business Idea:
{user_constraints.get("business_idea", "N/A")}

Technology Preference:
{user_constraints.get("technology_preference", "N/A")}

Cloud Preference:
{user_constraints.get("cloud_preference", "N/A")}

Expected Daily Traffic:
{user_constraints.get("expected_daily_traffic", "N/A")}

Delivery Timeline:
{user_constraints.get("delivery_timeline_months", "N/A")} months

Data Hosting Country:
{user_constraints.get("data_hosting_country", "N/A")}

These constraints are authoritative.

================ ROLE-SPECIFIC CHECKS ================

{role_guidance}

================ DELIVERABLE TO AUDIT ================

{str(agent_output or "").strip()}

================ UPSTREAM CONTEXT ================

{upstream_context.strip() or "No upstream context is applicable for this role."}

================ EVALUATION METHOD ================

Evaluate in this order:

1. Completeness
2. Depth and specificity
3. Constraint adherence
4. Internal consistency
5. Grounding in provided inputs/upstream work
6. Realism for the stated scope, scale, and timeline
7. Compliance with the agent's assigned responsibility

When information is missing from the inputs, do not punish the agent merely for
not knowing it. Check whether the agent:
- identifies the uncertainty
- makes a reasonable assumption where appropriate
- explains the impact
- raises an appropriate open question

Distinguish:
- minor weakness
- meaningful deficiency
- critical deficiency

A critical deficiency should normally cause failure.

Examples:
- BA omits essential MVP requirements or major business rules
- SA contradicts major requirements or produces a contradictory architecture
- TA violates user technology/cloud constraints without justification
- TA conflicts with the approved architecture
- DP exceeds the hard timeline or omits necessary testing/readiness work
- RW materially loses important specialist detail
- major security or data-residency requirements are ignored

================ SCORING ================

Calculate a score from 0.00 to 1.00 using:

Completeness & Depth ................. 35%
Constraint Adherence ................ 25%
Consistency & Grounding ............. 20%
Realism & Proportionality ........... 20%

Do not score based on document length alone.

A short deliverable can pass when it contains the required analytical substance.
A long deliverable can fail when it is generic, contradictory, or materially
incomplete.

================ ROLE COMPLETENESS STANDARD ================

Judge whether the deliverable contains enough useful substance to support the
next decision in the sequential pipeline.

For the Report Writer, a core section is insufficient when it is reduced to:
- a title with almost no content
- one generic paragraph where upstream material contains meaningful detail
- a tiny table without explanation
- a feature list without scope reasoning
- responsibilities without allocation
- milestones without sequencing
- tests without execution/exit criteria
- risks without mitigation/contingency

Do not impose artificial word counts.

Judge specificity, coverage, traceability, and decision usefulness.

================ REPORT WRITER HARD GATE ================

For Report Writer only, failure is mandatory when one or more of these serious
conditions exists:

1. Multiple core sections are substantially underdeveloped relative to the
   available upstream material.

2. The report is effectively a short executive summary instead of a full
   solution blueprint.

3. Workstreams are too generic to guide implementation.

4. Staffing is too shallow to explain responsibilities or allocation.

5. Timeline is too shallow to establish credible sequencing and feasibility.

6. Technology choices are presented without important rationale or trade-offs
   preserved from upstream work.

7. Architecture is reduced to a diagram or generic prose without meaningful
   explanation of components, flows, data, security, resilience, integrations,
   and deployment.

8. Testing, deployment, security, or production readiness are merely
   checklists.

9. Important specialist findings are omitted despite being relevant.

10. The result is materially less useful than the available upstream analysis
    because of unnecessary compression.

Do not fail merely because one section is concise.
Fail when concision causes meaningful information loss.

================ RESEARCH / ACCURACY CHECK ================

For research-dependent claims, verify that the deliverable:
- preserves source attribution when supplied
- distinguishes facts from assumptions
- avoids unsupported certainty
- does not fabricate technical, regulatory, licensing, cloud, or service-limit
  claims
- treats volatile/current claims cautiously

Do not require citations for ordinary reasoning that does not need external
verification.

================ REALISM CHECK ================

Check for:
- impossible timelines
- inadequate staffing
- excessive parallelism
- ignored dependencies
- insufficient testing/stabilization
- architecture complexity inconsistent with the delivery window
- technology choices conflicting with the approved architecture
- production-readiness work omitted from the schedule
- unsupported precision

When inputs are incomplete, explicit uncertainty is preferable to fabricated
precision.

================ PASS CONDITION ================

Return passed=true ONLY when all of the following are satisfied:

1. score >= threshold
2. no critical deficiency exists
3. the deliverable is sufficiently complete for its role
4. user constraints are respected
5. the proposal is realistic
6. the output is grounded in the available inputs/upstream material
7. any role-specific hard gate is satisfied

Otherwise return passed=false.

================ REMEDIATION ================

When the deliverable fails, provide precise instructions for the next retry.

Identify:
- the deficient section
- the missing or incorrect information
- what should be changed
- what upstream material should be preserved
- any realism or constraint problem

Do not say only:
"Add more detail."

Prefer:
"Expand Section 6 with workstream-level activities, owners, dependencies,
duration, and exit criteria using the Delivery Planner analysis."

When the deliverable passes:

remediation_guidance = "None"

================ OUTPUT FORMAT ================

Return ONLY valid JSON:

{{
  "score": 0.00,
  "passed": false,
  "summary": "Brief overall assessment.",
  "strengths": [
    "Specific strength"
  ],
  "critique": [
    "Specific deficiency"
  ],
  "remediation_guidance": "Specific correction instructions or 'None'."
}}

Do not return Markdown fences.
Do not return commentary outside the JSON object.
"""

    return Task(
        description=description,
        expected_output=(
            "Valid JSON containing exactly these fields: score, passed, summary, "
            "strengths, critique, and remediation_guidance. The evaluation must "
            "apply the role-specific quality criteria, user constraints, weighted "
            "scoring, realism checks, grounding checks, and any applicable "
            "Report Writer hard-depth gate."
        ),
        agent=agent,
    )