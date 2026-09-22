# MindMesh — Fixes Applied

This document tracks all fixes applied to the MindMesh codebase from the
adversarial audit checklist. Fixes are grouped by priority.

---

## MUST FIX — Blockers (all done)

### 1. Section extraction — all four per-agent tabs now return content

**Problem:** The section parser searched for headings like `## Section 1:` but
the blueprint builder emits `## 1. Delivery Overview`. Every tab fell through
to a fallback that showed the entire document in each tab.

**What was changed:**
- `backend/src/utils/section_parser.py` — completely rewritten. Now uses
  `_extract_numbered_section` from `blueprint_builder.py` to map each tab to
  its canonical numbered heading: BA→§2, SA→§9, TA→§3, DP→§4+§5+§6 combined.
- `frontend/views/dashboard_view.py` — deleted the broken local
  `extract_sections_from_markdown` function (200+ lines) and its `import re`.
  The view now uses the API's `sections` field directly, no client-side parser.

**How we verified:** Ran the parser against all 14 records in the SQLite
database. Before the fix: every section returned 0 characters. After the fix:
BA=684 chars, SA=1501 chars, TA=858 chars, DP=1238 chars (on the real record).

---

### 2. Section 9 collapse — architecture section no longer empty

**Problem:** The Report Writer's Section 9 had its Mermaid diagram stripped,
leaving only orphaned diagram captions. The "first non-empty" check picked up
those captions instead of falling through to the Solution Architect's
substantive architecture prose. Result: the core section of an architecture
product was diagram captions.

**What was changed in `backend/src/blueprint_builder.py`:**
- Added `_extract_rw_supporting_diagrams()` — extracts the 3 supporting
  Mermaid diagrams from the Report Writer's §9 before stripping. These are
  preserved and appended after the SA's authoritative diagram.
- Added `_is_substantive()` — checks whether §9 text has real architecture
  reasoning (at least 2 architecture terms like "component", "service",
  "database" + at least one substantive paragraph > 15 words). Caption-only
  remnants return False, so the fallback chain reaches the SA's prose.
- Changed §9 logic: if RW prose is substantive, use it first (with SA
  fallback). If not substantive, go straight to SA fallbacks.
- The SA's authoritative Mermaid diagram is always included. RW supporting
  diagrams are appended after it.

---

### 3. Quality gate now actually gates

**Problem:** `parsed["passed"] = score >= threshold` at `evaluation.py:85`
overwrote the evaluator's own verdict. The 934 lines of hard-gate rules in the
evaluator prompts were completely ignored. Every run passed regardless of
quality.

**What was changed in `backend/src/evaluation.py`:**
- Changed the gate to `passed = bool(evaluator_said_passed) and score >= threshold`.
  Now both the LLM evaluator AND the score threshold must agree to pass.
- Added `structural_check()` — a fast, deterministic check that runs BEFORE
  the expensive evaluator LLM call. It checks: minimum output length (100
  chars), Solution Architect must include `flowchart TD`, Report Writer must
  have all 14 section headings, sections 4/6/9/12 must each be over 800 chars.
  If structural check fails, returns immediate failure without an LLM call.
- Added `parse_ok` field to evaluation results — tracks whether the
  evaluator's JSON output was successfully parsed.

---

## Critical Fixes (all done)

### 4. Evaluator parse failure no longer corrupts specialist prompts

**Problem:** On a JSON parse failure, the evaluator returned
`remediation_guidance = "Return a JSON object using the required evaluation
schema."` and the pipeline appended this to the specialist's task
description. The Business Analyst's next attempt was told to emit evaluation
JSON instead of a requirements document.

**What was changed:**
- `backend/src/evaluation.py` — fixed the JSON parsing regex at line 22.
  `re.search(r"(\{.*?\})")` was non-greedy and truncated at the first `}`.
  Replaced with `json.JSONDecoder().raw_decode()` from the first `{`, which
  correctly handles nested braces. Also added to exception handling
  (`ValueError`).
- `backend/src/evaluation.py` — on parse failure, returns `parse_ok: False`.
- `backend/src/pipeline.py` — before appending evaluator remediation to a
  specialist's prompt, checks `parse_ok`. If False, skips the append entirely
  and retries the specialist without corrupted instructions.

---

### 5. Generated HTML is now sanitised (XSS fix)

**Problem:** `html_converter.py` used `markdown.markdown(extensions=["extra"])`
with no sanitizer. User text and search results could reach a document
designed to be downloaded and emailed. The code also deliberately reversed
entity escaping and used Mermaid `securityLevel: "loose"`.

**What was changed in `backend/src/utils/html_converter.py`:**
- Added `import bleach` and the `_sanitize_html()` function with an
  allowlist of safe tags (`div`, `p`, `table`, `pre`, `code`, etc.) and
  attributes (`class`, `id`, `href`, `src`, `alt`). Strips scripts,
  iframes, event handlers, and javascript URLs.
- Sanitization runs after markdown conversion and before Mermaid block
  processing, so it catches all user-supplied HTML while preserving safe
  structure and Mermaid code blocks.
