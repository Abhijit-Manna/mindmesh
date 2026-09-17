# SolutionForge AI — Hackathon TODO

This breakdown assumes six people working in parallel with shared contracts agreed on Day 1. The product must work for any business idea, so fixtures and demos should cover more than one domain.

## Repository structure

Current scaffold:

```text
mindmesh/
├── README.md
├── API_CONTRACTS.md
├── SOLUTION_BLUEPRINT.md
├── TODO.md
├── pyproject.toml
├── .python-version
├── backend/
│   ├── README.md
│   ├── pyproject.toml
│   └── src/
│       ├── main.py
│       ├── tasks.py
│       └── agents/
└── frontend/
```

Implementation target:

```text
backend/src/
├── routes/
│   ├── health.py
│   └── blueprints.py
├── config.py
├── models.py
├── orchestration.py
├── research.py              # CrewAI WebsiteSearchTool setup
├── evaluation.py
├── reporting.py
├── tasks.py
└── agents/
    ├── business_analyst.py
    ├── solution_architect.py
    ├── technology_advisor.py
    └── delivery_planner.py
frontend/
└── streamlit_app.py
```

Keep the implementation aligned with this structure. Use `API_CONTRACTS.md` as the source of truth for route paths, request/response schemas, status codes, and frontend integration. Do not create a Tavily adapter or Tavily-specific configuration.

## Shared MVP acceptance criteria

- [ ] Streamlit captures all six required inputs.
- [ ] FastAPI validates the request and runs the four agents sequentially.
- [ ] Business Analyst → Solution Architect → Technology Advisor → Delivery Planner context handoff is observable and tested.
- [ ] Every agent output passes a role-specific evaluation gate before downstream handoff.
- [ ] Unsatisfactory outputs receive evaluator feedback and are retried within a bounded retry budget.
- [ ] Each relevant agent can use CrewAI's built-in search tool for role-specific research, with source URLs preserved.
- [ ] Technology Advisor is the single source of truth for the recommended stack.
- [ ] Generated output contains all 14 required blueprint sections.
- [ ] Markdown is converted to styled HTML.
- [ ] HTML is rendered and downloadable from Streamlit.
- [ ] Backend and UI surface failures without returning an empty success.
- [ ] Structured logs expose run, agent, attempt, evaluation, retry, latency, and failure events with secrets redacted.
- [ ] Representative business-idea fixture produces recommendations consistent with its submitted scale, timeline, technology preference, cloud preference, and data-hosting country.

## Member 1 — Business Analyst agent

- [ ] Define the shared input and output contract for the Business Analyst.
- [ ] Implement the Business Analyst CrewAI agent and task.
- [ ] Write the requirements prompt: users, stakeholders, functional requirements, non-functional requirements, MVP/future scope, assumptions, constraints, risks.
- [ ] Add a representative business-idea fixture and expected requirement categories without coupling the agent to a specific industry.
- [ ] Ensure the output does not make concrete technology selections.
- [ ] Add unit tests for prompt context and structured output.
- [ ] Define evaluator criteria for complete requirements, stakeholder coverage, MVP/future separation, assumptions, and risks.
- [ ] Add role-specific CrewAI search queries for domain terminology and requirement considerations; preserve cited sources.
- [ ] Test that failed evaluation feedback causes a bounded retry before handoff.
- [ ] Review the final report's Business/MVP Scope & Priorities section.

## Member 2 — Solution Architect agent

- [ ] Define the architecture output contract consumed by Technology Advisor.
- [ ] Implement the Solution Architect CrewAI agent and task.
- [ ] Write the architecture prompt for style, components, data flow, storage, security, scalability, MVP boundary, and future evolution.
- [ ] Add explicit anti-over-engineering guidance.
- [ ] Include varied scale, timeline, cloud, technology preference, and data-hosting constraints in test fixtures.
- [ ] Add tests for upstream requirements context and architecture/MVP consistency.
- [ ] Define evaluator criteria for proportionality, security, data flow, scalability, and unjustified infrastructure.
- [ ] Add role-specific CrewAI search queries for architecture, security, scale, and data-residency guidance.
- [ ] Test rejection and retry of contradictory or over-engineered architecture output.
- [ ] Review the final text-based architecture diagram.

