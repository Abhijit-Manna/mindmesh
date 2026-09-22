import re
import time
from typing import Any, Dict


# ---------------------------------------------------------------------------
# Mermaid validation and cleanup
# ---------------------------------------------------------------------------

# Known Mermaid diagram-type keywords (lowercase for comparison).
_MERMAID_DIAGRAM_TYPES = (
    "flowchart", "graph", "sequencediagram", "classdiagram",
    "statediagram", "erdiagram", "gitgraph", "gantt", "pie",
    "mindmap", "timeline", "quadrantchart", "xychart", "journey",
)


def _first_meaningful_line(diagram: str) -> str:
    """Return the first non-empty, non-comment line of a diagram."""
    for line in diagram.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("%%"):
            return stripped
    return ""


def _detect_mermaid_type(diagram: str) -> str | None:
    """Return the Mermaid diagram-type keyword if the first meaningful line
    starts with one, otherwise None."""
    first_line = _first_meaningful_line(diagram)
    if not first_line:
        return None
    first_word = first_line.split(None, 1)[0].lower()
    if first_word in _MERMAID_DIAGRAM_TYPES:
        return first_word
    return None


def _is_whitespace_corrupted(diagram: str) -> bool:
    """
    Detect LLM 'underscore corruption' such as:
        flowchart_TD_____subgraph_ClientLayer_["Client Tier"]

    Healthy Mermaid never glues a diagram-type keyword to an underscore, and
    'subgraph'/'end' statements are never joined to the next keyword by
    underscore runs.
    """
    first_line = _first_meaningful_line(diagram)
    if not first_line:
        return False
    first_word = first_line.split(None, 1)[0].lower()
    for keyword in _MERMAID_DIAGRAM_TYPES:
        if first_word.startswith(keyword + "_"):
            return True
    if re.search(r"\b(end|subgraph)_{2,}\w", diagram):
        return True
    return False


def _repair_whitespace_corruption(diagram: str) -> str:
    """
    Best-effort repair of underscore corruption.

    Runs of 2+ underscores were collapsed newline+indentation; single
    underscores between word characters were collapsed spaces. Quote contents
    are repaired too, because the corruption also hit node labels.
    """
    # Corrupted arrows first: 'Traffic___>' was 'Traffic -->' with the
    # arrow head partially underscored. Restore it before the generic
    # underscore-run replacement turns it into a bogus line break.
    repaired = re.sub(r"_{2,}>", " --> ", diagram)

    repaired = re.sub(r"_{2,}", "\n    ", repaired)
    repaired = re.sub(r"(?<=[A-Za-z0-9\)\]])_(?=[A-Za-z0-9\(\[-])", " ", repaired)

    # A diagram-type keyword glued after the flowchart header (e.g.
    # "flowchart TD sequenceDiagram" or "flowchart TD flowchart LR") must
    # start its own line so that _strip_bogus_flowchart_header can drop the
    # bogus header.
    repaired = re.sub(
        r"(?im)^([ \t]*flowchart[ \t]+(?:TD|LR|TB|BT|RL))[ \t]+"
        r"((?:sequence|class|state|er)diagram|flowchart|graph|gantt|pie"
        r"|mindmap|timeline|gitgraph|journey|quadrantchart|xychart)\b",
        r"\1\n\2",
        repaired,
    )
    return repaired.strip()


def _strip_bogus_flowchart_header(diagram: str) -> str:
    """
    Remove a leading 'flowchart TD' line when the real diagram header
    (e.g. 'sequenceDiagram') appears on the immediately following line.
    Handles degenerate output like:
        flowchart TD
        sequenceDiagram
            participant ...
    """
    lines = diagram.splitlines()
    if len(lines) >= 2:
        first = lines[0].strip().lower()
        second = lines[1].strip()
        second_word = second.split(None, 1)[0].lower() if second else ""
        if (
            first in ("flowchart td", "flowchart lr", "flowchart", "graph td")
            and second_word in _MERMAID_DIAGRAM_TYPES
        ):
            return "\n".join(lines[1:]).lstrip()
    return diagram


