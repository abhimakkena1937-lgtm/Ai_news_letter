import asyncio

from nodes.planner import planner_node
from nodes.discovery_agent import discovery_agent_node
from nodes.news_agent import news_agent_node


async def main():

    state = {}

    # --------------------------------------------------
    # PLANNER
    # --------------------------------------------------
    print("=" * 80)
    print("RUNNING PLANNER")
    print("=" * 80)

    planner_result = await planner_node(state)
    state.update(planner_result)

    print("\nPLANNER TIME WINDOW:")
    print(state["time_window"])

    # --------------------------------------------------
    # DISCOVERY
    # --------------------------------------------------
    print("\n" + "=" * 80)
    print("RUNNING DISCOVERY AGENT")
    print("=" * 80)

    discovery_result = await discovery_agent_node(state)
    state.update(discovery_result)

    entities = state.get("discovered_entities", [])

    print(f"\nDISCOVERED ENTITIES: {len(entities)}")

    for entity in entities:
        print(
            f"{entity.name} | "
            f"{entity.entity_type} | "
            f"{entity.reason}"
        )

    # --------------------------------------------------
    # NEWS
    # --------------------------------------------------
    print("\n" + "=" * 80)
    print("RUNNING NEWS AGENT")
    print("=" * 80)

    news_result = await news_agent_node(state)
    state.update(news_result)

    news = state.get("news", [])

    print("\n" + "=" * 80)
    print("NEWS AGENT RESULT")
    print("=" * 80)

    print(f"\nEXTRACTED NEWS: {len(news)}")

    for i, item in enumerate(news, start=1):

        print("\n" + "-" * 70)
        print(f"NEWS {i}")

        print("TITLE:", item.title)
        print("SUMMARY:", item.summary)
        print("SOURCE:", item.source)
        print("URL:", item.url)

        if hasattr(item, "published_date"):
            print("PUBLISHED DATE:", item.published_date)

        if hasattr(item, "event_date"):
            print("EVENT DATE:", item.event_date)


if __name__ == "__main__":
    asyncio.run(main())