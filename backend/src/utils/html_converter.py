import re
import subprocess
import tempfile
import os
import html as html_lib
import shutil
import markdown
import bleach

from src.blueprint_builder import (
    _MERMAID_DIAGRAM_TYPES,
    _is_renderable_mermaid,
    _is_whitespace_corrupted,
    _normalize_diagram_token,
    _normalize_mermaid_fences,
    _validate_and_clean_mermaid,
)


def _ssr_enabled() -> bool:
    """Server-side SVG pre-rendering toggle (MERMAID_SSR, default on).

    When disabled, diagrams skip the npx/mmdc pre-render and go straight to
    the client-side Mermaid.js fallback (requires internet in the browser).
    """
    try:
        from src.config import settings
        return bool(getattr(settings, "MERMAID_SSR", True))
    except Exception:
        return os.environ.get("MERMAID_SSR", "1").strip().lower() not in (
            "0", "false", "no", "off",
        )


def _looks_like_mermaid(code: str) -> bool:
    """Heuristic: does this code block contain a Mermaid diagram?

    Checks the first meaningful line for a Mermaid diagram-type keyword
    (version suffixes such as ``stateDiagram-v2`` are normalized away).
    Used to catch mis-tagged fences (```flowchart instead of ```mermaid)
    while leaving genuine code samples untouched.
    """
    for line in code.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        first_word = _normalize_diagram_token(stripped.split(None, 1)[0])
        return first_word in _MERMAID_DIAGRAM_TYPES
    return False


BLEACH_ALLOWED_TAGS = [
    "a", "abbr", "b", "blockquote", "br", "caption", "cite", "code",
    "col", "colgroup", "dd", "del", "div", "dl", "dt", "em", "figcaption",
    "figure", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img",
    "li", "mark", "ol", "p", "pre", "q", "s", "small", "span", "strong",
    "sub", "sup", "table", "tbody", "td", "tfoot", "th", "thead", "tr",
    "u", "ul", "var", "wbr",
]

BLEACH_ALLOWED_ATTRS = {
    "*": ["class", "id"],
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan"],
}


def _convert_latex_to_text(text: str) -> str:
    """
    Convert simple LaTeX math expressions in prose to readable text.
    Only processes inline math ($...$) - leaves code blocks and Mermaid untouched.

    Uses word-based replacements to avoid HTML escaping by markdown parser.
    """
    if not text:
        return text

    # Pattern to match inline math: $...$ but not $$...$$ (display math)
    # and not inside code blocks
    def replace_inline_math(match):
        latex = match.group(1)
        # Common simple conversions - use words to avoid HTML escaping
        conversions = {
            r'\\text\{ms\}': 'ms',
            r'\\text\{s\}': 's',
            r'\\%': '%',
            r'\\ge': 'at least ',
            r'\\le': 'at most ',
            r'\\gt': 'greater than ',
            r'\\lt': 'less than ',
            r'\\approx': 'approx. ',
            r'\\times': 'x',
            r'\\cdot': '*',
            r'\\pm': '+/-',
            r'\\infty': 'infinity',
            # Raw comparison operators that appear in math expressions
            r'>=': 'at least ',
            r'<=': 'at most ',
            r'>': 'greater than ',
            r'<': 'less than ',
        }
        result = latex
        for pattern, replacement in conversions.items():
            result = re.sub(pattern, replacement, result)
        # Remove any remaining LaTeX commands like \text{...}
        result = re.sub(r'\\text\{([^}]+)\}', r'\1', result)
        # Remove braces
        result = result.replace('{', '').replace('}', '')
        # Clean up any remaining backslashes
        result = result.replace('\\', '')
        return result

    # Replace $...$ but not $$...$$
    # Negative lookbehind/lookahead to avoid display math
    text = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', replace_inline_math, text)
    return text


def _sanitize_html(html_content: str) -> str:
    """
    Strip dangerous HTML (XSS vectors) while preserving safe content.

    Applied after markdown conversion and before templating. Uses bleach
    with an allowlist of tags and attributes required by the document
    stylesheet. Event handlers, script/iframe/object tags, and
    javascript: URLs are removed.
    """
    return bleach.clean(
        html_content,
        tags=BLEACH_ALLOWED_TAGS,
        attributes=BLEACH_ALLOWED_ATTRS,
        strip=True,
    )