def _validate_and_clean_mermaid(diagram: str) -> str:
    """
    Conservative validation and cleanup for Mermaid syntax.

    Fixes the most common issues that actually cause Mermaid syntax errors:
    - LLM whitespace corruption (spaces/newlines collapsed to underscores)
      is detected and repaired on a best-effort basis
    - Missing 'flowchart TD' header (prepends it) — flowcharts only
    - 'graph TD' -> 'flowchart TD' (deprecated syntax)
    - Node IDs with spaces in definitions (e.g. "My Node[Label]" -> "My_Node[Label]")
    - Trailing garbage after the diagram (prose, markdown, etc.)

    Non-flowchart diagrams (sequenceDiagram, erDiagram, gantt, ...) are
    preserved as-is apart from whitespace repair: flowchart-specific fixes
    (header injection, node-ID rewriting, line truncation) previously
    destroyed them — e.g. a 'sequenceDiagram' was reduced to a bare
    'flowchart TD' line.
    """
    if not diagram:
        return diagram

    cleaned = diagram.strip()

    # --- 0. Repair LLM whitespace corruption (spaces/newlines -> underscores)
    if _is_whitespace_corrupted(cleaned):
        cleaned = _strip_bogus_flowchart_header(
            _repair_whitespace_corruption(cleaned)
        )

    # --- 1. Detect diagram type; only assume flowchart when unknown ---
    diagram_type = _detect_mermaid_type(cleaned)
    if diagram_type is None:
        diagram_type = "flowchart"
        cleaned = 'flowchart TD\n' + cleaned

    # --- 2. Normalize deprecated 'graph TD' to 'flowchart TD' ---
    if re.match(r'^\s*graph\s+TD\b', cleaned, re.IGNORECASE):
        cleaned = re.sub(r'^\s*graph\s+TD\b', 'flowchart TD', cleaned, flags=re.IGNORECASE)
        diagram_type = "flowchart"

    if diagram_type != "flowchart":
        # Non-flowchart diagram: flowchart-specific fixes would corrupt it.
        # Only normalize excessive blank lines.
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned.strip()

    # --- 3. Fix node IDs with spaces in definitions (flowcharts only) ---
    # Only match lines that look like node definitions:  ID[Label]  or  ID(Label)
    # where the ID contains spaces. We are careful not to match Mermaid keywords
    # like subgraph, end, classDef, class, click, linkStyle, style, direction.
    _MERMAID_KEYWORDS = {
        'subgraph', 'end', 'classDef', 'class', 'click', 'linkStyle',
        'style', 'direction', 'flowchart', 'graph', 'actor', 'participant',
        'Note', 'alt', 'else', 'opt', 'loop', 'par', 'rect', 'autonumber',
    }

    def _fix_node_id_line(line: str) -> str:
        """Fix spaces in node ID for a single line, if it is a node definition."""
        stripped = line.strip()
        # Skip empty lines, comments, and known keywords
        if not stripped or stripped.startswith('%'):
            return line
        first_word = stripped.split(None, 1)[0]
        if first_word.lower() in {kw.lower() for kw in _MERMAID_KEYWORDS}:
            return line
        # Match:  <id with spaces>[label]  or  <id with spaces>(label)
        # The ID must start with a letter and can contain spaces before the bracket/paren.
        m = re.match(
            r'^(\s*)([a-zA-Z][a-zA-Z0-9_\-\s]*?)\s*(\[\[?|\(\()(.*)$',
            line,
        )
        if not m:
            return line
        indent, node_id, bracket, rest = m.groups()
        # Only fix if the ID actually contains spaces
        if ' ' not in node_id.strip():
            return line
        clean_id = re.sub(r'\s+', '_', node_id.strip())
        return f'{indent}{clean_id}{bracket}{rest}'

    lines = cleaned.split('\n')
    lines = [_fix_node_id_line(line) for line in lines]
    cleaned = '\n'.join(lines)

    # --- 4. Remove trailing garbage after the diagram (flowcharts only) ---
    # Stop at the first blank line that is followed by non-diagram content,
    # or at the first line that doesn't look like Mermaid syntax at all.
    _VALID_LINE_RE = re.compile(
        r'^\s*(flowchart|graph|subgraph|end|classDef|class|click|linkStyle|style|direction'
        r'|[a-zA-Z_][a-zA-Z0-9_\-.]*\s*(\[\[?|\(\(?|\{\{?|-->|---|\.\.|==>|==|<->|->|<-|<--))',
        re.IGNORECASE,
    )
    _BLANK_RE = re.compile(r'^\s*$')

    valid_lines = []
    blank_seen = False
    for line in lines:
        stripped = line.strip()
        if _BLANK_RE.match(line):
            blank_seen = True
            valid_lines.append(line)
            continue
        if blank_seen and not _VALID_LINE_RE.match(stripped):
            # Blank line followed by non-diagram content -> stop
            break
        blank_seen = False
        if _VALID_LINE_RE.match(stripped):
            valid_lines.append(line)
        else:
            # First line that doesn't look like Mermaid syntax -> stop
            break

    cleaned = '\n'.join(valid_lines).strip()

    # Remove excessive blank lines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return cleaned


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
            return _validate_and_clean_mermaid(diagram)

    # Fallback: any fenced code block containing flowchart TD.
    fenced_matches = re.findall(
        r"```(?:[a-zA-Z0-9_-]+)?\s*\n([\s\S]*?)```",
        text,
        re.IGNORECASE,
    )

    for block in fenced_matches:
        if re.search(r"\bflowchart\s+TD\b", block, re.IGNORECASE):
            return _validate_and_clean_mermaid(block.strip())

    # Final fallback: locate raw flowchart TD.
    raw_match = re.search(
        r"(?ims)^\s*(flowchart\s+TD\b[\s\S]*?)(?=^\s*#{1,4}\s+|\Z)",
        text,
    )

    if raw_match:
        return _validate_and_clean_mermaid(raw_match.group(1).strip())

    return ""


