import re
import time
from typing import Any, Dict


# ---------------------------------------------------------------------------
# Utility: extract a subsection of agent output by heading keyword
# ---------------------------------------------------------------------------

def _extract_block(text: str, *keywords: str, fallback: str = "") -> str:
    """
    Extract text from `text` that falls under the first heading whose content
    matches any of the supplied keywords (case-insensitive). Returns the block
    up to the next same-or-higher-level heading, or `fallback` if not found.
    """
    if not text:
        return fallback

    lines = text.splitlines()
    start_idx = None
    heading_level = 2  # default

    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            level = len(m.group(1))
            title = m.group(2).lower()
            if any(kw.lower() in title for kw in keywords):
                start_idx = i + 1
                heading_level = level
                break

    if start_idx is None:
        return fallback

    # Collect until a heading of same or higher level appears
    collected = []
    for line in lines[start_idx:]:
        m = re.match(r"^(#{1,4})\s+", line)
        if m and len(m.group(1)) <= heading_level:
            break
        collected.append(line)

    result = "\n".join(collected).strip()
    return result if result else fallback


def _clean_agent_header(text: str) -> str:
    """
    Strip boilerplate first-line agent preambles (e.g. '## Section 1: …',
    '*Synthesized by …*') that would be redundant when embedded under our
    document headings.
    """
    text = re.sub(r"(?im)^#{1,3}\s*section\s*\d+[:\-–—].*$", "", text)
    text = re.sub(r"(?im)^\*synthesized by.*\*$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def build_master_blueprint(
    inputs: Dict[str, Any],
    ba_output: str,
    sa_output: str,
    ta_output: str,
    dp_output: str,
    rw_output: str = "",
    run_id: str = "run_master",
) -> str:
    """
    Synthesize all specialist agent deliverables into a single, continuous,
    professional Enterprise Solution Blueprint organized under 14 standard
    headings. Content is routed from the appropriate agent to each heading
    rather than dumped in raw numbered sections.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    cloud = inputs.get("cloud_preference", "N/A")
    tech_pref = inputs.get("technology_preference", "N/A")
    traffic = inputs.get("expected_daily_traffic", "N/A")
    timeline = inputs.get("delivery_timeline_months", 6)
    country = inputs.get("data_hosting_country", "N/A")
    idea = inputs.get("business_idea", "").strip()

    # Clean boilerplate headers from each agent output
    ba = _clean_agent_header(ba_output)
    sa = _clean_agent_header(sa_output)
    ta = _clean_agent_header(ta_output)
    dp = _clean_agent_header(dp_output)
    rw = _clean_agent_header(rw_output)

    # ------------------------------------------------------------------
    # Route content to the 14 required sections.
    # Primary source for each section is chosen by topic ownership;
    # supplementary detail is pulled via _extract_block where useful.
    # ------------------------------------------------------------------

    # 1. Delivery Overview — executive summary (RW first, fallback to BA intro)
    delivery_overview = (
        _extract_block(rw, "executive", "overview", "summary", "strategic")
        or _extract_block(ba, "overview", "summary", "objective")
        or (rw.split("\n\n")[0] if rw else ba.split("\n\n")[0] if ba else "")
    )

    # 2. Business / MVP Scope — BA owns this
    mvp_scope = (
        _extract_block(ba, "mvp", "scope", "priority", "functional requirement",
                       "core feature", "user stor", "stakeholder")
        or ba
    )

    # 3. Technology Stack — TA owns this entirely
    tech_stack = ta or "_Technology stack recommendations not available._"

    # 4. Implementation Workstreams — DP owns this
    workstreams = (
        _extract_block(dp, "workstream", "sprint", "phase", "milestone",
                       "iteration", "implementation plan")
        or dp
    )

    # 5. Team & Roles — DP owns this
    team_roles = (
        _extract_block(dp, "team", "role", "resource", "staffing", "personnel",
                       "engineer", "headcount")
        or _extract_block(dp, "team")
        or ""
    )

    # 6. Delivery Timeline & Milestones — DP owns this
    timeline_section = (
        _extract_block(dp, "timeline", "milestone", "schedule", "gantt",
                       "delivery plan", "roadmap")
        or ""
    )

    # 7. Effort & Complexity — DP owns this
    effort = (
        _extract_block(dp, "effort", "complexity", "estimation", "story point",
                       "capacity", "sizing")
        or ""
    )

    # 8. Dependencies & Prerequisites — BA + DP
    dependencies = (
        _extract_block(dp, "dependenc", "prerequisite", "blocker", "integration")
        or _extract_block(ba, "dependenc", "prerequisite", "assumption")
        or ""
    )

    # 9. High-Level Solution Architecture — SA owns; ASCII diagram from RW
    architecture = sa or "_Architecture design not available._"
    ascii_diagram = _extract_block(rw, "ascii", "diagram", "topology", "architecture")

    # 10. Testing & Quality — DP owns this
    testing = (
        _extract_block(dp, "test", "quality", "qa", "acceptance", "coverage")
        or ""
    )

    # 11. Deployment & Release — DP + SA
    deployment = (
        _extract_block(dp, "deploy", "release", "ci/cd", "pipeline", "rollout",
                       "production", "environment")
        or _extract_block(sa, "deploy", "release", "ci/cd")
        or ""
    )

    # 12. Risks & Mitigations — DP owns this
    risks = (
        _extract_block(dp, "risk", "mitigation", "issue", "concern", "challenge")
        or ""
    )

    # 13. Future Evolution — RW + SA
    future = (
        _extract_block(rw, "future", "evolution", "roadmap", "phase 2", "next",
                       "scale", "expansion")
        or _extract_block(sa, "future", "evolution", "scalab")
        or ""
    )

    # 14. Assumptions & Open Questions — BA owns this
    assumptions = (
        _extract_block(ba, "assumption", "open question", "constraint", "risk",
                       "dependency")
        or _extract_block(ba, "assumption")
        or ""
    )

    # ------------------------------------------------------------------
    # For sections where _extract_block returns empty (agent didn't use
    # that exact heading), fall back to a short relevant portion of the
    # owning agent's full output to avoid blank sections.
    # ------------------------------------------------------------------
    def _para(source: str, max_paras: int = 3) -> str:
        """Return the first `max_paras` paragraphs of source."""
        paras = [p for p in source.split("\n\n") if p.strip()]
        return "\n\n".join(paras[:max_paras])

    if not team_roles and dp:
        team_roles = _para(dp, 3)
    if not timeline_section and dp:
        timeline_section = _para(dp, 4)
    if not effort and dp:
        effort = _para(dp, 3)
    if not dependencies and ba:
        dependencies = _para(ba, 2)
    if not testing and dp:
        testing = _para(dp, 3)
    if not deployment and dp:
        deployment = _para(dp, 3)
    if not risks and dp:
        risks = _para(dp, 3)
    if not future:
        future = _para(rw or sa, 3)
    if not assumptions and ba:
        assumptions = _para(ba, 3)

    # ------------------------------------------------------------------
    # Sections 4–8 and 10–12 may share similar content from `dp`.
    # Deduplicate by using distinct sub-extractions when available,
    # but avoid blank sections by falling back gracefully.
    # ------------------------------------------------------------------

    # Compose the blueprint
    blueprint_md = f"""# Enterprise Solution Blueprint

