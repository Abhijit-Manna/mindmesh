# SolutionForge AI — API Contracts

**Status:** MVP implementation contract  
**Base URL:** `http://localhost:8000`  
**API prefix:** `/api/v1`  
**Transport:** JSON over HTTP  
**Authentication:** None for the local MVP; authentication and authorization must be added before public deployment.

This document is the routing and payload source of truth for the Streamlit frontend, FastAPI backend, integration tests, and demo scripts. All application routes belong under `/api/v1`, except the service health route and FastAPI's generated documentation routes.

The generation flow is a typed JSON pipeline. The validated user input is given to the Business Analyst. The accepted JSON output from that agent is passed as context to the Solution Architect; that accepted JSON output is passed to the Technology Advisor; and that accepted JSON output is passed to the Delivery Planner. The final Delivery Planner JSON is assembled into the canonical Markdown report and converted into a sanitized, downloadable HTML file.

## 1. Endpoint inventory

| Method | Path | Endpoint role | Main caller | Success |
| --- | --- | --- | --- | --- |
| `GET` | `/health` | Confirms that the API process is alive; does not run agents or dependency checks | Frontend, local scripts, deployment probes | `200 OK` |
| `POST` | `/api/v1/blueprints` | Starts a new full blueprint run from user input and executes all four agents in sequence | Streamlit Generate Blueprint action | `201 Created` |
| `GET` | `/api/v1/blueprints/{run_id}` | Retrieves a completed blueprint without regenerating it | Streamlit restore/refresh action | `200 OK` |
| `POST` | `/api/v1/blueprints/{run_id}/regenerate` | Regenerates one selected agent and every downstream agent, creating a new child run | Streamlit regeneration action or API client | `201 Created` |
| `GET` | `/docs` | Interactive Swagger UI for exploring and testing the API | Developers | `200 OK` |
| `GET` | `/redoc` | Human-readable generated API reference | Developers | `200 OK` |
| `GET` | `/openapi.json` | Machine-readable OpenAPI schema for tooling and contract validation | API tools and CI | `200 OK` |

The table defines the standard HTTP methods, URL paths, functions, primary callers, and expected success responses for the system's API:

GET /health: Confirms that the API process is alive. It does not run deep agents or dependency checks. It is primarily used by frontend components, local scripts, and deployment probes, returning a 200 OK.

POST /api/v1/blueprints: Starts a brand new, full blueprint run using user input. It executes all four system agents in sequential order. This is called by the Streamlit "Generate Blueprint" action and returns a 201 Created.

GET /api/v1/blueprints/{run_id}: Retrieves a previously completed blueprint run without re-running or regenerating it. Used by Streamlit restore/refresh actions, returning a 200 OK.POST /api/v1/blueprints/{run_id}/regenerate: Regenerates a specific selected agent and any downstream agents following it. This process creates a new "child run" instead of modifying the old one. It is triggered by Streamlit regeneration actions or external API clients, returning a 201 Created.

Documentation Routes:
GET /docs: Serves the interactive Swagger UI for developers to explore and test the API (200 OK).

GET /redoc: Serves a human-readable, generated API reference page for developers (200 OK).GET /openapi.json: Serves the raw machine-readable OpenAPI schema used by API tools and CI/CD validation pipelines (200 OK).

The API does not expose separate agent, research, evaluation, retry, or HTML-file routes. Agent retries remain internal to a run. Regeneration is different: it is a public operation that starts a new child run from a selected stage. The generated HTML is returned in the blueprint response; the frontend must not call internal CrewAI functions directly.

There is no `GET /api/v1/blueprints` list endpoint in the local MVP because no persistence layer is currently defined. There is no asynchronous job or polling endpoint: generation and regeneration are synchronous and the request remains open until the workflow completes or fails.

## 2. Routing layout

The FastAPI application should be organized as follows:

```text
backend/src/
├── main.py                    # Creates FastAPI app and includes routers
├── routes/
│   ├── health.py              # GET /health
│   └── blueprints.py              # /api/v1/blueprints routes, including regeneration
├── models.py                  # Shared Pydantic contracts
├── orchestration.py           # CrewAI execution and lifecycle events
├── evaluation.py
├── reporting.py
└── ...
```

