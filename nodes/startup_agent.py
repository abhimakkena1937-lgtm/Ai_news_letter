import asyncio
from utils.gemini_limiter import gemini_semaphore
from tools.web_search import tavily_search, format_research

from schemas import DiscoveredEntity, StartUpItems

from prompts import (
    STARTUP_EXTRACTION_SYSTEM_PROMPT,
    STARTUP_EXTRACTION_USER_PROMPT,
)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import GEMINI_MODEL
from state import NewsLetterState


async def search_startup_sources(
    entity: DiscoveredEntity,
    time_window: str,
) -> list[dict]:

    if entity.entity_type != "startup":
        return []

    queries = [
        f"{entity.name} startup funding",
        f"{entity.name} startup investors",
        f"{entity.name} startup acquisition",
        f"{entity.name} startup valuation",
        f"{entity.name} YC",
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

    for query, result in zip(
        queries,
        results
    ):

        print("\n" + "=" * 70)
        print("STARTUP QUERY:", query)
        print("SEARCH WINDOW:", time_window)

        if isinstance(result, Exception):

            print(
                "ERROR:",
                repr(result)
            )

            continue

        print(
            "RESULT COUNT:",
            len(result)
        )

        combined.extend(result)

    print(
        "\nTOTAL STARTUP RESEARCH RESULTS:",
        len(combined)
    )

    return combined


def get_startup_llm():

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    ).with_structured_output(
        StartUpItems
    )


def deduplicate_research(
    results: list[dict]
) -> list[dict]:

    seen = set()
    unique = []

    for result in results:

        url = result.get(
            "url",
            ""
        )

        title = result.get(
            "title",
            ""
        )

        key = (
            url.strip().lower()
            if url
            else title.strip().lower()
        )

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)
        unique.append(result)

    return unique


def deduplicate_startups(
    startups: list
) -> list:

    seen = set()
    unique = []

    for startup in startups:

        key = (
            startup.startup_name
            .strip()
            .lower()
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(startup)

    return unique


async def startup_agent_node(
    state: NewsLetterState,
) -> dict:

    entities = state.get(
        "discovered_entities",
        []
    )

    time_window = state.get(
        "time_window",
        ""
    )

    # --------------------------------------------------
    # Get startup entities
    # --------------------------------------------------

    startup_entities = [
        entity
        for entity in entities
        if entity.entity_type == "startup"
    ]

    print(
        "\nSTARTUP ENTITIES:",
        len(startup_entities)
    )

    if not startup_entities:

        return {
            "startups": [],
            "progress": [
                "startup_agent: no startup entities found"
            ],
        }

    # --------------------------------------------------
    # Search all startups
    # --------------------------------------------------

    research_batches = await asyncio.gather(
        *(
            search_startup_sources(
                entity,
                time_window
            )
            for entity in startup_entities
        ),
        return_exceptions=True,
    )

    # --------------------------------------------------
    # Combine research
    # --------------------------------------------------

    all_research = []

    for entity, result in zip(
        startup_entities,
        research_batches
    ):

        if isinstance(result, Exception):

            print(
                f"Startup search failed for "
                f"{entity.name}: {result}"
            )

            continue

        # Add entity information so Gemini knows
        # which startup the evidence belongs to.

        for item in result:

            item = dict(item)

            item["startup_entity"] = entity.name

            all_research.append(item)

    # --------------------------------------------------
    # Remove duplicate research
    # --------------------------------------------------

    all_research = deduplicate_research(
        all_research
    )

    print(
        "\nTOTAL COMBINED STARTUP RESEARCH:",
        len(all_research)
    )

    if not all_research:

        return {
            "startups": [],
            "progress": [
                "startup_agent: no startup research found"
            ],
        }

    # --------------------------------------------------
    # IMPORTANT:
    # Limit total research sent to Gemini
    # --------------------------------------------------

    all_research = all_research[:10]

    print(
        "\nSTARTUP RESULTS SENT TO GEMINI:",
        len(all_research)
    )

    research_text = format_research(
        all_research
    )

    # --------------------------------------------------
    # ONE GEMINI CALL
    # --------------------------------------------------

    llm = get_startup_llm()

    async with gemini_semaphore:
        response = await llm.ainvoke(
            [
                SystemMessage(
                    content=STARTUP_EXTRACTION_SYSTEM_PROMPT
                ),
                HumanMessage(
                    content=STARTUP_EXTRACTION_USER_PROMPT.format(
                        research_results=research_text,
                        time_window=time_window,
                    )
                ),
            ]
        )

    startups = deduplicate_startups(
        response.startups
    )

    print(
        "\nSTARTUPS EXTRACTED:",
        len(startups)
    )

    return {
        "startups": startups,
        "progress": [
            f"startup_agent: extracted "
            f"{len(startups)} startups"
        ],
    }