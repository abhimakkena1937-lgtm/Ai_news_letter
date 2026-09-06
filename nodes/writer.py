from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL
from prompts import (
    WRITER_SYSTEM_PROMPT,
    WRITER_USER_PROMPT,
)
from state import NewsLetterState

from utils.gemini_limiter import gemini_semaphore
def get_writer_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0.3,
    )


async def writer_node(
    state: NewsLetterState,
) -> dict:

    ranked_context = state["ranked_context"]

    print("\n" + "=" * 80)
    print("RUNNING WRITER AGENT")
    print("=" * 80)

    # ---------------------------------------------------------
    # Limit content passed to Writer
    # ---------------------------------------------------------

    ranked_context.top_news = ranked_context.top_news[:10]
    ranked_context.top_start_ups = ranked_context.top_start_ups[:10]
    ranked_context.top_tweets = ranked_context.top_tweets[:10]
    ranked_context.top_github_repos = ranked_context.top_github_repos[:10]
    ranked_context.top_papers = ranked_context.top_papers[:10]

    print("\n" + "=" * 80)
    print("CONTENT SENT TO WRITER")
    print("=" * 80)

    print(
        "NEWS:",
        len(ranked_context.top_news)
    )

    print(
        "STARTUPS:",
        len(ranked_context.top_start_ups)
    )

    print(
        "PEOPLE:",
        len(ranked_context.top_tweets)
    )

    print(
        "GITHUB:",
        len(ranked_context.top_github_repos)
    )

    print(
        "PAPERS:",
        len(ranked_context.top_papers)
    )

    # ---------------------------------------------------------
    # Gemini
    # ---------------------------------------------------------

    llm = get_writer_llm()
    async with gemini_semaphore:
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

    # ---------------------------------------------------------
    # Handle Gemini response
    # ---------------------------------------------------------

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