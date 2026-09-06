import asyncio
from pathlib import Path

from nodes.exporter import exporter_node


async def main():

    markdown_file = Path("output/ai_daily.md")

    if not markdown_file.exists():
        print("No existing newsletter found.")
        return

    newsletter_markdown = markdown_file.read_text(
        encoding="utf-8"
    )

    state = {
        "newsletter_markdown": newsletter_markdown
    }

    await exporter_node(state)


if __name__ == "__main__":
    asyncio.run(main())