Recommended registration:

```python
app.include_router(health_router)
app.include_router(blueprint_router, prefix="/api/v1")
```

The router must define `POST /blueprints`, `GET /blueprints/{run_id}`, and `POST /blueprints/{run_id}/regenerate`. Do not register the same route under both `/generate-blueprint` and `/api/v1/blueprints`; the latter is the canonical path.

## 3. Common HTTP rules

### Request headers

Clients must send:

```http
Content-Type: application/json
Accept: application/json
```

`X-Request-ID` is optional. If supplied, the server must validate its length, include it in logs, and return it in the response header. If absent, the server generates a request ID. `X-Request-ID` is a correlation identifier and is not the blueprint `run_id`.

### Response headers

Successful and error responses should include:

```http
Content-Type: application/json
X-Request-ID: <correlation-id>
```

The `html` field in a blueprint response is a string containing the generated HTML document. It is not returned as `text/html` by a separate route.

### JSON naming

JSON field names use `snake_case`. Enum values are lowercase except for the cloud values shown below. Unknown request fields should be rejected rather than silently ignored.

### Size and timeout policy

- `business_idea`: 20–10,000 characters after trimming.
- `expected_daily_traffic`: 1–200 characters after trimming.
- `data_hosting_country`: 2–100 characters after trimming.
- `delivery_timeline_months`: integer from 1 through 60.
- The server must apply a configured request timeout and return an explicit error if generation exceeds it.
- Do not log complete request bodies or generated reports by default.

## 4. `GET /health`

Returns process liveness and build information. This route must not call an LLM, CrewAI, search tool, or persistence layer.

### Response — `200 OK`

```json
{
  "status": "ok",
  "service": "solutionforge-api",
  "version": "0.1.0"
}
```

`status` is always `ok` for a successful response. A failed process cannot serve this route; dependency readiness is not implied by this endpoint.

## 5. `POST /api/v1/blueprints`

Validates the request, runs Business Analyst → Solution Architect → Technology Advisor → Delivery Planner, evaluates each stage, passes accepted JSON output between stages, converts the final result to Markdown and HTML, and returns the complete blueprint.

### Request body — `BlueprintRequest`

```json
{
  "business_idea": "A customer-facing platform that replaces a manual operational process. Customers submit requests, track status, and receive notifications; internal staff review and manage requests.",
  "technology_preference": "open-source",
  "cloud_preference": "AWS",
  "expected_daily_traffic": "Approximately 20,000 daily active users",
  "delivery_timeline_months": 6,
  "data_hosting_country": "India"
}
```

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `business_idea` | string | Yes | Trimmed, non-blank, 20–10,000 characters; domain-agnostic free text |
| `technology_preference` | enum | Yes | `open-source` or `enterprise` |
| `cloud_preference` | enum | Yes | `AWS`, `Azure`, `GCP`, or `none` |
| `expected_daily_traffic` | string | Yes | Trimmed, non-blank traffic description |
| `delivery_timeline_months` | integer | Yes | Whole number from 1 through 60 |
| `data_hosting_country` | string | Yes | Trimmed, non-blank country or jurisdiction |

The API must preserve these constraints in the context passed to every relevant agent. `Technology Advisor` owns the authoritative recommended stack, and `Delivery Planner` must consume that accepted output rather than inventing a competing stack.

### Agent JSON handoff contract

Each agent must return a JSON object that validates against its role-specific contract. JSON is the only data format used for inter-agent handoff; Markdown must not be passed between agents as the primary context format.

#### 1. Business Analyst output

