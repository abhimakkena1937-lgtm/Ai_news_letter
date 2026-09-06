import asyncio

from nodes.planner import planner_node
from nodes.discovery_agent import discovery_agent_node
from nodes.news_agent import news_agent_node
from nodes.startup_agent import startup_agent_node
from nodes.people_agent import people_agent_node
from nodes.github_agent import github_agent_node
from nodes.paper_agent import paper_agent_node
from nodes.reducer import reducer_node


async def main():

    state = {}

    # =====================================================
    # PLANNER
    # =====================================================

    print("=" * 80)
    print("RUNNING PLANNER")
    print("=" * 80)

    result = await planner_node(state)
    state.update(result)

    print("\nTIME WINDOW:")
    print(state["time_window"])


    # =====================================================
    # DISCOVERY
    # =====================================================

    print("\n" + "=" * 80)
    print("RUNNING DISCOVERY AGENT")
    print("=" * 80)

    result = await discovery_agent_node(state)
    state.update(result)

    print(
        "\nDISCOVERED ENTITIES:",
        len(state.get("discovered_entities", []))
    )


    # =====================================================
    # RUN ALL AGENTS
    # =====================================================

    print("\n" + "=" * 80)
    print("RUNNING NEWS AGENT")
    print("=" * 80)

    result = await news_agent_node(state)
    state.update(result)


    print("\n" + "=" * 80)
    print("RUNNING STARTUP AGENT")
    print("=" * 80)

    result = await startup_agent_node(state)
    state.update(result)


    print("\n" + "=" * 80)
    print("RUNNING PEOPLE AGENT")
    print("=" * 80)

    result = await people_agent_node(state)
    state.update(result)


    print("\n" + "=" * 80)
    print("RUNNING GITHUB AGENT")
    print("=" * 80)

    result = await github_agent_node(state)
    state.update(result)


    print("\n" + "=" * 80)
    print("RUNNING PAPER AGENT")
    print("=" * 80)

    result = await paper_agent_node(state)
    state.update(result)


    # =====================================================
    # CHECK INPUTS TO REDUCER
    # =====================================================

    print("\n" + "=" * 80)
    print("DATA GOING INTO REDUCER")
    print("=" * 80)

    print("NEWS:", len(state.get("news", [])))
    print("STARTUPS:", len(state.get("startups", [])))
    print("TWEETS:", len(state.get("tweets", [])))
    print("GITHUB:", len(state.get("github_repos", [])))
    print("PAPERS:", len(state.get("research_papers", [])))


    # =====================================================
    # REDUCER
    # =====================================================

    print("\n" + "=" * 80)
    print("RUNNING REDUCER")
    print("=" * 80)

    result = await reducer_node(state)
    state.update(result)


    # =====================================================
    # FINAL RANKED CONTEXT
    # =====================================================

    ranked = state["ranked_context"]

    print("\n" + "=" * 80)
    print("FINAL RANKED CONTEXT")
    print("=" * 80)


    print("\nTOP NEWS:")
    for item in ranked.top_news:
        print("-", item)


    print("\nTOP STARTUPS:")
    for item in ranked.top_start_ups:
        print("-", item)


    print("\nTOP TWEETS:")
    for item in ranked.top_tweets:
        print("-", item)


    print("\nTOP GITHUB REPOSITORIES:")
    for item in ranked.top_github_repos:
        print("-", item)


    print("\nTOP PAPERS:")
    for item in ranked.top_papers:
        print("-", item)


    print("\nTOOL OF THE DAY:")
    print(ranked.tool_of_the_day)


if __name__ == "__main__":
    asyncio.run(main())