# A supporting-diagram caption line, e.g.:
#   **Supporting Diagram 1: Instant P2P Transfer Request Sequence**
#   #### Supporting Diagram 2 - Data Residency Lifecycle Flow
#   Supporting Diagram 3: Deployment & Blue-Green Release Pipeline
_SUPPORTING_CAPTION_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?\**\s*supporting\s+diagram\s*#?\s*(\d+)\s*"
    r"[:\-–—]\s*(.+?)\**\s*$",
    re.IGNORECASE,
)

# Lines that terminate a caption block.
_HEADING_LINE_RE = re.compile(r"^\s*#{1,6}\s+\S")
_HR_LINE_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
_FENCE_LINE_RE = re.compile(r"^\s*```")

# A standalone "Supporting Diagrams" section heading (no number, no title).
_SUPPORTING_SECTION_HEADING_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?\**\s*supporting\s+diagrams\s*(?:[:\-–—]\s*)?\**\s*$",
    re.IGNORECASE,
)

# A standalone "Authoritative Architecture Diagram" heading.
_AUTHORITATIVE_HEADING_RE = re.compile(
    r"^\s*#{1,4}\s*authoritative\s+architecture\s+diagram\s*$",
    re.IGNORECASE,
)

# Leading "Explanation:" label variants on caption explanation text.
# Handles "*Explanation:*", "**Explanation:**", "_Explanation:_",
# "Explanation:", and "**Explanation** -" forms.
_EXPLANATION_LABEL_RE = re.compile(
    r"^\s*[*_]{0,2}\s*explanation\b[*_\s]*[:\-–—][*_\s]*",
    re.IGNORECASE,
)


