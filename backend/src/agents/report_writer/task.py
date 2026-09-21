from typing import Dict, Any
from crewai import Task

from .agent import create_report_writer


def create_report_writer_task(
    inputs: Dict[str, Any],
    ba_task: Task,
    sa_task: Task,
    ta_task: Task,
    dp_task: Task,
    ba_output: str = "",
    sa_output: str = "",
    ta_output: str = "",
    dp_output: str = "",
) -> Task:
    agent = create_report_writer()

    # The pipeline already supplies the actual specialist outputs below.
    # Do not also pass CrewAI task context: that would duplicate the same material.
    def _task_output(task: Task) -> str:
        output = getattr(task, "output", None)
        if output is None:
            return ""
        raw = getattr(output, "raw", output)
        return str(raw or "").strip()

    ba_source = str(ba_output or "").strip() or _task_output(ba_task)
    sa_source = str(sa_output or "").strip() or _task_output(sa_task)
    ta_source = str(ta_output or "").strip() or _task_output(ta_task)
    dp_source = str(dp_output or "").strip() or _task_output(dp_task)

    description = f"""
You are the final author of the MindMesh Enterprise Solution Blueprint.
Synthesize the four specialist deliverables below into ONE coherent,
execution-ready proposal for readers who were not present for the analysis.

Do not create a fifth solution. Preserve the approved upstream decisions,
trade-offs, constraints, research, and uncertainty. Your job is to connect them
into a clear chain:
Business Need -> Requirements -> MVP -> Architecture -> Technology -> Delivery
-> Testing -> Deployment -> Operations.

USER INPUTS
------------
Business Problem / Idea:
{inputs.get('business_idea', '').strip()}

Technology Preference: {inputs.get('technology_preference', 'N/A')}
Cloud Preference: {inputs.get('cloud_preference', 'N/A')}
Expected Daily Traffic: {inputs.get('expected_daily_traffic', 'N/A')}
Delivery Timeline: {inputs.get('delivery_timeline_months', 6)} months
Data Hosting Country: {inputs.get('data_hosting_country', 'N/A')}

UPSTREAM SPECIALIST DELIVERABLES
--------------------------------
These are the actual specialist outputs. Treat them as the primary factual source.
Preserve useful detail rather than flattening it into generic statements.

[BUSINESS ANALYST]
{ba_source}

[SOLUTION ARCHITECT]
{sa_source}

[TECHNOLOGY ADVISOR]
{ta_source}

[DELIVERY PLANNER]
{dp_source}

AUTHORITY ORDER
---------------
Business Analyst: business problem, users, requirements, rules, MVP/deferred scope.
Solution Architect: architecture style, boundaries, flows, security, resilience,
integrations, deployment topology.
Technology Advisor: concrete technology choices, tooling, cloud services,
data stores, messaging, observability, CI/CD and technology trade-offs.
Delivery Planner: workstreams, staffing, sequencing, milestones, critical path,
testing, readiness, go-live and delivery risks.

When sources overlap, use the authority above. When they materially conflict and
cannot be reconciled from the sources, state the unresolved issue instead of
inventing a new decision.

AUTHORING RULES
---------------
1. WRITE ONE INTEGRATED DOCUMENT
Use one voice. Do not write four mini-reports or repeatedly say which agent
recommended something.

2. EXECUTION-READY DEPTH
For every major decision, workstream, role, or milestone, answer as applicable:
WHAT, WHY, HOW, WHO, WHEN, DEPENDS ON, and WHAT PROVES COMPLETION.
Prefer concise explanatory prose plus tables over name-only lists.

3. TECHNOLOGY DECISIONS MUST BE DEFENDED
For important selections, preserve:
- requirement being satisfied
- selected technology and purpose
- relevant alternatives considered upstream
- project-specific rationale
- important trade-offs and drawbacks
- operational/scaling/security/maintainability implications
- licensing/vendor implications when relevant
- when an alternative would become preferable
Do not reduce rationale to phrases such as "mature", "scalable", or "industry standard".

4. WORKSTREAMS MUST DESCRIBE REAL WORK
For each significant workstream show:
objective, concrete activities/deliverables, owner, supporting roles, prerequisites,
dependencies, timing, parallel work, handoffs, and exit/acceptance evidence.
Avoid vague rows such as "build backend" or "set up infrastructure".

5. STAFFING MUST FOLLOW THE WORK
Show role, FTE/count, seniority/skills, responsibilities, owned workstreams,
active window/allocation, handoffs, and whether responsibilities can be combined.
Do not invent headcount. Preserve upstream sizing and explain the workload logic.

6. TIMELINE MUST BE EXECUTABLE
Use the Delivery Planner's sequencing. Show relative windows (Week/Sprint/Month),
objectives, workstreams in progress, deliverables, dependencies, exit criteria,
parallelism, critical path, stabilization/hardening, go-live, hypercare, and
contingency. Do not invent calendar dates when only duration is known.

7. TESTING / SECURITY / RELEASE CANNOT BE CHECKLIST-ONLY
Explain what is validated, where, by whom, when, and what must be true before
production. Include concrete release/rollback/readiness conditions supported by
upstream analysis.

8. PRESERVE RESEARCH AND UNCERTAINTY
Keep supplied evidence, source attribution, comparisons, service limitations,
standards, assumptions, and open questions. Do not fabricate citations or facts.

9. DO NOT INVENT OR REDESIGN
Do not add unsupported requirements, architecture components, technologies,
staffing numbers, dates, regulations, metrics, or scope. Do not quietly move
deferred features into MVP.

10. OUTPUT BUDGET
The document must be detailed, but every paragraph must earn its place. Spend
space on decisions, implementation detail, sequencing, trade-offs, dependencies,
and acceptance criteria rather than repeated background prose.

REQUIRED OUTPUT STRUCTURE
-------------------------
Produce the following 14 sections in exactly this order. Each section must be
substantive when upstream material supports it.

1. DELIVERY OVERVIEW
- business objective/problem, target users, proposed solution, MVP strategy
- principal architecture/technology direction
- delivery approach, constraints, major risks, expected outcome
- concise phase summary table

2. BUSINESS / MVP SCOPE AND PRIORITIES
- personas/users and important journeys
- core capabilities and functional requirements
- business rules and acceptance criteria where supplied
- explicit MVP, deferred, and out-of-scope boundary
- scope-control implications and traceability to business need

3. RECOMMENDED TECHNOLOGY STACK
Use a matrix such as:
| Layer / Component | Selected Technology | Purpose | Rationale | Alternatives / Trade-offs |
Include all relevant layers from upstream (frontend, backend/API, DB, cache,
messaging, storage, search, identity/auth, realtime/video, jobs/AI, observability,
security, CI/CD, IaC, cloud, testing). Defend major choices; do not merely list them.

4. IMPLEMENTATION WORKSTREAMS
Use a detailed table or grouped subsections covering the real work required.
Include epics/deliverables, concrete activities, owner/support, dependencies,
timing, parallelism, handoffs, and exit criteria. Include specialist workstreams
such as data, integrations, infrastructure, security, QA, performance, release,
training/migration only when supported by upstream analysis.

5. RECOMMENDED TEAM AND ROLE DISTRIBUTION
Show realistic staffing tied to workload and timeline. Explain why each significant
role exists, where it is needed, when it is active, and what it owns/supports.

6. DELIVERY TIMELINE AND MILESTONES
Use relative timeboxes and a detailed sequence. Include discovery/baseline,
foundation, implementation, integration, automation, security, performance,
UAT, hardening, release, go-live and hypercare as applicable. Clearly mark
critical-path items, dependencies, justified parallel work, and contingency.

7. EFFORT & COMPLEXITY ASSESSMENT
Cover the main effort drivers across requirements, architecture, technology,
integrations, data, security/compliance, infrastructure, testing, performance,
operations and organization. Preserve upstream estimates; do not invent precision.

8. DEPENDENCIES AND PREREQUISITES
Use:
| Type | Dependency / Prerequisite | Why Required | Responsible Party | Required By | Impact if Delayed | Mitigation |
Distinguish hard blockers from softer dependencies where supported and identify
critical-path dependencies.

9. HIGH-LEVEL SOLUTION ARCHITECTURE
Explain architecture style, boundaries, responsibilities, request/data flows,
persistence, cache/messaging, integrations, security/identity, secrets,
observability, resilience, scaling, deployment topology, trade-offs and deferred
patterns. Connect important architecture decisions to business/NFR needs.

Authoritative Architecture Diagram:
- Preserve the Solution Architect's valid Mermaid architecture exactly in substance.
- Do not design a competing topology.
- Use a Mermaid fenced block when the upstream output supplies one.

Supporting Diagrams:
For a sufficiently complex solution, include at least 3 useful supporting Mermaid
diagrams when upstream material supports them. Prefer different concepts such as:
1) user/business workflow, 2) request/interaction sequence, 3) data lifecycle/flow,
4) integration flow, 5) deployment/release flow, 6) critical-path/dependency flow,
7) incident/operations flow, or 8) test/release validation flow.
Each diagram must have a short explanation of what it shows and why it matters.
Supporting diagrams must not redefine architecture boundaries or duplicate the
canonical topology. Omit a diagram only when the upstream material genuinely
cannot support it.

10. TESTING & QUALITY STRATEGY
Use:
| Test Type | Scope | Tool / Approach | Environment | Timing | Exit Criterion | Owner |
Cover applicable unit, component, contract/API, integration, DB/event, E2E,
regression, security, performance/load, resilience, backup/restore, UAT and
production smoke validation. Explain the quality gates and release evidence.

11. DEPLOYMENT & RELEASE STRATEGY
Explain the end-to-end path from development to staging/test to production,
including CI/CD, artifact flow, infrastructure changes, migrations, secrets/config,
approvals, health checks, smoke tests, rollback triggers, monitoring, incident
readiness and hypercare. Keep it consistent with the approved architecture/stack.

12. DELIVERY RISKS & MITIGATIONS
Use:
| Risk | Cause | Impact | Likelihood | Early Warning | Mitigation | Contingency | Owner |
Focus on project-specific scope, timeline, staffing, architecture, technology,
integration, data, security/compliance, performance, vendor and operational risks.

13. FUTURE EVOLUTION
Preserve intentionally deferred capabilities. For each significant item explain
why deferred, prerequisite, benefit, technical/delivery implication and likely
sequence. Separate near-term post-MVP from longer-term evolution.

14. ASSUMPTIONS AND OPEN QUESTIONS
Use:
| Area | Assumption / Question | Why It Matters | Impact if Wrong | Decision Owner / Next Action |
Keep unresolved business, product, technical, scale, integration, data, security,
compliance, vendor and delivery questions visible.

OPTIONAL ADDITIONAL SECTIONS
----------------------------
After section 14, add only sections materially supported by upstream analysis,
for example Cost/TCO, Security Threat Model, Compliance Controls, Data Model,
Integration/API Strategy, Observability/Operations, DR/BCP, Governance/Decision Log,
Analytics, or Post-MVP Roadmap.

FINAL QUALITY GATE (INTERNAL)
-----------------------------
Before returning the document, verify internally that:
- all 14 core sections exist and are substantive
- important upstream details were not lost
- major technology choices retain rationale and trade-offs
- workstreams contain actual implementation work
- staffing is tied to workload/timeline
- timeline shows sequencing, parallelism, critical path, stabilization and go-live
- testing, security, deployment and production readiness explain what proves readiness
- at least 3 supporting diagrams are included for a complex solution when supported
- the canonical architecture remains authoritative
- scope, technology, architecture and delivery remain consistent
- no unsupported facts or invented precision were introduced
- unresolved conflicts/questions remain visible
- the result reads as one serious proposal that another team could execute from

Return only the completed blueprint in Markdown.
"""

    return Task(
        agent=agent,
        description=description,
        expected_output=(
            "A single, detailed Enterprise Solution Blueprint in Markdown with all 14 core "
            "sections in order. It must preserve upstream requirements, architecture, "
            "technology rationale/trade-offs, implementation work, staffing, timeline, "
            "dependencies, testing, release/readiness, risks, future evolution and open "
            "questions. Include the authoritative Solution Architect Mermaid topology and "
            "use at least 3 additional supporting Mermaid diagrams for a sufficiently "
            "complex solution when upstream material supports them. Do not invent facts, "
            "decisions, dates, staffing or scope."
        ),
        context=[],
    )
