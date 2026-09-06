from markdown import markdown
from pathlib import Path
import webbrowser

from state import NewsLetterState


async def exporter_node(state: NewsLetterState) -> dict:

    markdown_text = state["newsletter_markdown"]

    print("\n" + "=" * 80)
    print("RUNNING EXPORTER")
    print("=" * 80)

    # Convert Markdown to HTML
    content_html = markdown(
        markdown_text,
        extensions=["extra"]
    )

    html = f"""
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>AI Daily</title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 0;
            background: #f5f5f5;
            font-family: Arial, Helvetica, sans-serif;
            color: #222;
        }}

        .container {{
            max-width: 750px;
            margin: 40px auto;
            background: white;
            padding: 35px;
            border-radius: 10px;
        }}

        h1 {{
            margin-top: 0;
            font-size: 32px;
        }}

        h2 {{
            margin-top: 35px;
            padding-bottom: 8px;
            border-bottom: 1px solid #ddd;
            font-size: 22px;
        }}

        h3 {{
            margin-top: 25px;
            margin-bottom: 8px;
            font-size: 18px;
        }}

        p {{
            line-height: 1.6;
        }}

        li {{
            margin-bottom: 12px;
            line-height: 1.5;
        }}

        a {{
            text-decoration: none;
            word-break: break-word;
        }}

        img {{
            display: block;
            width: 100%;
            max-width: 100%;
            height: auto;
            margin: 15px 0 20px 0;
            border-radius: 8px;
        }}

        ul {{
            padding-left: 25px;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 13px;
            color: #777;
            text-align: center;
        }}

        @media (max-width: 800px) {{

            body {{
                background: white;
            }}

            .container {{
                margin: 0;
                padding: 20px;
                border-radius: 0;
            }}

            h1 {{
                font-size: 28px;
            }}

        }}

    </style>

</head>

<body>

    <div class="container">

        {content_html}

        <div class="footer">
            AI Daily — Automated AI research newsletter
        </div>

    </div>

</body>

</html>
"""

    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Save Markdown
    markdown_file = output_dir / "ai_daily.md"
    markdown_file.write_text(
        markdown_text,
        encoding="utf-8"
    )

    # Save HTML
    html_file = output_dir / "ai_daily.html"
    html_file.write_text(
        html,
        encoding="utf-8"
    )

    # Open newsletter in browser
    webbrowser.open(
        html_file.resolve().as_uri()
    )

    print("\nNEWSLETTER GENERATED")
    print("=" * 80)
    print(f"Markdown: {markdown_file.resolve()}")
    print(f"HTML:     {html_file.resolve()}")
    print("=" * 80)

    return {
        "newsletter_html": html,
        "progress": [
            "exporter: generated newsletter HTML",
            f"exporter: saved {html_file}"
        ]
    }