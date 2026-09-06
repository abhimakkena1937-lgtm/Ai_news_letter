import asyncio
from tools.web_search import tavily_search,format_research
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_MODEL
from schemas import DiscoveredEntity,DiscoveredEntities
from prompts import Entity_discovery_sys_prompt,ENTITY_DISCOVERY_USER_PROMPT
from langchain_core.messages import HumanMessage,SystemMessage
from state import NewsLetterState
from datetime import datetime, timedelta, timezone
Discovery_Queries=[
    "latest AI news",
    "latest AI model releases",
    "latest AI startup funding",
    "latest AI acquisitions",
    "latest AI product launches",
    "latest AI research breakthroughs",
    "latest AI policy developments",
]
def expand_time_window(time_window: str, days: int) -> str:

    start_text, end_text = time_window.split("to", maxsplit=1)

    start = datetime.fromisoformat(start_text.strip())
    end = datetime.fromisoformat(end_text.strip())

    new_start = end - timedelta(days=days)

    return (
        f"{new_start.isoformat()} to "
        f"{end.isoformat()}"
    )
async def search_queries(queries:list[str],time_window:str,)->list[dict]:
    results=await asyncio.gather(
        *(
            tavily_search(
                query,
                max_results=5,
                time_window=time_window,

            )for query in queries
        ),
        return_exceptions=True,
    )
    combined_results=[]
    for query,result in zip(queries,results):
        print("\n" + "=" * 70)
        print("QUERY:", query)
        print("SEARCH WINDOW:", f"last {time_window} day(s)")
        if isinstance(result,Exception):
            continue
        combined_results.extend(result)
    return combined_results

async def discover_web_results(time_window:str)->list[dict]:
    results = await search_queries(
        Discovery_Queries,
        time_window,
    )
    print("\nDEBUG SEARCH OUTPUT TYPES:")

    print("\n24 hour results:", len(results))
    if len(results)<10:
        time_window=expand_time_window(time_window,3,)
        print('\n'+"#"*80)
        print("not enough results")
        print("expanding search to last 3 days")
        print("#"*80)
        results=await search_queries(Discovery_Queries,time_window,)
        print("\n 3 day results:",len(results))
    if len(results)<10:
        time_window=expand_time_window(time_window,7,)
        print("\n" + "#" * 80)
        print("STILL NOT ENOUGH RESULTS")
        print("EXPANDING SEARCH TO LAST 7 DAYS")
        print("#" * 80)
        results=await search_queries(Discovery_Queries,time_window,)
        print("\n 7- day results:",len(results))
    print("\n"+"#"*80)
    print("final discovery results:",len(results))
    print("#"*80)
    return results

def get_entity_discovery_llm():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    ).with_structured_output(DiscoveredEntities)

async def discover_entities(time_window:str)->list[DiscoveredEntity]:
    research_results=await discover_web_results(time_window,)
    if not research_results:
        return []
    research_text=format_research(research_results)
    print("\n" + "#" * 80)
    print("FORMATTED RESEARCH")
    print("#" * 80)
    print(research_text[:5000])
    llm=get_entity_discovery_llm()
    response=await llm.ainvoke(
        [
            SystemMessage(content=Entity_discovery_sys_prompt),
            HumanMessage(content=ENTITY_DISCOVERY_USER_PROMPT.format(
                research_results=research_text,
                time_window=time_window,

            ))
        ]
    )
    return response.entities
async def discovery_agent_node(state: NewsLetterState,) -> dict:
    time_window=state.get("time_window","")
    entities = await discover_entities(time_window,)
    return {
        "discovered_entities": entities,
        "progress": [
            f"discovery_agent: discovered {len(entities)} entities"
        ],
    }