```json
{
  "agent": "Business Analyst",
  "status": "accepted",
  "users_and_stakeholders": [
    {
      "name": "Customer",
      "goals": ["Submit and track a request"],
      "needs": ["Status visibility", "Notifications"]
    }
  ],
  "functional_requirements": [
    {
      "id": "FR-001",
      "title": "Submit request",
      "description": "A customer can submit a request.",
      "priority": "must-have"
    }
  ],
  "non_functional_requirements": [
    {
      "category": "security",
      "requirement": "Protect customer data with authenticated access",
      "priority": "must-have"
    }
  ],
  "mvp_scope": ["Request submission", "Status tracking", "Staff review"],
  "future_scope": ["Advanced automation", "Analytics"],
  "assumptions": ["The business will provide workflow rules"],
  "constraints": ["Six-month delivery timeline", "India data hosting"],
  "risks": ["Unconfirmed regulatory requirements"],
  "open_questions": ["What notification channels are required?"],
  "sources": []
}
```

The Business Analyst must not select concrete implementation technologies. `sources` contains source URLs returned by the CrewAI search tool and may be empty when search is disabled.

#### 2. Solution Architect output

```json
{
  "agent": "Solution Architect",
  "status": "accepted",
  "architecture_style": {
    "name": "Modular monolith",
    "rationale": "Supports a small team and the stated MVP timeline"
  },
  "components": [
    {
      "name": "Request management API",
      "responsibility": "Validate, store, and expose request state"
    }
  ],
  "data_flow": [
    "Customer submits request",
    "API validates and stores request",
    "Staff reviews request",
    "Notification is sent on status change"
  ],
  "data_storage": [
    {
      "data": "Requests and status history",
      "boundary": "Primary application database",
      "residency": "India"
    }
  ],
  "security_controls": ["Authentication", "Role-based authorization", "Audit logging"],
  "scalability_approach": ["Stateless API", "Horizontal scaling when traffic requires it"],
  "mvp_boundary": ["One deployable application", "One primary database"],
  "future_evolution": ["Extract services only when independently scaling"],
  "avoided_overengineering": ["No event mesh or multi-region deployment for the MVP"],
  "trade_offs": ["Simpler delivery now in exchange for less independent component scaling"],
  "risks": ["A later service split may require domain-boundary refactoring"],
  "sources": []
}
```

The Solution Architect receives the complete accepted Business Analyst JSON plus the original validated request. It must describe capabilities and boundaries without replacing the Technology Advisor's stack decision.

#### 3. Technology Advisor output

```json
{
  "agent": "Technology Advisor",
  "status": "accepted",
  "recommended_stack": {
    "frontend": {
      "technology": "Recommended frontend technology",
      "rationale": "Fits the product and delivery constraints",
      "trade_offs": ["Trade-off"],
      "risks": ["Risk"]
    },
    "backend": {
      "technology": "Recommended backend technology",
      "rationale": "Fits the API and team constraints",
      "trade_offs": ["Trade-off"],
      "risks": ["Risk"]
    },
    "database": {
      "technology": "Recommended database",
      "rationale": "Fits the data and scale requirements",
      "trade_offs": ["Trade-off"],
      "risks": ["Risk"]
    },
    "cloud": {
      "provider": "AWS",
      "services": ["Recommended services"],
      "rationale": "Respects the submitted cloud preference and data residency",
      "trade_offs": ["Trade-off"],
      "risks": ["Risk"]
    }
  },
  "alternatives_considered": [
    {
      "capability": "Backend",
      "alternative": "Alternative technology",
      "reason_not_selected": "Less suitable for the submitted constraints"
    }
  ],
  "technology_preference_alignment": "open-source",
  "cloud_preference_alignment": "AWS",
  "complexity_assessment": "Moderate",
  "lock_in_considerations": ["Documented interfaces reduce provider coupling"],
  "sources": []
}
```

The Technology Advisor receives the accepted Business Analyst and Solution Architect JSON objects. Its `recommended_stack` is authoritative. The Delivery Planner must use these exact recommendations in its plan and may not silently substitute technologies.

#### 4. Delivery Planner output

