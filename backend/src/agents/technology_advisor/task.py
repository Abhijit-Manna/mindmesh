from typing import Optional

from crewai import Task

from .agent import create_technology_advisor


def create_technology_advisor_task(
    technology_preference: str,
    cloud_preference: str,
    expected_daily_traffic: str,
    delivery_timeline_months: int,
    data_hosting_country: str,
    ba_task: Task,
    sa_task: Task,
) -> Task:
    agent = create_technology_advisor()

    description = f"""
Act as the Principal Technology Advisor for this solution.

Your job is to convert the Business Analyst requirements and Solution
Architect design into a concrete, defensible, implementation-ready technology
stack.

The Business Analyst defines the business requirements.
The Solution Architect defines the logical architecture and component
boundaries.
You own the concrete technology decisions.

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


================ TECHNOLOGY DECISION OBJECTIVE ================

Select technologies that are appropriate for the actual problem.

Every major technology choice must be defensible against:
- functional requirements
- NFRs
- architecture
- expected scale
- delivery timeline
- team feasibility
- security
- compliance
- data residency
- operational complexity
- cost / TCO
- long-term maintainability

Do not choose technology because it is fashionable or merely powerful.

Avoid unnecessary infrastructure and unnecessary distributed-system complexity.

When concrete facts are volatile or version-dependent, use available research
tools and distinguish verified facts from assumptions.

================ REQUIRED DELIVERABLES ================

1. TECHNOLOGY DECISION SUMMARY

Begin with the recommended stack and briefly explain the purpose of each major
technology.

Use:

| Layer / Capability | Recommended Technology | Purpose | Key Reason | Architecture Fit |

Include all major relevant layers, such as:
- application/backend
- API
- frontend/client where in scope
- database
- cache
- messaging / queues
- object/file storage
- search/indexing where needed
- identity/security components
- observability
- CI/CD
- cloud infrastructure services

2. REQUIREMENTS-TO-TECHNOLOGY TRACEABILITY

Connect important requirements and architectural decisions to technology
choices.

Use:

| Requirement / Architectural Need | Technology Choice | Why It Fits | Important Constraint |

Do not merely list technologies.

Explain how the selected technology satisfies the actual need.

3. MAJOR ALTERNATIVES & TRADE-OFFS

For each major decision, compare meaningful alternatives before selecting one.

At minimum, evaluate alternatives for the important areas where a real choice
exists, such as:
- backend/application framework
- primary database
- caching / messaging approach
- major cloud services where applicable

Use:

| Decision Area | Option | Benefits | Drawbacks | Delivery Impact | Operational Impact | Scale / Performance | Licensing / Cost | Fit |

Then explain why the selected option is appropriate for this specific project.

Do not manufacture alternatives simply to satisfy the format.

4. DATABASE & DATA-STORE STRATEGY

Define the recommended data-store approach.

Explain:
- primary persistence model
- logical storage responsibilities
- transactional needs
- consistency expectations
- indexing considerations
- backup/recovery considerations
- caching strategy
- cache invalidation / TTL considerations
- read-heavy vs write-heavy behavior
- when additional storage technologies are justified

Do not introduce polyglot persistence unless there is a concrete reason.

5. MESSAGING & ASYNCHRONOUS PROCESSING

Where asynchronous processing is required, explain:
- why it is needed
- selected mechanism
- message/event boundaries
- delivery semantics
- retry behavior
- dead-letter handling
- idempotency
- ordering requirements
- expected workload
- operational implications

If asynchronous infrastructure is not necessary for part of the solution,
say so rather than adding it automatically.

6. CLOUD SERVICE MAPPING

Map the logical architecture to concrete services on the user's preferred
cloud platform.

Use:

| Infrastructure Role | Selected Cloud Service | Purpose | Configuration / Sizing Consideration | Residency Consideration |

Cover relevant:
- compute
- networking
- database
- cache
- object storage
- messaging
- secrets
- monitoring
- logging
- security controls

Respect the requested cloud preference.

When a requested service does not exist or is not suitable, explain the
constraint and identify the closest viable approach rather than silently
changing the cloud platform.

7. SCALABILITY & CAPACITY CONSIDERATIONS

Evaluate the stack against:
{expected_daily_traffic}

Explain:
- likely bottlenecks
- scaling mechanisms
- stateless/stateful concerns
- database scaling
- caching
- asynchronous workload isolation
- rate limiting / backpressure where relevant
- capacity assumptions

Use calculations when they can be derived from the available inputs.

Do not invent precise capacity numbers without a defensible basis.

8. SECURITY & COMPLIANCE TECHNOLOGY

Identify the concrete technologies or services needed for:
- authentication
- authorization / IAM
- secrets management
- encryption
- key management
- audit logging
- network security
- vulnerability management
- observability/security monitoring

Tie the choices to the stated data-hosting country and relevant compliance
needs.

Do not claim legal or regulatory compliance merely because a technology is
present. Separate technical controls from legal/compliance obligations.

9. OPEN-SOURCE / ENTERPRISE & LICENSING STRATEGY

Respect:
{technology_preference}

Evaluate where relevant:
- license type
- commercial support
- operational implications
- vendor lock-in
- migration difficulty
- availability of managed services
- long-term sustainability

Flag licenses or commercial restrictions that could materially affect the
project.

Do not make unsupported licensing claims; verify important licensing facts.

10. DEVELOPER EXPERIENCE & QUALITY TOOLCHAIN

Recommend the supporting engineering toolchain.

Cover relevant:
- testing frameworks
- API testing
- integration testing
- mocking
- linting
- formatting
- static analysis
- API documentation
- dependency scanning
- container/image scanning
- CI/CD quality checks

Keep the toolchain consistent with the selected technologies.

11. OPERATIONAL TOOLING & OBSERVABILITY

Define the recommended approach for:
- logs
- metrics
- traces
- alerting
- dashboards
- health checks
- error tracking
- audit events
- incident diagnostics

Explain which operational signals are important for production.

12. TECHNOLOGY RISKS & MITIGATIONS

Create a concrete technology risk register.

Use:

| Risk | Cause | Impact | Likelihood | Early Warning | Mitigation | Contingency |

Focus on risks that arise from the actual stack, such as:
- vendor dependency
- service limits
- operational complexity
- immature components
- migration difficulty
- performance bottlenecks
- licensing constraints
- data residency limitations
- integration limitations

13. FINAL TECHNOLOGY RECOMMENDATION

End with a consolidated decision summary.

For each major technology decision, state:
- selected option
- principal reason
- major trade-off
- important dependency
- important risk
- why it is appropriate for the current architecture and timeline

Also identify any technology decision that should remain provisional because
an unresolved assumption or discovery question must be answered first.

================ DECISION RULES ================

Respect this authority model:

Business Analyst:
- business problem
- users
- requirements
- MVP scope
- business rules
- business NFRs

Solution Architect:
- architecture style
- logical components
- component boundaries
- request/data flows
- data boundaries
- resilience patterns
- architectural constraints

Technology Advisor:
- frameworks
- programming languages
- databases
- cache
- messaging
- cloud services
- infrastructure technologies
- security tooling
- observability tooling
- developer toolchain
- technology trade-offs

Do not silently redesign the Solution Architect's architecture.

If the architecture appears to require a technology change, explain the
conflict explicitly and document the smallest necessary adjustment.

================ AUTHORING STANDARD ================

The result must be analytical, comparative, and implementation-oriented.

Avoid:
- generic technology lists
- unexplained recommendations
- "industry standard" as the only justification
- technology choices disconnected from requirements
- unnecessary complexity
- unsupported claims
- fake precision

For every major choice, answer:

What is being selected?
Why is it needed?
Why this option?
What are the alternatives?
What does it cost or complicate?
What risks does it introduce?
How does it fit the architecture?
How does it affect delivery?
What assumption could change the decision?

The final technology specification must give the Delivery Planner enough
information to estimate implementation work, staffing, dependencies, testing,
deployment, and operational effort realistically.
"""

    return Task(
        description=description,
        expected_output=(
            "A detailed and defensible Technology Architecture Specification "
            "covering the recommended technology stack, requirements-to-technology "
            "traceability, meaningful alternatives and trade-offs, database and "
            "storage strategy, messaging, cloud service mapping, scalability, "
            "security and compliance tooling, licensing/vendor considerations, "
            "developer and operational tooling, technology risks, and final "
            "technology decisions. Major choices must be justified against the "
            "actual architecture, requirements, scale, delivery timeline, and "
            "user constraints."
        ),
        agent=agent,
        context=[ba_task, sa_task],
    )