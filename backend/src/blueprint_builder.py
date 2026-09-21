import re
import time
from typing import Any, Dict


# ---------------------------------------------------------------------------
# Section extraction
# ---------------------------------------------------------------------------

def _extract_numbered_section(
    text: str,
    section_number: int,
    fallback: str = "",
) -> str:
    """
    Extract a numbered Markdown section such as:

    ## 1. Delivery Overview
    ...
    ## 2. Business / MVP Scope
    ...

    The extraction stops at the next same-or-higher-level heading.

    This is intentionally based on section numbers rather than loose keywords
    so similarly worded sections cannot be confused with one another.
    """
    if not text:
        return fallback

    lines = text.splitlines()

    start_idx = None
    heading_level = None

    pattern = re.compile(
        rf"^(#{{1,4}})\s*{section_number}\.\s+.+$",
        re.IGNORECASE,
    )

    for i, line in enumerate(lines):
        match = pattern.match(line.strip())
        if match:
            start_idx = i + 1
            heading_level = len(match.group(1))
            break

    if start_idx is None:
        return fallback

    collected = []

    for line in lines[start_idx:]:
        heading_match = re.match(r"^(#{1,4})\s+", line.strip())

        if heading_match and len(heading_match.group(1)) <= heading_level:
            break

        collected.append(line)

    result = "\n".join(collected).strip()
    return result if result else fallback

def _extract_additional_numbered_sections(
    text: str,
    minimum_section_number: int = 15,
) -> str:
    """
    Preserve additional top-level numbered sections produced by the
    Report Writer, starting at minimum_section_number.

    Only level-2 numbered Markdown headings are treated as additional
    document sections. Nested headings inside those sections remain part
    of the section content.
    """
    if not text:
        return ""

    lines = text.splitlines()

    heading_pattern = re.compile(
        r"^##\s+(\d+)\.\s+(.+?)\s*$",
        re.IGNORECASE,
    )

    section_starts = []

    for index, line in enumerate(lines):
        match = heading_pattern.match(line.strip())

        if not match:
            continue

        section_number = int(match.group(1))

        if section_number >= minimum_section_number:
            section_starts.append((index, section_number, match.group(2).strip()))

    if not section_starts:
        return ""

    sections = []

    for position, (start_index, section_number, title) in enumerate(section_starts):
        end_index = (
            section_starts[position + 1][0]
            if position + 1 < len(section_starts)
            else len(lines)
        )

        content_lines = lines[start_index + 1:end_index]

        # Remove trailing horizontal rules and excessive blank lines.
        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)

        while content_lines and not content_lines[-1].strip():
            content_lines.pop()

        content = "\n".join(content_lines).strip()

        if not content:
            continue

        sections.append(
            f"## {section_number}. {title}\n\n{content}"
        )

    return "\n\n---\n\n".join(sections)

# ---------------------------------------------------------------------------
# Generic extraction by explicit keywords
# ---------------------------------------------------------------------------

def _extract_block(
    text: str,
    *keywords: str,
    fallback: str = "",
) -> str:
    """
    Fallback extractor used only when an exact numbered section is unavailable.

    Unlike the old builder, this should not be the primary routing mechanism.
    """
    if not text:
        return fallback

    lines = text.splitlines()
    start_idx = None
    heading_level = 2

    for i, line in enumerate(lines):
        match = re.match(r"^(#{1,4})\s+(.+)$", line.strip())

        if not match:
            continue

        title = match.group(2).strip().lower()

        if any(keyword.lower() in title for keyword in keywords):
            start_idx = i + 1
            heading_level = len(match.group(1))
            break

    if start_idx is None:
        return fallback

    collected = []

    for line in lines[start_idx:]:
        match = re.match(r"^(#{1,4})\s+", line.strip())

        if match and len(match.group(1)) <= heading_level:
            break

        collected.append(line)

    result = "\n".join(collected).strip()
    return result if result else fallback


