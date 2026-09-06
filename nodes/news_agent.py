import asyncio

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL
from prompts import (
    NEWS_EXTRACTION_SYSTEM_PROMPT,
    NEWS_EXTRACTION_USER_PROMPT,
)
from schemas import DiscoveredEntity, NewsItems
from state import NewsLetterState
from tools.freshness import check_freshness
from tools.web_search import format_research, tavily_search
from tools.freshness import filter_fresh_news


# ---------------------------------------------------------
# Search one entity
# ---------------------------------------------------------

async def research_entity(entity:str,time_window:str,)->list[dict]:
    return await tavily_search(
        f"{entity} latest AI news",
        max_results=5,
        time_window=time_window
    )

# ---------------------------------------------------------
# Search all discovered entities concurrently
# ---------------------------------------------------------

async def targeted_research(entities:list[DiscoveredEntity],time_window:str)->list[dict]:
        results=await asyncio.gather(
        *(
            research_entity(entity.name,time_window) for entity in entities
        ),
        return_exceptions=True, 
        )
        combined=[]
        for entity,result in zip(entities,results):
            print("\n" + "=" * 70)
            print("ENTITY:", entity.name)
            if isinstance(result,Exception):
                continue
            for item in result:
                print("TITLE:", item.get("title"))
                print("PUBLISHED:", item.get("published_at"))
                print("URL:", item.get("url"))
            combined.extend(result)
        print("\n Total raw news results:",len(combined))
        return combined         
def get_news_llm():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    ).with_structured_output(NewsItems)

async def extract_news(entities: list[DiscoveredEntity],time_window: str,) -> list:

    research_results = await targeted_research(entities,time_window)

    if not research_results:
        return []

    research_text = format_research(research_results)

    llm = get_news_llm()

    response = await llm.ainvoke(
        [
            SystemMessage(
                content=NEWS_EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(
                content=NEWS_EXTRACTION_USER_PROMPT.format(
                    research_results=research_text,
                    time_window=time_window,
                )
            ),
        ]
    )
    news_items=response.news
    return news_items

async def news_agent_node(state:NewsLetterState)->dict:
     entities=state.get("discovered_entities",[])
     time_window=state.get("time_window","")
     news=await extract_news(
          entities,time_window=time_window,
     )
     return {
          "news":news,
          "progress":[
               f"news_agent:extracted{len(news)} news items"
          ],
     }