## Member 3 — Technology Advisor agent

- [ ] Define the authoritative technology recommendation schema.
- [ ] Implement the Technology Advisor CrewAI agent and task.
- [ ] Write the prompt for specific choices, rationale, trade-offs, risks, open-source/enterprise analysis, scale, security, complexity, and lock-in.
- [ ] Enforce the exact cloud preference enum in the context.
- [ ] Ensure one recommended option and alternatives considered are returned for major capabilities.
- [ ] Add tests proving the selected cloud input is respected and the output is consumable by Delivery Planner.
- [ ] Define evaluator criteria for concrete choices, rationale, trade-offs, risks, preference compliance, and source evidence.
- [ ] Add role-specific CrewAI search queries for official technology/cloud documentation, limits, support status, and alternatives.
- [ ] Test that unsupported or weak recommendations are retried and that source URLs are retained.

## Member 4 — Delivery Planner agent

- [ ] Define the delivery output contract and required report headings.
- [ ] Implement the Delivery Planner CrewAI agent and task.
- [ ] Write the prompt for workstreams, roles, milestones, dependencies, risks, testing, deployment, effort, and future evolution.
- [ ] Ensure milestones fit the requested number of months.
- [ ] Add a representative timeline plan as an integration fixture and verify it fits the submitted number of months.
- [ ] Implement or coordinate required-section and consistency validation.
- [ ] Define evaluator criteria for timeline fit, dependencies, roles, testing, deployment, risks, and use of the accepted stack.
- [ ] Add role-specific CrewAI search queries for delivery practices, technology maturity, and testing/deployment constraints.
- [ ] Test that milestones outside the requested timeline are rejected and retried.
- [ ] Review the complete generated blueprint for consulting-style clarity.

## Member 5 — CrewAI orchestration and FastAPI backend

- [ ] Create the Python project structure and dependency manifest.
- [ ] Centralize environment configuration for OpenRouter, model name, CrewAI search, evaluators, and runtime settings.
- [ ] Centralize configuration for search enablement, evaluator thresholds, per-agent timeout, and `MAX_AGENT_RETRIES`; do not add Tavily-specific settings.
- [ ] Wire the four agents into a `Process.sequential` CrewAI crew.
- [ ] Add a deterministic orchestration wrapper around CrewAI for built-in search-tool calls, evaluation, bounded retries, and accepted-output handoff.
- [ ] Pass each accepted task output as context to the next task.
- [ ] Implement `POST /api/v1/blueprints` with typed Pydantic request/response models.
- [ ] Implement `GET /health` and `GET /api/v1/blueprints/{run_id}` according to `API_CONTRACTS.md`.
- [ ] Add input validation for enums, blank business idea, timeline, traffic, and country.
- [ ] Implement Markdown-to-styled-HTML conversion and safe rendering/sanitization.
- [ ] Add required-heading validation before returning a successful response.
- [ ] Add role-specific deterministic evaluators and optional LLM-as-judge evaluation.
- [ ] Feed failed evaluator criteria into retry prompts; fail explicitly after retry exhaustion.
- [ ] Attach CrewAI's built-in search tool to the relevant agents with source metadata and explicit provider-failure handling.
- [ ] Add explicit error handling and diagnostic logging without logging sensitive input unnecessarily.
- [ ] Emit structured lifecycle events for run, agent, research, evaluation, retry, acceptance, and failure.
- [ ] Confirm a separate coordinator agent is not needed; use CrewAI sequential process plus deterministic Python control flow.
- [ ] Add API unit and mocked integration tests.
- [ ] Add contract tests for every route, status code, validation error, and response shape in `API_CONTRACTS.md`.
- [ ] Document local API startup and `/docs`.

## Member 6 — Streamlit frontend, testing/demo, and docs

