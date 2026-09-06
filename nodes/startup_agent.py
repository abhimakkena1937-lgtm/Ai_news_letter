import asyncio
from tools.web_search import tavily_search,format_research
from schemas import DiscoveredEntity,StartUpItems
from prompts import STARTUP_EXTRACTION_SYSTEM_PROMPT
from prompts import STARTUP_EXTRACTION_USER_PROMPT
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import GEMINI_MODEL
from state import NewsLetterState

async def search_startup_sources(entity: DiscoveredEntity,time_window:str,)->list[dict]:

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
    for query ,result in zip(queries,results):
        print("\n" + "=" * 70)
        print("STARTUP QUERY:", query)
        print("SEARCH WINDOW:", time_window)
        if isinstance(result, Exception):
            print("ERROR:", repr(result))
            continue
        print("RESULT COUNT:", len(result))
        combined.extend(result)
        print("\nTOTAL STARTUP RESEARCH RESULTS:",len(combined),)
        return combined


def get_startup_llm():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    ).with_structured_output(StartUpItems)

async def extract_startups(entity: DiscoveredEntity,time_window: str,)-> list:

    if entity.entity_type != "startup":
        return []

    research_results = await search_startup_sources(entity,time_window,)

    if not research_results:
        return []

    research_text = format_research(research_results)

    llm = get_startup_llm()

    response = await llm.ainvoke(
        [
            SystemMessage(
                content=STARTUP_EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(
                content=STARTUP_EXTRACTION_USER_PROMPT.format(
                    research_results=research_text,
                    time_window=time_window,
                )
            ),
        ]
    )
    return response.startups

def deduplicate_startups(startups:list,)->list:
    seen=set()
    unique=[]
    for startup in startups:
        key=startup.startup_name.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(startup)
    return unique

async def startup_agent_node(state: NewsLetterState,)-> dict:

    entities = state.get("discovered_entities",[])
    time_window = state.get("time_window","")
    startups = []
    for entity in entities:
        result = await extract_startups(
            entity,
            time_window,
        )

        startups.extend(result)
    unique_startups=deduplicate_startups(startups)

    return {
        "startups": startups,
        "progress": [
            f"startup_agent: extracted {len(startups)} startups",
            f"startup_agent: after dedup {len(unique_startups)} startups",
        ],
    }