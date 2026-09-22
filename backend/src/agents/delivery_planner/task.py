from crewai import Task

from .agent import create_delivery_planner


def create_delivery_planner_task(
    delivery_timeline_months: int,
    ba_task: Task,
    sa_task: Task,
    ta_task: Task,
) -> Task:
    agent = create_delivery_planner()

    context_tasks = [ba_task, sa_task, ta_task]

    description = f"""
Act as the Principal Delivery Planner for this solution.

Create a realistic, execution-ready Delivery and Implementation Plan using the
Business Analyst requirements, Solution Architect architecture, and Technology
Advisor technology decisions.

================ HARD DELIVERY CONSTRAINT ================

Delivery Timeline:
{delivery_timeline_months} months

This is a hard constraint.

================ PREFERENCE SENSITIVITY RULE ================
The project plan must adapt to the user’s stated preferences, especially
technology preference, cloud preference, traffic assumptions, and country-level
residency constraints. If these preferences change, the delivery plan should
update sequencing, staffing emphasis, infrastructure choices, testing scope,
operational readiness, and risk profile accordingly.

The MVP must be designed, implemented, integrated, tested, security-validated,
production-readied, and released within this timeline.

Do not silently extend the timeline.

If the upstream scope cannot realistically fit, identify the conflict and
show how scope, sequencing, staffing, or implementation approach must change.
Do not hide feasibility problems.

================ DELIVERY OBJECTIVE ================

Translate the upstream solution into an executable delivery model.

The plan must make clear:

What needs to be built?
Who builds it?
In what order?
What depends on what?
What can happen in parallel?
How much effort is involved?
When is each capability expected?
What proves the work is complete?
What can block delivery?
How is the system prepared for production?

Use the actual upstream requirements, architecture, and technology choices.
Do not redesign them.

================ REQUIRED DELIVERABLES ================

1. DELIVERY STRATEGY & GOVERNANCE

Define the delivery approach appropriate for the project.

Cover:
- delivery methodology
- sprint / iteration cadence
- planning cadence
- backlog / scope control
- architecture and technical decision governance
- Definition of Ready
- Definition of Done
- review/demo cadence
- defect management
- stakeholder checkpoints
- release governance

Explain why the chosen delivery approach fits the project and timeline.

2. MVP-TO-WORK MAPPING

Translate the Business Analyst's MVP scope into actual implementation work.

Use:

| MVP Capability | Required Outcome | Major Work Needed | Primary Owner | Dependencies | Delivery Phase |

Do not reduce the MVP to a list of feature names.

Show how business requirements become engineering work.

3. IMPLEMENTATION WORKSTREAMS

Create detailed workstreams.

Examples where relevant:
- foundation/platform setup
- frontend/client implementation
- backend/application implementation
- core business workflows
- data/persistence
- integrations
- authentication/authorization
- security/compliance
- observability
- performance/scalability
- testing/QA
- DevOps/deployment
- production readiness

Use:

| Workstream | Objective | Major Activities | Deliverables | Primary Role | Supporting Roles | Dependencies | Duration |

Activities must describe real implementation work, not generic labels.

For example, prefer:
"Implement consent validation rules and audit events"
over:
"Build consent module."

4. TEAM & STAFFING MODEL

Derive the team from the actual scope.

Use:

| Role | Core Responsibility | Workstreams | Allocation / FTE | Active Phase | Key Deliverables |

Explain:
- why each role is required
- where the role is heavily used
- where the role is part-time/shared
- which responsibilities should not be combined
- when specialist involvement is required
- how the team changes across phases

Do not invent a large team merely to make the schedule appear faster.

5. CAPACITY & STAFFING FEASIBILITY CHECK

Validate whether the proposed staffing can actually complete the stated work.

Consider:
- parallel work capacity
- specialist bottlenecks
- shared-role contention
- review/approval capacity
- QA capacity
- security capacity
- DevOps capacity
- integration capacity

Identify any staffing bottleneck that could affect the critical path.

6. PHASE PLAN

Break the complete timeline into meaningful implementation phases.

At minimum, cover as applicable:
- foundation
- core implementation
- integrations
- system integration
- validation
- hardening
- production readiness
- go-live / hypercare

For each phase explain:
- objective
- major workstreams
- major activities
- expected outputs
- dependencies
- entry conditions
- exit criteria
- major risks

Do not compress the project into a handful of generic milestones.

7. DETAILED SPRINT / ITERATION PLAN

Create a realistic sprint-level or iteration-level plan across the
{delivery_timeline_months}-month timeline.

Use a structure such as:

| Sprint / Window | Objective | Work in Progress | Key Deliverables | Dependencies | Quality Gate | Exit Condition |

Make dependencies and parallel work visible.

The schedule must show the movement from:

Foundation
→ Implementation
→ Integration
→ Validation
→ Stabilization
→ Production

Include contingency or recovery space where realistically required.

8. CRITICAL PATH & DEPENDENCIES

Identify the work that controls the delivery date.

Use:

| Dependency / Milestone | Predecessor | Successor | Why It Matters | Critical Path? | Consequence if Delayed | Mitigation |

Cover relevant:
- business approvals
- environment setup
- architecture decisions
- technology provisioning
- integrations
- data availability
- security prerequisites
- testing dependencies
- deployment prerequisites
- external/vendor dependencies

Distinguish hard blockers from softer dependencies.

9. EFFORT & COMPLEXITY ASSESSMENT

For major workstreams estimate relative effort and complexity.

Use:

| Workstream | Scope | Complexity | Main Effort Drivers | Key Risk | Estimated Relative Effort |

Do not fabricate precision.

Explain the drivers behind the estimates.

Where the upstream inputs are insufficient for numerical estimation, say so and
use qualitative sizing.

10. TESTING & QUALITY PLAN

Create an execution-oriented testing strategy tied to the delivery schedule.

Cover relevant:
- unit testing
- component testing
- API/contract testing
- integration testing
- end-to-end testing
- database/data validation
- asynchronous processing
- regression testing
- security testing
- performance/load testing
- resilience/failure testing
- backup/restore
- UAT
- production smoke testing

Use:

| Test Area | Scope | Owner | Environment | Planned Phase | Entry Criteria | Exit Criteria |

Explain what must be proven before production.

Do not treat testing as a final-stage activity only.

11. SECURITY & PRODUCTION READINESS

Explain the work required to turn the solution into a production-ready system.

Cover relevant:
- security hardening
- IAM validation
- secrets/configuration
- encryption validation
- vulnerability remediation
- audit/log verification
- monitoring/alerting
- backup/recovery validation
- operational runbooks
- support readiness
- incident response readiness
- rollback readiness

Make clear when these activities occur in the timeline.

12. DEPLOYMENT & GO-LIVE PLAN

Describe the complete production release sequence.

Cover:
- environment readiness
- build/artifact promotion
- database/schema migration
- configuration/secrets
- release approvals
- deployment
- health checks
- smoke tests
- rollback
- monitoring
- hypercare
- ownership after release

Use entry and exit criteria for go-live.

13. DELIVERY RISK REGISTER

Create a project-specific risk register.

Use:

| Risk | Cause | Impact | Likelihood | Early Warning | Mitigation | Contingency | Owner |

Cover the risks that actually matter for this project:
- scope
- timeline
- staffing
- architecture
- technology
- integrations
- data
- security
- compliance
- performance
- deployment
- external dependencies

Do not fill the register with generic project-management risks.

14. POST-MVP EVOLUTION ROADMAP

Preserve capabilities intentionally deferred from MVP.

For each major post-MVP capability explain:
- why it was deferred
- prerequisite
- expected value
- technical implication
- delivery implication
- relationship to the MVP architecture

Separate near-term evolution from longer-term expansion.

================ DELIVERY REALISM RULES ================

Build a plan a real engineering organization could execute.

Do not:
- assume unlimited parallelism
- schedule every activity simultaneously
- ignore dependencies
- under-resource QA/security/DevOps
- leave no stabilization time
- postpone all integration until the end
- pretend production release is instantaneous
- invent impossible staffing capacity
- hide scope/timeline conflicts

For every major commitment, internally check:

1. What must exist first?
2. Which role performs the work?
3. What dependency exists?
4. What can run in parallel?
5. What must be validated?
6. What happens if it is delayed?
7. Does the staffing support the workload?
8. Does the work fit inside the hard timeline?

================ UPSTREAM AUTHORITY ================

Business Analyst owns:
- business problem
- users/personas
- business requirements
- business rules
- MVP scope
- NFRs
- business dependencies and risks

Solution Architect owns:
- architecture style
- component boundaries
- data boundaries
- system flows
- resilience patterns
- integration architecture
- security architecture

Technology Advisor owns:
- programming languages
- frameworks
- databases
- messaging
- cloud services
- security tooling
- observability tooling
- technology trade-offs

Delivery Planner owns:
- implementation sequencing
- workstreams
- staffing
- milestones
- sprint plan
- dependencies
- critical path
- delivery effort
- testing schedule
- production readiness
- deployment
- delivery risks

Do not silently redesign upstream decisions.

If an upstream decision creates a delivery problem, identify the problem and
document the delivery implication rather than silently replacing the decision.

================ AUTHORING STANDARD ================

The final plan must be detailed enough that a delivery manager, engineering
lead, QA lead, security lead, DevOps engineer, and project stakeholder can
understand what happens, when it happens, who is responsible, and what proves
completion.

Do not produce a high-level roadmap with generic labels; include concrete
workstreams, staffing logic, dependencies, milestones, testing gates, and
production-readiness checks.

Prefer concrete activities, tables, sequencing, dependencies, owners, and exit
criteria over generic project-management language.

The plan must clearly connect:

Business Scope
→ Implementation Work
→ Team
→ Dependencies
→ Timeline
→ Testing
→ Production Readiness
→ Go-Live
"""

    return Task(
        description=description,
        expected_output=(
            "A rigorous, execution-ready Delivery and Implementation Plan covering "
            "delivery methodology, MVP-to-work mapping, detailed implementation "
            "workstreams, realistic staffing and role allocation, staffing "
            "feasibility, phased delivery, sprint/iteration sequencing, critical "
            "path and dependencies, effort and complexity, testing and quality "
            "gates, security and production readiness, deployment and go-live, "
            "project-specific risks and mitigations, and post-MVP evolution. "
            "It must be substantive and concrete, with real work items, owners, dependencies, "
            "and exit criteria, rather than a brief summary. The plan must fit within the "
            "hard delivery timeline and remain consistent with the upstream Business Analyst, "
            "Solution Architect, and Technology Advisor decisions. It must also reflect the "
            "user’s stated technology, cloud, traffic, and residency preferences and adapt as "
            "those inputs change."
        ),
        agent=agent,
        context=context_tasks,
    )