- Changed Mermaid `securityLevel: "loose"` → `"strict"`.
- Deleted `_decode_html_entities()` function. Replaced its single call in
  `convert_mermaid_blocks` with `html_lib.unescape()` from the standard
  library (same behavior, less custom code).

**Frontend XSS fixes:**
- `frontend/components/sidebar.py` — added `import html as html_lib`. All
  four interpolated values (`display_title`, `created`, `tag_text`, `r_id`)
  now use `html_lib.escape()` before insertion into `unsafe_allow_html=True`
  markdown.
- `frontend/views/execution_view.py` — added `import html as html_lib`. All
  dynamic values extracted from server events (`msg`, `agent_name`,
  `stream_error`) are now HTML-escaped at their extraction point, protecting
  every downstream rendering including the terminal display with
  `unsafe_allow_html=True`.

### 6. API security locked down

**Problem:** `main.py:18-24` had `allow_origins=["*"]` with
`allow_credentials=True`, reflecting any caller's Origin with zero
authentication. Any page could read every stored business idea, delete
history, and burn the team's Gemini quota. `run_id` was an unvalidated
path parameter allowing arbitrary `.md`/`.html` read + delete via path
traversal. No input bounds on any field.

**What was changed:**
- `backend/main.py` — narrowed CORS to `allow_origins=["http://localhost:8501"]`,
  `allow_credentials=False`, explicit methods (`GET`, `POST`, `DELETE`, `OPTIONS`),
  explicit headers (`Content-Type`, `Accept`, `X-API-Key`).
- `backend/src/config.py` — added `API_SECRET_KEY` setting (empty by default
  for development, enables shared-secret auth when set).
- `backend/src/routes/blueprint.py` — multiple changes:
  - Added `verify_api_key` dependency: checks `X-API-Key` header against
    `API_SECRET_KEY`. Skipped when key is empty (dev mode). Applied to
    all blueprint routes via `Depends(verify_api_key)`.
  - Added `run_id` validation (`re.fullmatch(r"[0-9a-f]{12}", run_id)`)
    on both read and delete handlers → 400 if invalid. Blocks `../x`,
    `..\x`, and other path traversal attempts.
- Added input bounds to `BlueprintRequest`:
     `business_idea: Field(min_length=15, max_length=5000)`,
     `delivery_pipeline_months: int = Field(ge=1, le=36)`, and
     length bounds on all string fields. Invalid input → 422 automatically.

---

### Credibility Landmines (all done)

- Deleted `frontend/dummy_data.py` (205 dead lines with fabricated data including `get_dummy_response()` returning fabricated `run_metadata`).
- Untracked database: `git rm --cached backend/db/mindmesh.db` (1.4 MB, 13 of 14 records were junk backfill with `Modern Stack`/`Cloud Native` defaults).
- Purged unsupported claims:
  - `html_converter.py:508`: "Generated autonomously by SolutionForge AI • Verified Enterprise Architecture Document" → "Generated by MindMesh"
  - `header.py:17-19`: "Endless consistent architectures… Precision engineering across every run" → "Consistent architectures… Precise engineering on every run"
  - `pipeline.py:296`: dropped "autonomous" from init message
  - `execution_view.py:15`: dropped "autonomous" from caption
- Fixed dead form validation in `form_view.py`: replaced select-box sentinel checks with `.strip()` non-empty for text inputs; kept sentinel checks for actual selectboxes.
- Deleted dead `TRAFFIC_OPTIONS` / `COUNTRY_OPTIONS` from `constants.py`.
- Removed duplicate `cur_country` line in `form_view.py`.
- Aligned validation message: help text now says "Minimum 15 characters" (was 20, matching code and README).

---

## Remaining Fixes (not yet applied)
- Instrument latency and tokens per stage (StageMetrics dataclass, attach to
  SSE events, persist to a run_metrics table, render per-run table).
- Add 10 deterministic tests (no API key required) covering all blockers.
- Add a two-record database seed script to replace the untracked local
  database for demos and development.
- Add a semaphore to cap concurrent blueprint generations and protect API
  capacity.

### Demo Hardening
- Set `verbose=False` on all six agents (currently broadcasting full prompts).
- Increase client SSE timeout from 300s to 900s.
- Add SSE heartbeat every ~15s.
- Add `MERMAID_SSR=0` env switch to skip server-side Mermaid rendering.
- Pre-warm the model/client before the demo.
- Pre-generate a fallback result before the demo.
- Rehearse the complete demo flow and recovery path.

### SHOULD FIX IF TIME
- Typed contracts between stages (Deliverable/Evaluation Pydantic models).
- Evaluator `temperature=0.0` (currently 0.4 for all agents including grader).
- Startup model preflight (fail fast on bad model name).
- Persist a `running` row at pipeline init (browser disconnect loses paid work).
- Degrade gracefully on evaluator failure (don't kill entire run).
- SQLite hardening (WAL mode, atomic writes).
- Fix backfill regexes in `db.py` (they search for strings the builder never
  emits).
- Reconcile README with code (LOG_LEVEL undocumented, sections always empty,
  etc.).
- Add LICENSE file.
- Declare Node.js/npx as a prerequisite.