def remove_emojis(text: str) -> str:
    """Remove emoji characters from text for clean corporate document styling."""
    emoji_pattern = re.compile(
        "["
        "\U0001F000-\U0001F9FF"  # Emoticons, Pictographs, Supplemental Symbols
        "\U0001FA00-\U0001FAFF"  # Chess, Symbols and Pictographs Extended-A
        "\U00002600-\U000027BF"  # Miscellaneous Symbols, Dingbats
        "\U00002300-\U000023FF"  # Miscellaneous Technical
        "\U00002B00-\U00002BFF"  # Miscellaneous Symbols and Arrows
        "]+",
        flags=re.UNICODE
    )
    # Strip emojis and normalize spaces
    cleaned = emoji_pattern.sub("", text)
    # Also remove common emoji surrogate artefacts if any
    cleaned = re.sub(r"[🏛🎯📋🏗⚡🚀💡🔒📈⏱️🎉🗑️👁️💳🏥📦📑⚙️🧪🟢🔴🟡]", "", cleaned)
    return cleaned


def mermaid_to_svg(mermaid_code: str) -> str | None:
    """
    Convert Mermaid diagram code to an inline SVG string using the
    @mermaid-js/mermaid-cli package (mmdc) via npx.

    Returns the SVG string on success, or None if conversion fails
    (e.g. mmdc not available, invalid syntax, timeout).

    The SVG is stripped of the XML declaration and DOCTYPE so it can
    be safely embedded inline inside an HTML document.
    """
    mermaid_code = mermaid_code.strip()
    if not mermaid_code:
        return None

    npx_path = shutil.which("npx")
    if npx_path is None:
        print("[html_converter] npx is unavailable; using client-side Mermaid rendering.")
        return None

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "diagram.mmd")
            output_path = os.path.join(tmpdir, "diagram.svg")

            with open(input_path, "w", encoding="utf-8") as f:
                f.write(mermaid_code)

            result = subprocess.run(
                [
                    npx_path, "-y", "@mermaid-js/mermaid-cli",
                    "-i", input_path,
                    "-o", output_path,
                    "--backgroundColor", "white",
                    "--quiet",
                ],
                capture_output=True,
                text=True,
                timeout=120,  # mmdc downloads on first run; allow generous timeout
                cwd=tmpdir,
            )

            if result.returncode != 0:
                print(
                    f"[html_converter] mmdc exited with code {result.returncode}.\n"
                    f"stderr: {result.stderr[:500]}"
                )
                return None

            if not os.path.exists(output_path):
                print("[html_converter] mmdc produced no output file.")
                return None

            with open(output_path, "r", encoding="utf-8") as f:
                svg_content = f.read()

            # Strip XML declaration and DOCTYPE — unsafe for inline embedding
            svg_content = re.sub(r"<\?xml[^?]*\?>", "", svg_content, flags=re.IGNORECASE)
            svg_content = re.sub(
                r"<!DOCTYPE[^>]*>", "", svg_content, flags=re.IGNORECASE | re.DOTALL
            )
            svg_content = svg_content.strip()

            return svg_content

    except FileNotFoundError:
        print("[html_converter] npx could not be started; using client-side Mermaid rendering.")
        return None
    except subprocess.TimeoutExpired:
        print("[html_converter] mmdc timed out.")
        return None
    except Exception as exc:
        print(f"[html_converter] mermaid_to_svg error: {exc}")
        return None


def _extract_mermaid_code(raw: str) -> str:
    """
    Extract the raw Mermaid code from various possible containers:
    - Markdown fenced block:  ```mermaid\\n...\\n```
    - Already-decoded text that starts with a Mermaid keyword
    Returns the cleaned Mermaid code string.
    """
    raw = raw.strip()

    # Strip stray fence remnants (e.g. a doubled opener "```mermaid" or
    # "```flowchart TD" that survived inside the block).
    raw = "\n".join(
        line for line in raw.splitlines()
        if not line.strip().startswith("```")
    ).strip()

    # Case 1: Markdown fenced block (may survive if called on raw markdown)
    fence_match = re.match(
        r"^```(?:mermaid)?\s*\n(.*?)\n```\s*$", raw, re.DOTALL | re.IGNORECASE
    )
    if fence_match:
        return fence_match.group(1).strip()

    # Case 2: The text is already clean Mermaid (starts with known diagram types)
    first_word = _normalize_diagram_token(raw.split(None, 1)[0]) if raw else ""
    if first_word in _MERMAID_DIAGRAM_TYPES:
        return raw

    return raw


