from __future__ import annotations

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from utils.gemini_limiter import gemini_semaphore
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL
from prompts import (
    IMAGE_SYSTEM_PROMPT,
    IMAGE_USER_PROMPT,
)
from state import NewsLetterState
from schemas import RankedContext
from tools.web_search import tavily_search


def get_image_llm():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
    )


def extract_image_url(page_url: str) -> str | None:

    try:
        response = requests.get(
            page_url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Open Graph image
        og_image = soup.find(
            "meta",
            property="og:image"
        )

        if og_image and og_image.get("content"):
            return urljoin(
                page_url,
                og_image["content"]
            )

        # Twitter image
        twitter_image = soup.find(
            "meta",
            attrs={"name": "twitter:image"}
        )

        if twitter_image and twitter_image.get("content"):
            return urljoin(
                page_url,
                twitter_image["content"]
            )

        # First usable image
        for img in soup.find_all("img"):

            src = img.get("src")

            if not src:
                continue

            image_url = urljoin(
                page_url,
                src
            )

            if image_url.startswith("http"):
                return image_url

    except Exception as e:

        print(
            f"Image extraction failed: "
            f"{page_url} -> {e}"
        )

    return None


async def search_images(
    query: str,
    time_window: str
) -> list[dict]:

    results = await tavily_search(
        query,
        max_results=5,
        time_window=time_window
    )

    image_results = []

    for result in results:

        page_url = result.get(
            "url",
            ""
        )

        if not page_url:
            continue

        image_url = extract_image_url(
            page_url
        )

        if image_url:

            image_results.append({
                "title": result.get(
                    "title",
                    ""
                ),
                "page_url": page_url,
                "image_url": image_url,
                "source": result.get(
                    "source",
                    ""
                )
            })

    return image_results


async def image_agent_node(
    state: NewsLetterState
) -> dict:

    print("\n" + "=" * 80)
    print("RUNNING IMAGE AGENT")
    print("=" * 80)

    ranked_context = state["ranked_context"]
    time_window = state["time_window"]

    image_results = []

    # --------------------------------------------------
    # NEWS
    # --------------------------------------------------

    for item in ranked_context.top_news[:10]:

        query = (
            f"{item.title} "
            f"{item.company or ''} "
            f"AI"
        )

        results = await search_images(
            query,
            time_window
        )

        image_results.extend([
            {
                "type": "news",
                "item": item.title,
                **result
            }
            for result in results
        ])

    # --------------------------------------------------
    # STARTUPS
    # --------------------------------------------------

    for item in ranked_context.top_start_ups[:10]:

        query = (
            f"{item.startup_name} AI startup"
        )

        results = await search_images(
            query,
            time_window
        )

        image_results.extend([
            {
                "type": "startup",
                "item": item.startup_name,
                **result
            }
            for result in results
        ])

    # --------------------------------------------------
    # PEOPLE
    # --------------------------------------------------

    for item in ranked_context.top_tweets[:10]:

        query = (
            f"{item.person} AI"
        )

        results = await search_images(
            query,
            time_window
        )

        image_results.extend([
            {
                "type": "person",
                "item": item.person,
                **result
            }
            for result in results
        ])

    # --------------------------------------------------
    # GITHUB
    # --------------------------------------------------

    for item in ranked_context.top_github_repos[:10]:

        query = (
            f"{item.repo_name} GitHub AI"
        )

        results = await search_images(
            query,
            time_window
        )

        image_results.extend([
            {
                "type": "github",
                "item": item.repo_name,
                **result
            }
            for result in results
        ])

    # --------------------------------------------------
    # PAPERS
    # --------------------------------------------------

    for item in ranked_context.top_papers[:10]:

        query = (
            f"{item.title} AI research paper"
        )

        results = await search_images(
            query,
            time_window
        )

        image_results.extend([
            {
                "type": "paper",
                "item": item.title,
                **result
            }
            for result in results
        ])

    print(
        f"Image candidates found: "
        f"{len(image_results)}"
    )

    # --------------------------------------------------
    # Limit image candidates sent to Gemini
    # --------------------------------------------------

    image_results = image_results[:50]

    print(
        f"Image candidates sent to Gemini: "
        f"{len(image_results)}"
    )

    # --------------------------------------------------
    # GEMINI IMAGE SELECTION
    # --------------------------------------------------

    llm = get_image_llm().with_structured_output(
        RankedContext
    )
    async with gemini_semaphore:
        response = await llm.ainvoke([
            SystemMessage(
                content=IMAGE_SYSTEM_PROMPT
            ),
            HumanMessage(
                content=IMAGE_USER_PROMPT.format(
                    ranked_context=ranked_context,
                    image_results=image_results
                )
            )
        ])

    print("IMAGE AGENT COMPLETE")

    return {
        "ranked_context": response,
        "progress": [
            "image_agent: selected newsletter images"
        ]
    }