```json
{
  "agent": "Delivery Planner",
  "status": "accepted",
  "delivery_overview": "Decision-oriented summary of the proposed MVP",
  "business_mvp_scope_priorities": [],
  "implementation_workstreams": [
    {
      "name": "Backend foundation",
      "outcomes": ["Working API and persistence"],
      "dependencies": [],
      "months": [1, 2]
    }
  ],
  "team_and_roles": [
    {
      "role": "Backend engineer",
      "responsibilities": ["Implement API and integration tests"]
    }
  ],
  "milestones": [
    {
      "name": "MVP beta",
      "target_month": 5,
      "exit_criteria": ["Core workflow passes acceptance tests"]
    }
  ],
  "effort_and_complexity": "Moderate effort with the highest risk in workflow clarification",
  "dependencies_and_prerequisites": ["Confirmed business rules", "Cloud account"],
  "testing_strategy": ["Unit", "integration", "acceptance", "security"],
  "deployment_strategy": ["Staged deployment", "Rollback procedure"],
  "risks_and_mitigations": [
    {
      "risk": "Timeline expansion",
      "mitigation": "Protect MVP scope and defer future features"
    }
  ],
  "future_evolution": ["Add advanced automation after MVP validation"],
  "assumptions_and_open_questions": [],
  "architecture_diagram": "User -> API -> Database",
  "used_recommended_stack": true,
  "sources": []
}
```

The Delivery Planner receives all three accepted upstream JSON objects and the original request. It must fit milestones within `delivery_timeline_months`, preserve the Technology Advisor stack, and provide enough structured content for final report assembly.

### Handoff and evaluation rules

For each stage:

1. Build the agent input from the original request and accepted upstream JSON objects.
2. Run the agent task.
3. Parse the result as JSON; invalid JSON is a failed attempt.
4. Validate the JSON against the role schema; schema failure is a failed attempt.
5. Run deterministic and optional quality evaluation.
6. If accepted, store the JSON and pass it unchanged as context to the next agent.
7. If rejected, pass evaluator feedback into the next bounded retry; never pass rejected JSON downstream.

The run fails with a non-success response when an agent exhausts its retry budget. The response must not contain a partial or success-shaped blueprint.

### Response — `201 Created`

```json
{
  "run_id": "run_01J8EXAMPLE",
  "status": "completed",
  "markdown": "# Solution Blueprint\n\n## Delivery Overview\n...",
  "html": "<!doctype html><html>...</html>",
  "run_metadata": {
    "attempts": {
      "Business Analyst": 1,
      "Solution Architect": 2,
      "Technology Advisor": 1,
      "Delivery Planner": 1
    },
    "search_enabled": true,
    "accepted_evaluations": 4,
    "source_count": 8,
    "duration_ms": 42310,
    "handoff_format": "json",
    "handoff_sequence": [
      "request -> Business Analyst",
      "Business Analyst JSON -> Solution Architect",
      "Solution Architect JSON -> Technology Advisor",
      "Technology Advisor JSON -> Delivery Planner"
    ],
    "download": {
      "filename": "solution-blueprint-run_01J8EXAMPLE.html",
      "media_type": "text/html",
      "available": true
    }
  },
  "agents": [
    "Business Analyst",
    "Solution Architect",
    "Technology Advisor",
    "Delivery Planner"
  ]
}
```

| Field | Type | Meaning |
| --- | --- | --- |
| `run_id` | string | Unique identifier for this generation run |
| `status` | literal | `completed` |
| `markdown` | string | Canonical generated report source |
| `html` | string | Styled, sanitized presentation version of `markdown` |
| `run_metadata.attempts` | object | Attempt count per agent, including the first attempt |
| `run_metadata.search_enabled` | boolean | Whether the built-in CrewAI search tool was enabled |
| `run_metadata.accepted_evaluations` | integer | Number of accepted agent evaluation gates; expected to be 4 |
| `run_metadata.source_count` | integer | Number of retained search sources |
| `run_metadata.duration_ms` | integer | Total server-side generation duration |
| `run_metadata.handoff_format` | literal | Always `json` for the MVP |
| `run_metadata.handoff_sequence` | string array | Ordered record of JSON context handoffs |
| `run_metadata.download` | object | Download metadata for the generated HTML artifact |
| `agents` | string array | Ordered agent names; must remain in the four-agent sequence |

