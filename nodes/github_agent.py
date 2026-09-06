import asyncio

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL
from prompts import (
    GITHUB_EXTRACTION_SYSTEM_PROMPT,
    GITHUB_EXTRACTION_USER_PROMPT,
)
from schemas import GitHubItem, GitHubItems
from state import NewsLetterState
from tools.web_search import tavily_search, format_research


# ---------------------------------------------------------
# GitHub-focused searches
# ---------------------------------------------------------

GITHUB_QUERIES = [
    "new AI GitHub repository",
    "new AI open source GitHub repository",
    "new generative AI GitHub repository",
    "new agentic AI GitHub repository",
    "new AI agent GitHub repository",
    "new LLM GitHub repository",
    "new RAG GitHub repository",
    "new machine learning GitHub repository",
    "new AI coding agent GitHub repository",
    "new open source AI model GitHub repository",
]


# ---------------------------------------------------------
# Search the web for GitHub repositories
# ---------------------------------------------------------

async def search_github_sources(
    query: str,
    time_window: str,
) -> list[dict]:

    try:
        results = await tavily_search(
            query,
            max_results=10,
            time_window=time_window,
        )

        print("\n" + "=" * 70)
        print("GITHUB QUERY:", query)
        print("TIME WINDOW:", time_window)
        print("RESULT COUNT:", len(results))

        for item in results:
            print("TITLE:", item.get("title"))
            print("PUBLISHED:", item.get("published_at"))
            print("URL:", item.get("url"))

        return results

    except Exception as e:
        print("GITHUB SEARCH ERROR:", repr(e))
        return []


# ---------------------------------------------------------
# Run all GitHub searches in parallel
# ---------------------------------------------------------

async def research_github(time_window: str) -> list[dict]:

    results = await asyncio.gather(
        *(
            search_github_sources(
                query,
                time_window,
            )
            for query in GITHUB_QUERIES
        ),
        return_exceptions=True,
    )

    combined = []

    for result in results:

        if isinstance(result, Exception):
            print("GITHUB RESEARCH ERROR:", repr(result))
            continue

        combined.extend(result)

    print("\n" + "=" * 80)
    print("TOTAL RAW GITHUB RESULTS:", len(combined))
    print("=" * 80)

    return combined


# ---------------------------------------------------------
# Deduplicate search results
# ---------------------------------------------------------

def deduplicate_results(results: list[dict]) -> list[dict]:

    seen = set()
    unique = []

    for result in results:

        url = result.get("url")

        if not url:
            continue

        url = str(url).strip().lower()

        if url in seen:
            continue

        seen.add(url)
        unique.append(result)

    return unique


# ---------------------------------------------------------
# Gemini structured output
# ---------------------------------------------------------

def get_github_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    ).with_structured_output(GitHubItems)


# ---------------------------------------------------------
# Extract GitHub repositories
# ---------------------------------------------------------

async def extract_github(
    time_window: str,
) -> list[GitHubItem]:

    research_results = await research_github(
        time_window
    )

    if not research_results:
        print("NO GITHUB RESEARCH RESULTS")
        return []

    # Remove duplicate URLs before sending to Gemini
    research_results = deduplicate_results(
        research_results
    )

    print(
        "\nUNIQUE GITHUB RESULTS:",
        len(research_results)
    )

    research_text = format_research(
        research_results
    )

    print("\n" + "#" * 80)
    print("GITHUB RESEARCH EVIDENCE")
    print("#" * 80)

    print(research_text[:10000])

    llm = get_github_llm()

    response = await llm.ainvoke(
        [
            SystemMessage(
                content=GITHUB_EXTRACTION_SYSTEM_PROMPT
            ),
            HumanMessage(
                content=GITHUB_EXTRACTION_USER_PROMPT.format(
                    research_results=research_text,
                    time_window=time_window,
                )
            ),
        ]
    )

    return response.repositories


# ---------------------------------------------------------
# GitHub Agent Node
# ---------------------------------------------------------

async def github_agent_node(
    state: NewsLetterState,
) -> dict:

    # Planner is the source of truth
    time_window = state["time_window"]

    print("\n" + "=" * 80)
    print("RUNNING GITHUB AGENT")
    print("=" * 80)

    print("PLANNER TIME WINDOW:")
    print(time_window)

    repositories = await extract_github(
        time_window
    )

    print("\n" + "=" * 80)
    print("NEW AI GITHUB REPOSITORIES")
    print("=" * 80)

    for i, repo in enumerate(
        repositories,
        start=1,
    ):

        print(f"\n{i}. {repo.repo_name}")
        print("Description:", repo.description)
        print("GitHub URL:", repo.url)
        print("Reason:", repo.reason)

        if repo.stars is not None:
            print("Stars:", repo.stars)

        if repo.language:
            print("Language:", repo.language)

    print(
        "\nTOTAL GITHUB REPOSITORIES:",
        len(repositories),
    )

    return {
        "github_repos": repositories,
        "progress": [
            f"github_agent: extracted {len(repositories)} new AI repositories"
        ],
    }