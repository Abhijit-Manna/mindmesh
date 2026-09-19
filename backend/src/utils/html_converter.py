import markdown


def markdown_to_html(markdown_text: str) -> str:
    """
    Convert Markdown text into a complete HTML document.
    """

    html_content = markdown.markdown(
        markdown_text,
        extensions=[
            "extra",
            "tables",
            "fenced_code",
        ],
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>MindMesh Solution Blueprint</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            color: #222;
        }}

        h1, h2, h3 {{
            color: #1f2937;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
        }}

        th {{
            background: #f3f4f6;
        }}

        code {{
            background: #f3f4f6;
            padding: 3px 6px;
            border-radius: 4px;
        }}

        pre {{
            background: #f3f4f6;
            padding: 15px;
            overflow-x: auto;
        }}
    </style>
</head>

<body>
{html_content}
</body>
</html>
"""