import re
import markdown


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


def markdown_to_html(markdown_text: str, title: str = "MindMesh Solution Blueprint") -> str:
    """
    Convert Markdown text into a clean, executive-grade, emoji-free professional HTML document.
    Designed like a Fortune 500 Enterprise Architecture Whitepaper.
    """
    clean_markdown = remove_emojis(markdown_text)
    clean_title = remove_emojis(title)

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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
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
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            font-size: 0.9rem;
        }}

        th {{
            background: #f8fafc;
            color: #0f172a;
            font-weight: 600;
            text-align: left;
            padding: 10px 14px;
            border: 1px solid var(--border);
        }}

        td {{
            padding: 10px 14px;
            border: 1px solid var(--border);
            color: var(--text-muted);
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
            Generated autonomously by SolutionForge AI • Verified Enterprise Architecture Document
        </div>
    </div>
</body>
</html>
"""