The Markdown must contain all 14 report headings defined in `SOLUTION_BLUEPRINT.md`. The API must validate required headings and consistency before returning `201`. The HTML must be generated from the accepted final Delivery Planner JSON, contain the same report content, be sanitized, and be downloadable by the frontend as `solution-blueprint-{run_id}.html`.

### HTML download contract

The API returns the complete HTML document in `html`; it does not return a filesystem path and must not expose server-local file locations. The Streamlit frontend creates the download action from this field:

```text
download_data = response["html"]
download_filename = response["run_metadata"]["download"]["filename"]
download_mime_type = response["run_metadata"]["download"]["media_type"]
```

The download must:

- use the exact sanitized HTML returned by the API;
- use the filename `solution-blueprint-{run_id}.html`;
- use media type `text/html`;
- open as a standalone document without requiring the API server;
- not include secrets, internal prompts, rejected agent attempts, or raw provider diagnostics.

No separate HTML download route is required for the MVP. If a future deployment adds one, it must return the same artifact and use `Content-Disposition: attachment; filename="solution-blueprint-{run_id}.html"`.

### Processing contract

1. Validate the JSON body with Pydantic.
2. Create a `run_id` and correlation metadata.
3. Execute the four CrewAI agents using `Process.sequential`.
4. Attach CrewAI's built-in `WebsiteSearchTool` where enabled.
5. Parse and validate the Business Analyst JSON, then pass it to the Solution Architect.
6. Parse and validate the Solution Architect JSON, then pass it to the Technology Advisor.
7. Parse and validate the Technology Advisor JSON, then pass it to the Delivery Planner.
8. Evaluate every JSON output before handing it downstream.
9. Retry failed outputs only within `MAX_AGENT_RETRIES`, including evaluator feedback.
10. Assemble the accepted Delivery Planner JSON into the final Markdown report.
11. Convert the Markdown to sanitized HTML and create download metadata.
12. Reject the run explicitly if retries are exhausted, search fails in a required mode, report validation fails, or HTML conversion fails.
13. Return the accepted Markdown, sanitized HTML, and non-sensitive metadata.

## 6. `GET /api/v1/blueprints/{run_id}`

Retrieves a previously generated blueprint by its run ID.

The MVP may use an in-memory run store with a bounded retention policy. A future persistent store can replace it without changing this route or response contract. If the process restarted or the run was evicted, return `404`; do not regenerate the blueprint.

### Path parameter

| Parameter | Type | Rules |
| --- | --- | --- |
| `run_id` | string | Non-empty opaque ID returned by `POST /api/v1/blueprints`; no path traversal or arbitrary file access |

### Response — `200 OK`

Returns the same `BlueprintResponse` shape as `POST /api/v1/blueprints`, with the original `run_id`.

### Not found — `404 Not Found`

```json
{
  "error": {
    "code": "BLUEPRINT_NOT_FOUND",
    "message": "No blueprint was found for run_id 'run_01J8EXAMPLE'.",
    "request_id": "req_01J8EXAMPLE",
    "details": {}
  }
}
```

## 7. `POST /api/v1/blueprints/{run_id}/regenerate`

Regenerates a completed blueprint from a selected agent stage. This endpoint creates a new child run and never overwrites the original run.

### Request body — `RegenerateBlueprintRequest`

```json
{
  "from_agent": "Solution Architect",
  "reason": "The architecture is too complex for the six-month delivery timeline."
}
```

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `from_agent` | enum | Yes | `Business Analyst`, `Solution Architect`, `Technology Advisor`, or `Delivery Planner` |
| `reason` | string | Yes | Trimmed, non-blank explanation, 10–2,000 characters |

### Regeneration behavior

The server loads the original request and accepted JSON outputs from the parent run:

| `from_agent` | Reused from parent | Regenerated |
| --- | --- | --- |
| `Business Analyst` | Original request only | Business Analyst → Solution Architect → Technology Advisor → Delivery Planner |
| `Solution Architect` | Request and accepted Business Analyst JSON | Solution Architect → Technology Advisor → Delivery Planner |
| `Technology Advisor` | Request, Business Analyst JSON, and Solution Architect JSON | Technology Advisor → Delivery Planner |
| `Delivery Planner` | Request and all accepted upstream JSON | Delivery Planner only |

The selected agent receives the regeneration reason as additional instruction. Every regenerated agent must still return schema-valid JSON, pass evaluation, and provide accepted JSON to the next regenerated agent. If a regenerated stage fails, its normal bounded retry policy applies.

Regeneration must:

1. Validate `run_id` and the request body.
2. Confirm the parent run exists and has `status: completed`.
3. Load the original request and accepted JSON handoff state.
4. Preserve accepted upstream JSON before `from_agent`.
5. Start a new run with a new `run_id` and `parent_run_id`.
6. Regenerate the selected agent and all downstream agents.
7. Rebuild the final Markdown and sanitized HTML from the new Delivery Planner JSON.
8. Preserve the original run unchanged and return the new child result.

### Response — `201 Created`

Returns the standard `BlueprintResponse` shape, with these additional metadata fields:

```json
{
  "run_id": "run_01J8CHILD",
  "status": "completed",
  "markdown": "# Solution Blueprint\n\n## Delivery Overview\n...",
  "html": "<!doctype html><html>...</html>",
  "run_metadata": {
    "parent_run_id": "run_01J8PARENT",
    "regenerated_from_agent": "Solution Architect",
    "regeneration_reason": "The architecture is too complex for the six-month delivery timeline.",
    "handoff_format": "json",
    "handoff_sequence": [
      "parent Business Analyst JSON -> regenerated Solution Architect",
      "regenerated Solution Architect JSON -> regenerated Technology Advisor",
      "regenerated Technology Advisor JSON -> regenerated Delivery Planner"
    ],
    "download": {
      "filename": "solution-blueprint-run_01J8CHILD.html",
      "media_type": "text/html",
      "available": true
    }
  },
  "agents": [
    "Business Analyst",
    "Solution Architect",
    "Technology Advisor",
    "Delivery Planner"
  ]
}
```

`GET /api/v1/blueprints/{run_id}` can retrieve the new child run using its new `run_id`. The parent run remains available according to the run-store retention policy.

### Regeneration errors

- `404 BLUEPRINT_NOT_FOUND` if the parent `run_id` is unknown or expired.
- `409 BLUEPRINT_NOT_REGENERATABLE` if the parent run is incomplete, failed, or does not contain the accepted JSON handoff state required for regeneration.
- `422 VALIDATION_ERROR` if `from_agent` or `reason` is invalid.
- `500 AGENT_RETRY_EXHAUSTED` if a regenerated agent cannot produce accepted JSON within the retry budget.
- `504 GENERATION_TIMEOUT` if regeneration exceeds the configured timeout.

## 8. Error contract