> **Blueprint ID:** `{run_id}` | **Generated:** `{timestamp}`
> **Cloud Platform:** `{cloud}` | **Technology Preference:** `{tech_pref}`
> **Expected Traffic:** `{traffic}` | **Timeline:** `{timeline} Months` | **Data Residency:** `{country}`

---

**Business Problem / Idea:**
{idea}

---

## 1. Delivery Overview

{delivery_overview or _para(ba or rw, 3)}

---

## 2. Business / MVP Scope and Priorities

{mvp_scope}

---

## 3. Recommended Technology Stack

{tech_stack}

---

## 4. Implementation Workstreams

{workstreams}

---

## 5. Recommended Team and Roles

{team_roles}

---

## 6. Delivery Timeline and Milestones

{timeline_section}

---

## 7. Effort & Complexity Assessment

{effort}

---

## 8. Dependencies and Prerequisites

{dependencies}

---

## 9. High-Level Solution Architecture

{architecture}
{chr(10) + ascii_diagram if ascii_diagram else ""}

---

## 10. Testing & Quality Strategy

{testing}

---

## 11. Deployment & Release Strategy

{deployment}

---

## 12. Delivery Risks & Mitigations

{risks}

---

## 13. Future Evolution

{future}

---

## 14. Assumptions & Open Questions

{assumptions}

---

*MindMesh Multi-Agent Engine — Autonomous Enterprise Architecture Blueprinting*
"""
    return blueprint_md