def _diagram_source_block(mermaid_code: str, note: str) -> str:
    """Fallback for a diagram that Mermaid cannot parse.

    Mermaid renders unparseable input as a large "Syntax error in text" error
    graphic, which hides the architecture information completely. When a
    diagram is known to be unparseable the source is shown instead, so the
    reader still gets the content in a readable form.
    """
    return (
        '<div class="diagram-fallback">'
        f'<p class="diagram-fallback-note">{note}</p>'
        f"<pre><code>{html_lib.escape(mermaid_code, quote=False)}</code></pre>"
        "</div>"
    )


def _client_side_diagram(mermaid_code: str) -> str:
    """Client-side Mermaid.js fallback.

    The diagram source is kept next to the rendered diagram so the content is
    never lost when the Mermaid CDN is unavailable in the browser; the
    converter's inline script reveals it when rendering fails.
    """
    escaped = html_lib.escape(mermaid_code, quote=False)
    return (
        '<div class="diagram-container">'
        f'<div class="mermaid">{escaped}</div>'
        '<details class="diagram-source">'
        "<summary>Diagram source (Mermaid)</summary>"
        f"<pre><code>{escaped}</code></pre>"
        "</details>"
        "</div>"
    )


def convert_mermaid_blocks(html: str) -> str:
    """
    Find fenced-code blocks that the Markdown library converted to
    ``<pre><code class="language-...">...</code></pre>`` and replace Mermaid
    diagrams with either:
      - An inline ``<svg>`` (pre-rendered server-side via npx mmdc), wrapped in
        a styled ``<div class="architecture-diagram">``, OR
      - A ``<div class="mermaid">`` fallback for client-side Mermaid.js rendering
        if server-side conversion is unavailable or fails.

    Any language class is accepted (language-mermaid, language-flowchart,
    ...) — the block content decides: only blocks whose first meaningful
    line is a Mermaid diagram keyword are converted, so genuine code samples
    are left untouched.
    """
    pattern = r'<pre><code(?: class="language-([^"]*)")?>(.*?)</code></pre>'

    def replace_mermaid(match: re.Match) -> str:
        lang = (match.group(1) or "").strip().lower()
        raw_code = match.group(2)

        # Decode HTML entities introduced by the Markdown library
        mermaid_code = html_lib.unescape(raw_code)
        mermaid_code = _extract_mermaid_code(mermaid_code)

        if not (
            _looks_like_mermaid(mermaid_code)
            or _is_whitespace_corrupted(mermaid_code)
        ):
            # Not a diagram (genuine code sample): leave untouched.
            # Whitespace-corrupted diagrams ('flowchart_TD_____subgraph_...')
            # hide their diagram keyword from _looks_like_mermaid, so they
            # are admitted through the gate as well and repaired by the
            # cleaner below — otherwise they stay in the document as broken
            # code boxes instead of rendered diagrams.
            return match.group(0)

        # Repair/normalize the diagram (fixes LLM whitespace corruption such
        # as 'flowchart_TD_____subgraph_...' and preserves non-flowchart
        # diagram types) before attempting to render it.
        mermaid_code = _validate_and_clean_mermaid(mermaid_code)
        if not mermaid_code:
            return match.group(0)

        # A diagram Mermaid cannot parse at all (no diagram type, unclosed
        # 'subgraph', ...) is never handed to the renderer: it would come back
        # as Mermaid's "Syntax error in text" artwork. Show its source instead.
        if not _is_renderable_mermaid(mermaid_code):
            return _diagram_source_block(
                mermaid_code,
                "This diagram could not be rendered, so its Mermaid source is "
                "shown instead.",
            )

        # Attempt server-side SVG pre-rendering (unless MERMAID_SSR=0).
        svg = mermaid_to_svg(mermaid_code) if _ssr_enabled() else None
        if svg:
            return (
                '<div class="architecture-diagram" '
                'style="overflow-x:auto;margin:24px 0;padding:16px;'
                'background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;">'
                f"{svg}"
                "</div>"
            )

        # Fallback: client-side rendering via Mermaid.js CDN script in <head>.
        return _client_side_diagram(mermaid_code)

    return re.sub(pattern, replace_mermaid, html, flags=re.DOTALL)


