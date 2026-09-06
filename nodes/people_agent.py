import asyncio

from tools.web_search import tavily_search, format_research
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from utils.gemini_limiter import gemini_semaphore
from config import GEMINI_MODEL
from schemas import DiscoveredEntity, TweetItems
from prompts import (
    PEOPLE_EXTRACTION_SYSTEM_PROMPT,
    PEOPLE_EXTRACTION_USER_PROMPT,
)
from state import NewsLetterState


# ---------------------------------------------------------
# Search for X / Twitter activity of one person
# ---------------------------------------------------------

async def search_person_sources(
    entity: DiscoveredEntity,
    time_window: str,
) -> list[dict]:

    if entity.entity_type.lower() != "person":
        return []

    person = entity.name

    queries = [
        f'"{person}" posted on X AI',
        f'"{person}" posted on Twitter AI',
        f'"{person}" tweeted AI',
        f'"{person}" tweet artificial intelligence',
        f'"{person}" "on X" AI',
        f'"{person}" "X post" AI',
        f'"{person}" "Twitter post" AI',
        f'"{person}" CEO founder AI X',
    ]

    results = await asyncio.gather(
        *(
            tavily_search(
                query,
                max_results=5,
                time_window=time_window,
            )
            for query in queries
        ),
        return_exceptions=True,
    )

    combined = []

    for query, result in zip(queries, results):

        print("\n" + "=" * 70)
        print("PEOPLE QUERY:", query)
        print("SEARCH WINDOW:", time_window)

        if isinstance(result, Exception):
            print("ERROR:", repr(result))
            continue

        print("RESULT COUNT:", len(result))

        combined.extend(result)

    print(
        f"\nTOTAL RESEARCH RESULTS FOR {person}:",
        len(combined),
    )

    return combined


# ---------------------------------------------------------
# Search all discovered people
# ---------------------------------------------------------

async def targeted_people_research(
    entities: list[DiscoveredEntity],
    time_window: str,
) -> list[dict]:

    people = [
        entity
        for entity in entities
        if entity.entity_type.lower() == "person"
    ]

    print("\n" + "=" * 80)
    print("DISCOVERED PEOPLE")
    print("=" * 80)

    for person in people:
        print(
            f"{person.name} | "
            f"{person.reason}"
        )

    if not people:
        print("No people discovered.")
        return []

    results = await asyncio.gather(
        *(
            search_person_sources(
                person,
                time_window,
            )
            for person in people
        ),
        return_exceptions=True,
    )

    combined = []

    for result in results:

        if isinstance(result, Exception):
            print(
                "PEOPLE RESEARCH ERROR:",
                repr(result)
            )
            continue

        combined.extend(result)

    return combined


# ---------------------------------------------------------
# Remove duplicate search results
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# LLM
# ---------------------------------------------------------

def get_people_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    ).with_structured_output(
        TweetItems
    )


# ---------------------------------------------------------
# Extract actual X/Twitter posts
# ---------------------------------------------------------

async def extract_people(
    entities: list[DiscoveredEntity],
    time_window: str,
) -> list:

    research_results = await targeted_people_research(
        entities,
        time_window,
    )

    if not research_results:
        return []

    research_results = deduplicate_results(
        research_results
    )

    print(
        "\nUNIQUE PEOPLE RESULTS:",
        len(research_results)
    )

    # Limit research sent to Gemini
    research_results = research_results[:10]

    print(
        "\nPEOPLE RESULTS SENT TO GEMINI:",
        len(research_results)
    )

    research_text = format_research(
        research_results
    )

    print("\n" + "#" * 80)
    print("PEOPLE RESEARCH")
    print("#" * 80)

    print(
        research_text[:5000]
    )

    llm = get_people_llm()

    async with gemini_semaphore:
        response = await llm.ainvoke(
            [
                SystemMessage(
                    content=PEOPLE_EXTRACTION_SYSTEM_PROMPT
                ),
                HumanMessage(
                    content=PEOPLE_EXTRACTION_USER_PROMPT.format(
                        research_results=research_text,
                        time_window=time_window,
                    )
                ),
            ]
        )

    return response.tweets


# ---------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------

async def people_agent_node(
    state: NewsLetterState,
) -> dict:

    entities = state.get(
        "discovered_entities",
        [],
    )

    # Planner is the source of truth
    time_window = state["time_window"]

    tweets = await extract_people(
        entities,
        time_window,
    )

    print("\n" + "=" * 80)
    print(
        "EXTRACTED PEOPLE POSTS:",
        len(tweets)
    )
    print("=" * 80)

    for tweet in tweets:

        print(
            "\nPERSON:",
            tweet.person
        )

        print(
            "TWEET:",
            tweet.tweet
        )

        print(
            "SUMMARY:",
            tweet.summary
        )

        print(
            "URL:",
            tweet.url
        )

        print(
            "ENGAGEMENT:",
            tweet.engagement
        )

    return {
        "tweets": tweets,

        "progress": [
            f"people_agent: extracted {len(tweets)} tweets"
        ],
    }