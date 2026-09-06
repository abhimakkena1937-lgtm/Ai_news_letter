from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.gemini_limiter import gemini_semaphore
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
    ).with_structured_output(
        RankedContext
    )


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

    # ---------------------------------------------------------
    # Limit data sent to Gemini
    # ---------------------------------------------------------

    news = news[:10]
    startups = startups[:10]
    tweets = tweets[:10]
    github_repos = github_repos[:10]
    papers = papers[:10]

    print("\n" + "=" * 80)
    print("DATA SENT TO GEMINI")
    print("=" * 80)

    print("NEWS:", len(news))
    print("STARTUPS:", len(startups))
    print("TWEETS:", len(tweets))
    print("GITHUB REPOS:", len(github_repos))
    print("PAPERS:", len(papers))

    # ---------------------------------------------------------
    # Prepare research data
    # ---------------------------------------------------------

    research_data = {
        "news": news,
        "startups": startups,
        "tweets": tweets,
        "github_repos": github_repos,
        "papers": papers,
    }

    # ---------------------------------------------------------
    # Gemini
    # ---------------------------------------------------------

    llm = get_reducer_llm()
    async with gemini_semaphore:
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

    # ---------------------------------------------------------
    # Debug output
    # ---------------------------------------------------------

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