def markdown_to_html(markdown_text: str, title: str = "MindMesh Solution Blueprint") -> str:
    """
    Convert Markdown text into a clean, executive-grade, emoji-free professional HTML document.
    Designed like a Fortune 500 Enterprise Architecture Whitepaper.

    Mermaid diagrams embedded as fenced code blocks (```mermaid) are pre-rendered
    to inline SVG server-side. If pre-rendering is unavailable the Mermaid.js CDN
    script in <head> provides client-side fallback rendering.
    """
    clean_markdown = remove_emojis(markdown_text)
    clean_title = remove_emojis(title)

    # Normalize diagram fences BEFORE markdown processing so every diagram
    # becomes a clean, balanced ```mermaid block (fixes ```flowchart tags,
    # unbalanced fence pairs, and indented fences from LLM output).
    clean_markdown = _normalize_mermaid_fences(clean_markdown)

    # Convert LaTeX math in prose BEFORE markdown processing
    clean_markdown = _convert_latex_to_text(clean_markdown)

    html_content = markdown.markdown(
        clean_markdown,
        extensions=[
            "extra",
            "tables",
            "fenced_code",
            "toc",
            "nl2br",
        ],
    )

    html_content = _sanitize_html(html_content)
    html_content = convert_mermaid_blocks(html_content)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <!-- Mermaid.js: client-side fallback for any diagram that could not be pre-rendered -->
    <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";

    mermaid.initialize({{
        startOnLoad: false,
        theme: "default",
        securityLevel: "strict",
        // Never inject Mermaid's "Syntax error in text" artwork into the
        // document. Failures are handled below and the diagram source stays
        // readable instead of a large error graphic.
        suppressErrorRendering: true
    }});

    // Render every diagram on its own so one broken diagram cannot affect the
    // others, and reveal the Mermaid source of any diagram that fails.
    (async function renderDiagrams() {{
        const diagrams = Array.from(document.querySelectorAll(".mermaid"));
        for (const diagram of diagrams) {{
            try {{
                await mermaid.run({{ nodes: [diagram], suppressErrors: true }});
            }} catch (error) {{
                console.error("MindMesh: Mermaid rendering failed", error);
            }}
            if (!diagram.querySelector("svg")) {{
                const container = diagram.closest(".diagram-container");
                if (container) {{
                    container.classList.add("mermaid-render-error");
                    const source = container.querySelector(".diagram-source");
                    if (source) {{ source.open = true; }}
                }}
            }}
        }}
    }})();
