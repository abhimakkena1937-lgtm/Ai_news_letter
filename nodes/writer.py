from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL
from prompts import (
    WRITER_SYSTEM_PROMPT,
    WRITER_USER_PROMPT,
)
from state import NewsLetterState


def get_writer_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0.3,
    )


async def writer_node(state: NewsLetterState) -> dict:

    ranked_context = state["ranked_context"]

    print("\n" + "=" * 80)
    print("RUNNING WRITER AGENT")
    print("=" * 80)

    llm = get_writer_llm()

    response = await llm.ainvoke(
        [
            SystemMessage(
                content=WRITER_SYSTEM_PROMPT
            ),
            HumanMessage(
                content=WRITER_USER_PROMPT.format(
                    ranked_context=ranked_context
                )
            ),
        ]
    )

    newsletter = response.content

    if isinstance(newsletter, list):
        newsletter = "".join(
            block.get("text", "")
            for block in newsletter
            if isinstance(block, dict)
        )

    print("\n" + "=" * 80)
    print("NEWSLETTER GENERATED")
    print("=" * 80)

    print(newsletter)

    return {
        "newsletter_markdown": newsletter,
        "progress": [
            "writer: generated newsletter"
        ],
    }