def _extract_rw_supporting_diagram_units(text: str) -> tuple[list, str]:
    """
    Extract supporting diagram units (caption + Mermaid block) from the
    Report Writer §9 text.

    The first Mermaid block in §9 is the authoritative diagram (owned by the
    Solution Architect). Every later Mermaid block is a supporting diagram.

    Captions ("Supporting Diagram N: <name>" plus the explanation text that
    follows) are paired with the supporting Mermaid blocks, so each diagram
    can be presented together with its own name and explanation — instead of
    all captions being grouped in one place and the diagrams dumped
    separately.

    Captions are paired with supporting diagrams by document order (the Nth
    supporting block belongs to the Nth caption). This holds for every
    layout the Report Writer produces: captions grouped together before the
    diagrams, captions interleaved between diagrams, or each caption placed
    directly after its diagram.

    Returns:
        (units, cleaned_text)
        units: list of dicts {"name", "explanation", "mermaid"} in diagram
               order. Diagrams without a caption receive a generic name and
               an empty explanation; captions without a diagram are dropped.
        cleaned_text: the input with every Mermaid fence, every caption
               block, and any standalone "Supporting Diagrams" /
               "Authoritative Architecture Diagram" heading removed, so no
               orphaned captions remain in the prose.
    """
    if not text:
        return [], ""

    lines = text.splitlines()
    total = len(lines)

    mermaid_blocks = []   # (start_idx, end_idx_exclusive, code)
    caption_blocks = []   # (start_idx, end_idx_exclusive, name, explanation)

    i = 0
    while i < total:
        line = lines[i]

        if not _FENCE_LINE_RE.match(line):
            caption_match = _SUPPORTING_CAPTION_RE.match(line)
            if caption_match:
                name = caption_match.group(2).strip().strip("*").strip()
                # Collect the explanation text until the next caption,
                # heading, horizontal rule, or fenced block.
                j = i + 1
                while j < total:
                    nxt = lines[j]
                    if (
                        _SUPPORTING_CAPTION_RE.match(nxt)
                        or _HEADING_LINE_RE.match(nxt)
                        or _HR_LINE_RE.match(nxt)
                        or _FENCE_LINE_RE.match(nxt)
                    ):
                        break
                    j += 1
                explanation = "\n".join(lines[i + 1 : j]).strip()
                caption_blocks.append((i, j, name, explanation))
                i = j
                continue
            i += 1
            continue

        # Fenced block: capture Mermaid code, skip other languages.
        is_mermaid = line.strip().lower().startswith("```mermaid")
        j = i + 1
        while j < total and not _FENCE_LINE_RE.match(lines[j]):
            j += 1
        if is_mermaid:
            code = "\n".join(lines[i + 1 : j]).strip()
            mermaid_blocks.append((i, min(j + 1, total), code))
        i = j + 1 if j < total else total

    # Pair captions with supporting diagrams by document order: the Nth
    # supporting Mermaid block belongs to the Nth caption. This is correct
    # whether captions are grouped before the diagrams, interleaved between
    # them, or placed directly after each diagram. The first Mermaid block
    # is the authoritative diagram (SA-owned) and has no caption of its own.
    units = []
    for d_idx, (_start, _end, code) in enumerate(mermaid_blocks[1:], start=1):
        cleaned_code = _validate_and_clean_mermaid(code)
        if not cleaned_code:
            continue
        name, explanation = "", ""
        caption_idx = d_idx - 1
        if caption_idx < len(caption_blocks):
            _s, _e, name, explanation = caption_blocks[caption_idx]
        units.append(
            {
                "name": name,
                "explanation": explanation,
                "mermaid": cleaned_code,
            }
        )

    # --- Cleaned prose: drop fences, caption blocks, and the standalone ---
    # --- "Supporting Diagrams" heading ------------------------------------
    remove = set()
    for start, end, _code in mermaid_blocks:
        remove.update(range(start, end))
    for start, end, _name, _expl in caption_blocks:
        remove.update(range(start, end))
    for idx, line in enumerate(lines):
        if (
            _SUPPORTING_SECTION_HEADING_RE.match(line)
            or _AUTHORITATIVE_HEADING_RE.match(line)
        ):
            remove.add(idx)

    kept = [line for idx, line in enumerate(lines) if idx not in remove]
    cleaned_text = re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()

    # Strip leading/trailing blank lines and horizontal rules left behind
    # by the removals.
    kept_lines = cleaned_text.splitlines() if cleaned_text else []

    def _is_blank_or_rule(value: str) -> bool:
        return not value.strip() or bool(_HR_LINE_RE.match(value))

    start, end = 0, len(kept_lines)
    while start < end and _is_blank_or_rule(kept_lines[start]):
        start += 1
    while end > start and _is_blank_or_rule(kept_lines[end - 1]):
        end -= 1

    return units, "\n".join(kept_lines[start:end]).strip()