</script>


    <style>
        :root {{
            --bg-page: #f8fafc;
            --bg-doc: #ffffff;
            --text-main: #0f172a;
            --text-muted: #475569;
            --text-light: #64748b;
            --primary: #1e293b;
            --accent: #2563eb;
            --border: #e2e8f0;
            --border-light: #f1f5f9;
            --code-bg: #f8fafc;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-main);
            line-height: 1.65;
            padding: 40px 20px;
            -webkit-font-smoothing: antialiased;
        }}

        .document-wrapper {{
            max-width: 960px;
            margin: 0 auto;
            background: var(--bg-doc);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 56px 64px;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        }}

        /* Clean Header */
        .doc-header {{
            border-bottom: 2px solid var(--border);
            padding-bottom: 24px;
            margin-bottom: 32px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}

        .doc-brand {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
            letter-spacing: -0.01em;
        }}

        .doc-badge {{
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background: #f1f5f9;
            color: #334155;
            padding: 4px 10px;
            border-radius: 4px;
            border: 1px solid #cbd5e1;
        }}

        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--primary);
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        h1 {{
            font-size: 1.95rem;
            margin-bottom: 16px;
            color: #0f172a;
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
        }}

        h2 {{
            font-size: 1.35rem;
            margin-top: 36px;
            margin-bottom: 14px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-light);
            color: #1e293b;
        }}

        h3 {{
            font-size: 1.1rem;
            margin-top: 24px;
            margin-bottom: 10px;
            color: #334155;
        }}

        h4 {{
            font-size: 0.95rem;
            margin-top: 18px;
            margin-bottom: 8px;
            color: #475569;
        }}

        p {{
            margin-bottom: 16px;
            color: var(--text-muted);
            font-size: 0.95rem;
        }}

        strong {{
            color: #0f172a;
            font-weight: 600;
        }}

        ul, ol {{
            margin-bottom: 18px;
            padding-left: 24px;
            color: var(--text-muted);
            font-size: 0.95rem;
        }}

        li {{
            margin-bottom: 6px;
        }}

        blockquote {{
            background: #f8fafc;
            border-left: 4px solid #3b82f6;
            padding: 14px 18px;
            margin: 20px 0;
            color: #334155;
            font-size: 0.92rem;
            border-radius: 0 4px 4px 0;
        }}

        blockquote p:last-child {{
            margin-bottom: 0;
        }}

        /* Tables */
        /* Wide tables scroll horizontally instead of squishing columns:
           auto layout sizes columns to content; the block display enables
           overflow scrolling when the table exceeds the page width. */
        table {{
            display: block;
            width: fit-content;
            max-width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            font-size: 0.9rem;
            table-layout: auto;
            overflow-x: auto;
        }}

        th {{
            background: #f8fafc;
            color: #0f172a;
            font-weight: 600;
            text-align: left;
            padding: 10px 14px;
            border: 1px solid var(--border);
            white-space: nowrap;
            overflow-wrap: break-word;
            word-wrap: break-word;
        }}

        td {{
            padding: 10px 14px;
            border: 1px solid var(--border);
            color: var(--text-muted);
            overflow-wrap: break-word;
            word-wrap: break-word;
        }}

        tr:nth-child(even) {{
            background: #fafbfc;
        }}

        /* Code Blocks */
        code {{
            font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
            background: #f1f5f9;
            color: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.85em;
        }}

        pre {{
            background: #0f172a;
            color: #f8fafc;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 20px 0;
            font-size: 0.88rem;
        }}

        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
            border: none;
        }}

        hr {{
            border: none;
            border-top: 1px solid var(--border);
            margin: 32px 0;
        }}

        /* Architecture Diagram — pre-rendered SVG wrapper */
        .architecture-diagram {{
            overflow-x: auto;
            margin: 24px 0;
            padding: 16px;
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 8px;
            text-align: center;
        }}

        .architecture-diagram svg {{
            max-width: 100%;
            height: auto;
        }}

        /* Client-side rendered diagram — source kept alongside the render */
        .diagram-container {{
            overflow-x: auto;
            margin: 24px 0;
            padding: 16px;
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 8px;
            text-align: center;
        }}

        .diagram-container svg {{
            max-width: 100%;
            height: auto;
        }}

        .diagram-container .diagram-source {{
            margin-top: 12px;
            text-align: left;
            font-size: 0.8rem;
            color: var(--text-light);
        }}

        .diagram-container .diagram-source summary {{
            cursor: pointer;
        }}

        .diagram-container .diagram-source pre {{
            margin: 10px 0 0 0;
            text-align: left;
        }}

        .diagram-container.mermaid-render-error .diagram-source summary {{
            color: #b91c1c;
            font-weight: 600;
        }}

        /* Diagram whose Mermaid source cannot be rendered at all */
        .diagram-fallback {{
            margin: 24px 0;
            padding: 16px;
            background: #fff7ed;
            border: 1px solid #fdba74;
            border-radius: 8px;
        }}

        .diagram-fallback-note {{
            margin-bottom: 12px;
            color: #9a3412;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .diagram-fallback pre {{
            margin: 0;
        }}

        /* Footer */
        .doc-footer {{
            margin-top: 48px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-light);
        }}

        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .document-wrapper {{
                border: none;
                box-shadow: none;
                padding: 0;
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="document-wrapper">
        <div class="doc-header">
            <div class="doc-brand">MindMesh Enterprise Architecture Engine</div>
            <div class="doc-badge">Official Solution Blueprint</div>
        </div>
        {html_content}
        <div class="doc-footer">
            Generated by MindMesh
        </div>
    </div>
</body>
</html>
"""