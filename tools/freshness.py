from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,SystemMessage
from config import GEMINI_MODEL
from schemas import FreshnessCheck
from prompts import FRESHNESS_SYSTEM_PROMPT,FRESHNESS_USER_PROMPT

def get_freshness_llm():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    ).with_structured_output(FreshnessCheck)

async def check_freshness(event_text:str,time_window:str)->FreshnessCheck:
    llm=get_freshness_llm()
    response=await llm.ainvoke(
        [
            SystemMessage(content=FRESHNESS_SYSTEM_PROMPT),
            HumanMessage(content=FRESHNESS_USER_PROMPT.format(
                event_text=event_text,
                time_window=time_window,
            )),
        ]
    )
    return response
async def filter_fresh_news(news_items,time_window:str,):
    fresh_news=[]
    for item in news_items:
        event_text=f"""
        HEADLINE:{item.headline}
        COMPANY:{item.company}
        SUMMARY:{item.summary}
        PUBLISHED:{item.published_at}
        SOURCE:{item.source}
        URL:{item.url}
        """
        freshness=await check_freshness(
            event_text=event_text,
            time_window=time_window
        )
        print(
            f"\nFRESHNESS: {freshness.is_recent}"
            f"\nDATE: {freshness.event_date}"
            f"\nHEADLINE: {item.headline}"
        )
        if freshness.is_recent:
            fresh_news.append(item)
        return fresh_news