def _is_substantive(text: str) -> bool:
    """
    Check whether §9 prose contains real architecture reasoning.

    A caption-only remnant (e.g., three orphaned diagram descriptions
    left after stripping the authoritative Mermaid) has zero architecture
    value. This guard prevents it from shadowing the Solution Architect
    fallback in the block chain below.
    """
    if not text or len(text.strip()) < 50:
        return False

    architecture_terms = [
        "component", "service", "api", "database", "server", "security",
        "authentication", "authorization", "scalab",
        "resilien", "integration", "infrastructure", "network",
        "credential", "secret", "gateway", "load balancer", "firewall",
        "cache", "queue", "microservice", "throughput", "latency",
        "container", "orchestrat", "workload", "persistence", "topology",
        "boundary", "timeout", "retry", "auth", "encrypt", "token",
    ]
    lower = text.lower()
    matched_terms = [term for term in architecture_terms if term in lower]
    has_architecture = len(matched_terms) >= 2

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    has_substance = any(len(p.split()) > 15 for p in paragraphs)

    return has_architecture and has_substance


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
    # Supporting diagrams from RW are preserved and appended after the
    # authoritative one — each emitted as diagram + name + explanation.
    # ======================================================================
    architecture_prose = _extract_numbered_section(rw, 9)

    # Preserve RW supporting diagrams (with their captions) before stripping.
    # The first mermaid block is the authoritative diagram (owned by SA);
    # remaining blocks are supporting diagrams that must not be lost. The
    # extractor also removes caption blocks and Mermaid fences from the
    # prose, so no orphaned diagram names/explanations remain grouped at
    # the top of the section.
    rw_supporting_units, architecture_prose = _extract_rw_supporting_diagram_units(
        architecture_prose
    )

    # Any remaining "Authoritative Architecture Diagram" heading is stripped
    # here so the final blueprint contains exactly one authoritative
    # architecture diagram, owned by SA and emitted below.
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

    # Caption-only remnants (e.g., orphaned diagram captions) have zero
    # architecture value. Fall through to SA fallbacks instead of
    # shadowing them.
    if _is_substantive(architecture_prose):
        architecture_prose = _first_non_empty(
            architecture_prose,
            _extract_numbered_section(sa, 1),
            _extract_numbered_section(sa, 2),
            _extract_numbered_section(sa, 3),
            _extract_numbered_section(sa, 4),
            _para(sa, 5),
        )
    else:
        architecture_prose = _first_non_empty(
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

    # Append RW supporting diagrams after the authoritative one. Each unit is
    # emitted as: diagram, then its name, then the explanation text, so every
    # diagram appears together with its own caption instead of all captions
    # being grouped separately from the diagrams.
    if rw_supporting_units:
        unit_blocks = []
        for idx, unit in enumerate(rw_supporting_units, start=1):
            title = unit["name"].strip()
            display_name = (
                f"Supporting Diagram {idx}: {title}" if title
                else f"Supporting Diagram {idx}"
            )
            parts = [
                "```mermaid\n"
                f"{unit['mermaid']}\n"
                "```",
                f"**{display_name}**",
            ]
            explanation = _EXPLANATION_LABEL_RE.sub(
                "", unit["explanation"], count=1
            ).strip()
            if explanation:
                parts.append(f"*Explanation:* {explanation}")
            unit_blocks.append("\n\n".join(parts))
        architecture += (
            "\n\n### Supporting Diagrams\n\n" + "\n\n".join(unit_blocks)
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