- [ ] Build the Streamlit input form for the six required fields.
- [ ] Add generic guidance/example values without hard-coding an industry into submitted requests.
- [ ] Implement API call, pending state, agent progress display, success rendering, and HTML download.
- [ ] Display current agent, evaluation status, retry count, and research/source status where available.
- [ ] Preserve form values and show actionable errors after failed requests.
- [ ] Add a small UI smoke checklist for a representative business-idea walkthrough.
- [ ] Coordinate end-to-end testing with the mocked API and one real OpenRouter smoke run.
- [ ] Coordinate mocked CrewAI search-tool and evaluator tests plus one real search smoke run if the configured provider is available.
- [ ] Prepare demo scenarios from multiple domains that vary scale, timeline, technology preference, and cloud preference.
- [ ] Maintain `README.md`, `SOLUTION_BLUEPRINT.md`, and this `TODO.md` as implementation decisions settle.
- [ ] Prepare the two-minute judge walkthrough and final demo script.

## Cross-team integration tasks

- [ ] Agree on the shared request, agent-context, and final-report contracts before parallel implementation.
- [ ] Use a domain-agnostic business-idea fixture as the first end-to-end fixture.
- [ ] Verify all recommendations include rationale, trade-offs, and risks.
- [ ] Verify no agent output reaches downstream until its evaluation gate accepts it.
- [ ] Verify retry feedback changes the next attempt and retry exhaustion is visible.
- [ ] Verify search citations are attached to research-backed claims or the claim is marked as an assumption.
- [ ] Verify the generated plan is MVP-first and does not add unjustified infrastructure.
- [ ] Verify the API response contains both Markdown and HTML.
- [ ] Verify the downloaded HTML opens as a readable styled report.
- [ ] Review secrets and confirm `.env` is ignored before any demo.
- [ ] Review structured logs for useful debugging information and redaction of keys/sensitive input.
- [ ] Run the smallest relevant automated test set after each integration merge.

## Rough day-by-day milestones

### Day 1 — Contracts and skeleton

- [ ] Confirm ownership and shared input/output schemas.
- [ ] Create Python environment, dependency manifest, configuration pattern, and basic app entry points.
- [ ] Implement a minimal FastAPI health route and Streamlit shell.
- [ ] Agree on the representative fixtures and final report headings.

### Day 2 — Agents in isolation

- [ ] Business Analyst and Solution Architect tasks return structured mocked outputs.
- [ ] Technology Advisor and Delivery Planner prompt contracts are reviewed.
- [ ] CrewAI sequential skeleton runs with mocked LLM responses.
- [ ] First unit tests cover input schema, task ordering, evaluator gates, and retry budget.

### Day 3 — Backend and orchestration integration

- [ ] FastAPI endpoint accepts a representative business-idea request.
- [ ] Four-agent context handoff works end to end with a mocked model.
- [ ] Markdown report assembly and required-heading validation are in place.
- [ ] Error paths for validation and crew failure are tested.
- [ ] CrewAI search-tool and evaluator provider failures have explicit tested behavior.

### Day 4 — Frontend and report experience

- [ ] Streamlit form calls the API and retains inputs on failure.
- [ ] Agent progress and final HTML rendering work.
- [ ] HTML download works locally.
- [ ] A representative business idea can be demonstrated from a clean start.

### Day 5 — Quality and recommendation consistency

- [ ] Run integration tests and fix contradictions in prompts or contracts.
- [ ] Confirm submitted cloud, data-hosting country, technology preference, scale, and timeline appear in relevant outputs.
- [ ] Perform a real OpenRouter smoke run and tune output length/format.
- [ ] Perform a CrewAI built-in search smoke run and verify source-aware outputs.
- [ ] Confirm retry and evaluation logs are readable during a run.

### Day 6 — Demo scenarios and polish

- [ ] Run a few constraint variations to show recommendations adapt.
- [ ] Improve styled HTML readability and progress messaging.
- [ ] Complete README setup instructions and internal design documentation.
- [ ] Verify no secrets, broken links, or placeholder implementation instructions remain.
- [ ] Verify no unbounded retry loop or silent provider fallback remains.

### Day 7 — Freeze and present

- [ ] Run the clean setup and launch walkthrough on the demo machine.
- [ ] Execute the primary representative business-idea scenario end to end.
- [ ] Confirm report view and download for judges.
- [ ] Rehearse the two-minute explanation of problem, pipeline, output, and design principles.
- [ ] Freeze MVP scope; label any stretch work clearly as optional.