# ---------------------------------------------------------------------------
# Markdown cleanup
# ---------------------------------------------------------------------------

def _clean_agent_header(text: str) -> str:
    """
    Remove redundant agent-generated top-level section boilerplate.
    """
    if not text:
        return ""

    text = re.sub(
        r"(?im)^#{1,3}\s*section\s*\d+[:\-–—].*$",
        "",
        text,
    )

    text = re.sub(
        r"(?im)^\*synthesized by.*\*$",
        "",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


# ---------------------------------------------------------------------------
# Mermaid extraction
# ---------------------------------------------------------------------------

def _extract_mermaid(text: str) -> str:
    """
    Extract the authoritative Mermaid flowchart from the Solution Architect
    output.

    Preference:
    1. fenced ```mermaid``` block containing flowchart TD
    2. any fenced block containing flowchart TD
    3. raw flowchart TD text up to the next Markdown heading
    """
    if not text:
        return ""

    # Preferred: explicit Mermaid fenced block.
    mermaid_match = re.search(
        r"```mermaid\s*\n([\s\S]*?)```",
        text,
        re.IGNORECASE,
    )

    if mermaid_match:
        diagram = mermaid_match.group(1).strip()

        if re.search(r"\bflowchart\s+TD\b", diagram, re.IGNORECASE):
            return diagram

    # Fallback: any fenced code block containing flowchart TD.
    fenced_matches = re.findall(
        r"```(?:[a-zA-Z0-9_-]+)?\s*\n([\s\S]*?)```",
        text,
        re.IGNORECASE,
    )

    for block in fenced_matches:
        if re.search(r"\bflowchart\s+TD\b", block, re.IGNORECASE):
            return block.strip()

    # Final fallback: locate raw flowchart TD.
    raw_match = re.search(
        r"(?ims)^\s*(flowchart\s+TD\b[\s\S]*?)(?=^\s*#{1,4}\s+|\Z)",
        text,
    )

    if raw_match:
        return raw_match.group(1).strip()

    return ""


# ---------------------------------------------------------------------------
# Paragraph fallback
# ---------------------------------------------------------------------------

def _para(source: str, max_paras: int = 3) -> str:
    """
    Return the first max_paras paragraphs from a source.
    """
    if not source:
        return ""

    paras = [
        paragraph.strip()
        for paragraph in source.split("\n\n")
        if paragraph.strip()
    ]

    return "\n\n".join(paras[:max_paras])


# ---------------------------------------------------------------------------
# Utility: first non-empty value
# ---------------------------------------------------------------------------

def _first_non_empty(*values: str) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()

    return ""


# ---------------------------------------------------------------------------
# Master blueprint builder
# ---------------------------------------------------------------------------

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
    Build the final Enterprise Solution Blueprint.

    Design:
    - Report Writer is the primary source for final section synthesis.
    - Specialist outputs provide deterministic fallbacks.
    - Solution Architect owns the authoritative Mermaid diagram.
    - Section routing is based on explicit section numbers first.
    """

    timestamp = time.strftime(
        "%Y-%m-%d %H:%M:%S UTC",
        time.gmtime(),
    )

    cloud = inputs.get("cloud_preference", "N/A")
    tech_pref = inputs.get("technology_preference", "N/A")
    traffic = inputs.get("expected_daily_traffic", "N/A")
    timeline = inputs.get("delivery_timeline_months", 6)
    country = inputs.get("data_hosting_country", "N/A")
    idea = inputs.get("business_idea", "").strip()

    # Clean outputs before extraction.
    ba = _clean_agent_header(ba_output)
    sa = _clean_agent_header(sa_output)
    ta = _clean_agent_header(ta_output)
    dp = _clean_agent_header(dp_output)
    rw = _clean_agent_header(rw_output)

    # ======================================================================
    # SECTION 1 — Delivery Overview
    # RW owns final synthesis.
    # ======================================================================

    delivery_overview = _first_non_empty(
        _extract_numbered_section(rw, 1),
        _extract_numbered_section(ba, 1),
        _extract_block(rw, "executive", "overview", "summary"),
        _para(ba, 3),
    )

    # ======================================================================
    # SECTION 2 — Business / MVP Scope and Priorities
    # ======================================================================

    mvp_scope = _first_non_empty(
        _extract_numbered_section(rw, 2),
        _extract_numbered_section(ba, 6),
        _extract_block(ba, "mvp scope", "scope boundary"),
        _extract_numbered_section(ba, 1),
    )

    # ======================================================================
    # SECTION 3 — Recommended Technology Stack
    # ======================================================================

    tech_stack = _first_non_empty(
        _extract_numbered_section(rw, 3),
        _extract_numbered_section(ta, 2),
        _extract_block(ta, "authoritative technology", "technology stack"),
        "_Technology stack recommendations not available._",
    )

    # ======================================================================
    # SECTION 4 — Implementation Workstreams
    # ======================================================================

    workstreams = _first_non_empty(
        _extract_numbered_section(rw, 4),
        _extract_numbered_section(dp, 3),
        _extract_block(dp, "implementation workstreams", "epic breakdown"),
        _para(dp, 4),
    )

    # ======================================================================
    # SECTION 5 — Team and Roles
    # ======================================================================

    team_roles = _first_non_empty(
        _extract_numbered_section(rw, 5),
        _extract_numbered_section(dp, 4),
        _extract_block(dp, "team", "staffing"),
        _para(dp, 3),
    )

    # ======================================================================
    # SECTION 6 — Delivery Timeline and Milestones
    # ======================================================================

    timeline_section = _first_non_empty(
        _extract_numbered_section(rw, 6),
        _extract_numbered_section(dp, 5),
        _extract_numbered_section(dp, 6),
        _extract_block(dp, "phase-by-phase", "timeline", "milestone"),
        _para(dp, 4),
    )

    # ======================================================================
    # SECTION 7 — Effort and Complexity
    # ======================================================================

    effort = _first_non_empty(
        _extract_numbered_section(rw, 7),
        _extract_block(
            dp,
            "effort",
            "complexity",
            "estimation",
            "capacity",
            "sizing",
        ),
        _extract_block(
            ta,
            "performance",
            "capacity",
            "sizing",
        ),
        _para(dp, 3),
    )

    # ======================================================================
    # SECTION 8 — Dependencies and Prerequisites
    # ======================================================================

    dependencies = _first_non_empty(
        _extract_numbered_section(rw, 8),
        _extract_numbered_section(dp, 7),
        _extract_numbered_section(ba, 8),
        _extract_block(
            dp,
            "critical path",
            "dependencies",
            "prerequisites",
        ),
        _extract_block(
            ba,
            "assumptions",
            "constraints",
            "dependencies",
        ),
        _para(ba, 2),
    )

    # ======================================================================
    # SECTION 9 — High-Level Solution Architecture
    #
    # RW provides the synthesized prose.
    # SA provides the authoritative Mermaid diagram.
    # ======================================================================
    architecture_prose = _extract_numbered_section(rw, 9)

    # RW Section 9 may contain the same Mermaid diagram required by the
    # Report Writer prompt. Strip it here so the final blueprint contains
    # exactly one architecture diagram, owned by the Solution Architect.
    architecture_prose = re.sub(
        r"```mermaid\s*[\s\S]*?```",
        "",
        architecture_prose,
        flags=re.IGNORECASE,
    ).strip()

    architecture_prose = re.sub(
        r"(?im)^\s*#{1,4}\s*authoritative\s+architecture\s+diagram\s*$",
        "",
        architecture_prose,
    ).strip()

    architecture_prose = re.sub(
        r"\n{3,}",
        "\n\n",
        architecture_prose,
    ).strip()
    architecture_prose = _first_non_empty(
        architecture_prose,
        _extract_numbered_section(sa, 1),
        _extract_numbered_section(sa, 2),
        _extract_numbered_section(sa, 3),
        _extract_numbered_section(sa, 4),
        _para(sa, 5),
    )

    architecture_prose = re.sub(
        r"(?im)^\s*#{1,4}\s*authoritative\s+architecture\s+diagram\s*$",
        "",
        architecture_prose,
    ).strip()

    authoritative_mermaid = _extract_mermaid(sa)

    # If SA did not provide a Mermaid diagram, try RW only as a fallback.
    if not authoritative_mermaid:
        authoritative_mermaid = _extract_mermaid(rw)

    architecture = architecture_prose

    if authoritative_mermaid:
        architecture += (
            "\n\n### Authoritative Architecture Diagram\n\n"
            "```mermaid\n"
            f"{authoritative_mermaid}\n"
            "```"
        )

    if not architecture:
        architecture = "_Architecture design not available._"

    # ======================================================================
    # SECTION 10 — Testing & Quality
    # ======================================================================

    testing = _first_non_empty(
        _extract_numbered_section(rw, 10),
        _extract_numbered_section(dp, 8),
        _extract_block(
            dp,
            "testing",
            "quality",
            "qa",
            "performance",
        ),
        _para(dp, 3),
    )

    # ======================================================================
    # SECTION 11 — Deployment and Release
    # ======================================================================

    deployment = _first_non_empty(
        _extract_numbered_section(rw, 11),
        _extract_numbered_section(dp, 10),
        _extract_block(
            dp,
            "deployment",
            "release",
            "go-live",
            "production",
        ),
        _para(dp, 3),
    )

    # ======================================================================
    # SECTION 12 — Risks and Mitigations
    # ======================================================================

    risks = _first_non_empty(
        _extract_numbered_section(rw, 12),
        _extract_numbered_section(dp, 12),
        _extract_numbered_section(ta, 13),
        _extract_numbered_section(sa, 12),
        _extract_numbered_section(ba, 9),
        _extract_block(
            dp,
            "delivery risk",
            "risk register",
            "mitigation",
        ),
        _extract_block(
            ba,
            "risk register",
            "risk",
        ),
        _para(dp, 3),
    )

    # ======================================================================
    # SECTION 13 — Future Evolution
    # ======================================================================

    future = _first_non_empty(
        _extract_numbered_section(rw, 13),
        _extract_numbered_section(dp, 14),
        _extract_numbered_section(ta, 14),
        _extract_block(
            rw,
            "future",
            "evolution",
            "roadmap",
        ),
        _extract_block(
            dp,
            "future",
            "evolution",
            "roadmap",
        ),
        _para(dp, 3),
    )

    # ======================================================================
    # SECTION 14 — Assumptions and Open Questions
    # ======================================================================

    assumptions = _first_non_empty(
        _extract_numbered_section(rw, 14),
        _extract_numbered_section(ba, 8),
        _extract_numbered_section(ba, 11),
        _extract_block(
            ba,
            "assumptions",
            "open questions",
            "constraints",
        ),
        _para(ba, 4),
    )

    additional_sections = _extract_additional_numbered_sections(
        rw,
        minimum_section_number=15,
    )

    # ======================================================================
    # Final document
    # ======================================================================

    blueprint_md = f"""# Enterprise Solution Blueprint

> **Blueprint ID:** `{run_id}` | **Generated:** `{timestamp}`
> **Cloud Platform:** `{cloud}` | **Technology Preference:** `{tech_pref}`
> **Expected Traffic:** `{traffic}` | **Timeline:** `{timeline} Months`
> **Data Residency:** `{country}`

---

**Business Problem / Idea:**

{idea}

---

## 1. Delivery Overview

{delivery_overview}

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

## 14. Assumptions and Open Questions

{assumptions}

---

{additional_sections}

---

*MindMesh Multi-Agent Engine — Autonomous Enterprise Architecture Blueprinting*
"""

    return blueprint_md