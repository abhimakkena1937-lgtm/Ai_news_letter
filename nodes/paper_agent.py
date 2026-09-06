import asyncio

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL
from prompts import (
    PAPER_EXTRACTION_SYSTEM_PROMPT,
    PAPER_EXTRACTION_USER_PROMPT,
)
from schemas import PaperItem, PaperItems
from state import NewsLetterState
from tools.web_search import tavily_search, format_research


PAPER_QUERIES = [
    "new AI research paper",
    "new artificial intelligence research paper",
    "new machine learning research paper",
    "new LLM research paper",
    "new generative AI research paper",
    "new AI agents research paper",
    "new RAG research paper",
    "new multimodal AI research paper",
    "new computer vision AI research paper",
    "new natural language processing research paper",
]


async def search_paper_sources(
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
        print("PAPER QUERY:", query)
        print("TIME WINDOW:", time_window)
        print("RESULT COUNT:", len(results))

        for item in results:

            print("TITLE:", item.get("title"))
            print("PUBLISHED:", item.get("published_at"))
            print("URL:", item.get("url"))

        return results

    except Exception as e:

        print(
            "PAPER SEARCH ERROR:",
            repr(e)
        )

        return []


async def research_papers(
    time_window: str,
) -> list[dict]:

    results = await asyncio.gather(
        *(
            search_paper_sources(
                query,
                time_window,
            )
            for query in PAPER_QUERIES
        ),
        return_exceptions=True,
    )

    combined = []

    for result in results:

        if isinstance(result, Exception):

            print(
                "PAPER RESEARCH ERROR:",
                repr(result)
            )

            continue

        combined.extend(result)

    print("\n" + "=" * 80)
    print(
        "TOTAL RAW PAPER RESULTS:",
        len(combined)
    )
    print("=" * 80)

    return combined


def deduplicate_results(
    results: list[dict],
) -> list[dict]:

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


def get_paper_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    ).with_structured_output(PaperItems)


async def extract_papers(
    time_window: str,
) -> list[PaperItem]:

    research_results = await research_papers(
        time_window
    )

    if not research_results:

        print("NO PAPER RESEARCH RESULTS")

        return []

    research_results = deduplicate_results(
        research_results
    )

    print(
        "\nUNIQUE PAPER RESULTS:",
        len(research_results)
    )

    research_text = format_research(
        research_results
    )

    print("\n" + "#" * 80)
    print("PAPER RESEARCH EVIDENCE")
    print("#" * 80)

    print(
        research_text[:10000]
    )

    llm = get_paper_llm()

    response = await llm.ainvoke(
        [
            SystemMessage(
                content=PAPER_EXTRACTION_SYSTEM_PROMPT
            ),
            HumanMessage(
                content=PAPER_EXTRACTION_USER_PROMPT.format(
                    research_results=research_text,
                    time_window=time_window,
                )
            ),
        ]
    )

    return response.papers


async def paper_agent_node(
    state: NewsLetterState,
) -> dict:

    # Planner is the source of truth
    time_window = state["time_window"]

    print("\n" + "=" * 80)
    print("RUNNING PAPER AGENT")
    print("=" * 80)

    print(
        "PLANNER TIME WINDOW:",
        time_window
    )

    papers = await extract_papers(
        time_window
    )

    print("\n" + "=" * 80)
    print("NEW AI RESEARCH PAPERS")
    print("=" * 80)

    for i, paper in enumerate(
        papers,
        start=1,
    ):

        print(
            f"\n{i}. {paper.title}"
        )

        print(
            "Authors:",
            paper.authors
        )

        print(
            "URL:",
            paper.url
        )

        print(
            "Summary:",
            paper.summary
        )

        print(
            "Reason:",
            paper.reason
        )

    print(
        "\nTOTAL PAPERS:",
        len(papers)
    )

    return {
        "research_papers": papers,
        "progress": [
            f"paper_agent: extracted {len(papers)} papers"
        ],
    }