All application errors use this shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid fields.",
    "request_id": "req_01J8EXAMPLE",
    "details": {
      "fields": {
        "cloud_preference": "Input should be 'AWS', 'Azure', 'GCP' or 'none'"
      }
    }
  }
}
```

| Status | Code | When |
| --- | --- | --- |
| `400` | `MALFORMED_JSON` | Body is not valid JSON |
| `404` | `ROUTE_NOT_FOUND` | No application route matches the URL |
| `404` | `BLUEPRINT_NOT_FOUND` | `run_id` is not available |
| `409` | `BLUEPRINT_NOT_REGENERATABLE` | Parent run is not completed or lacks accepted JSON handoff state |
| `405` | `METHOD_NOT_ALLOWED` | Path exists but HTTP method is unsupported |
| `415` | `UNSUPPORTED_MEDIA_TYPE` | Request is not JSON |
| `422` | `VALIDATION_ERROR` | Pydantic field or business validation fails |
| `500` | `AGENT_RETRY_EXHAUSTED` | An agent could not produce accepted JSON within the retry budget |
| `500` | `GENERATION_FAILED` | CrewAI, evaluation, or required search processing fails |
| `500` | `REPORT_CONVERSION_FAILED` | Markdown validation or HTML conversion fails |
| `503` | `SERVICE_UNAVAILABLE` | Server is alive but a required configured dependency is unavailable |
| `504` | `GENERATION_TIMEOUT` | Configured generation timeout is exceeded |

Error requirements:

- Never return `200` or `201` with an empty, partial, or unverified blueprint.
- Do not expose API keys, provider stack traces, prompts, full business input, or raw model output in the client error.
- Log the detailed exception server-side with `request_id`, `run_id` when available, stage, and a redacted error.
- Preserve FastAPI's standard validation locations in `details.fields` where possible.

## 9. Validation examples

### Invalid enum — `422`

```json
{
  "business_idea": "Build a platform for customers to submit and track service requests.",
  "technology_preference": "free",
  "cloud_preference": "AWS",
  "expected_daily_traffic": "10,000 users/day",
  "delivery_timeline_months": 6,
  "data_hosting_country": "India"
}
```

### Blank idea — `422`

```json
{
  "business_idea": "   ",
  "technology_preference": "open-source",
  "cloud_preference": "none",
  "expected_daily_traffic": "1,000 users/day",
  "delivery_timeline_months": 3,
  "data_hosting_country": "India"
}
```

## 10. Frontend integration

The Streamlit frontend calls only these application routes:

1. `GET /health` before or during local connectivity checks.
2. `POST /api/v1/blueprints` when the user selects **Generate Blueprint**.
3. `GET /api/v1/blueprints/{run_id}` only when restoring or refreshing a known result.
4. `POST /api/v1/blueprints/{run_id}/regenerate` when the user requests regeneration from a selected agent.

The frontend must:

- Preserve all six form values after an error.
- Disable duplicate generation submissions while a request is active.
- Show validation messages from `error.details.fields`.
- Show a readable generation failure without fabricating report content.
- Render the returned `html` and offer it as the download payload.
- Display agent order and retry metadata from `run_metadata`.
- Display the regeneration reason and parent run relationship when a child run is returned.
- Treat the returned child `run_id` as the current result while retaining the parent `run_id` for history.

## 11. Contract testing checklist

- [ ] `GET /health` returns `200` without invoking CrewAI.
- [ ] `POST /api/v1/blueprints` accepts the reference request and returns `201`.
- [ ] The response contains non-empty Markdown and HTML.
- [ ] Each agent returns schema-valid JSON before its output is handed to the next agent.
- [ ] Rejected or invalid JSON is never passed downstream.
- [ ] The handoff sequence is request → Business Analyst JSON → Solution Architect JSON → Technology Advisor JSON → Delivery Planner JSON.
- [ ] All 14 report headings are present in Markdown.
- [ ] Agent order is Business Analyst → Solution Architect → Technology Advisor → Delivery Planner.
- [ ] Invalid enums, blank strings, missing fields, and invalid timeline values return `422`.
- [ ] Unsupported content types return `415`.
- [ ] CrewAI/evaluator/search failures return explicit non-success errors.
- [ ] Retry exhaustion never returns a successful response.
- [ ] `GET /api/v1/blueprints/{run_id}` returns the stored result.
- [ ] Unknown run IDs return `404` with `BLUEPRINT_NOT_FOUND`.
- [ ] Regeneration from each agent preserves earlier accepted JSON and reruns the selected and downstream agents.
- [ ] Regeneration creates a new `run_id` and does not overwrite the parent run.
- [ ] Regeneration returns `parent_run_id`, `regenerated_from_agent`, and `regeneration_reason`.
- [ ] Incomplete or failed parent runs return `409 BLUEPRINT_NOT_REGENERATABLE`.
- [ ] Download metadata contains the expected `.html` filename and `text/html` media type.
- [ ] The downloaded HTML is standalone, sanitized, and matches the response `html` field.
- [ ] `/docs` and `/openapi.json` expose the same request and response models.
- [ ] Error responses include a correlation `request_id` and never expose secrets.
