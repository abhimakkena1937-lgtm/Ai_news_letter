from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL
from prompts import (
    REDUCER_SYSTEM_PROMPT,
    REDUCER_USER_PROMPT,
)
from schemas import RankedContext
from state import NewsLetterState


def get_reducer_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    ).with_structured_output(RankedContext)


async def reducer_node(
    state: NewsLetterState,
) -> dict:

    news = state.get("news", [])
    startups = state.get("startups", [])
    tweets = state.get("tweets", [])
    github_repos = state.get("github_repos", [])
    papers = state.get("research_papers", [])

    print("\n" + "=" * 80)
    print("RUNNING REDUCER")
    print("=" * 80)

    print("NEWS:", len(news))
    print("STARTUPS:", len(startups))
    print("TWEETS:", len(tweets))
    print("GITHUB REPOS:", len(github_repos))
    print("PAPERS:", len(papers))

    research_data = {
        "news": news,
        "startups": startups,
        "tweets": tweets,
        "github_repos": github_repos,
        "papers": papers,
    }

    llm = get_reducer_llm()

    response = await llm.ainvoke(
        [
            SystemMessage(
                content=REDUCER_SYSTEM_PROMPT
            ),
            HumanMessage(
                content=REDUCER_USER_PROMPT.format(
                    research_data=research_data
                )
            ),
        ]
    )

    ranked_context = response

    print("\n" + "=" * 80)
    print("REDUCED CONTEXT")
    print("=" * 80)

    print(
        "TOP NEWS:",
        len(ranked_context.top_news)
    )

    print(
        "TOP STARTUPS:",
        len(ranked_context.top_start_ups)
    )

    print(
        "TOP TWEETS:",
        len(ranked_context.top_tweets)
    )

    print(
        "TOP GITHUB:",
        len(ranked_context.top_github_repos)
    )

    print(
        "TOP PAPERS:",
        len(ranked_context.top_papers)
    )

    print(
        "TOOL OF THE DAY:",
        ranked_context.tool_of_the_day
    )

    return {
        "ranked_context": ranked_context,
        "progress": [
            "reducer: ranked and selected newsletter content"
        ],
    }