import asyncio

from nodes.planner import planner_node
from nodes.discovery_agent import discovery_agent_node
from nodes.people_agent import people_agent_node


async def main():

    # Initial state
    state = {}

    # --------------------------------------------------
    # 1. Run Planner
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("RUNNING PLANNER")
    print("=" * 80)

    planner_result = await planner_node(state)

    # Add Planner output to state
    state.update(planner_result)

    print("\nPLANNER TIME WINDOW:")
    print(state["time_window"])

    # --------------------------------------------------
    # 2. Run Discovery Agent
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("RUNNING DISCOVERY AGENT")
    print("=" * 80)

    discovery_result = await discovery_agent_node(state)

    # Add Discovery output to state
    state.update(discovery_result)

    entities = state.get(
        "discovered_entities",
        [],
    )

    print("\n" + "=" * 80)
    print("DISCOVERED ENTITIES")
    print("=" * 80)

    print(
        f"Total entities: {len(entities)}"
    )

    for entity in entities:

        print(
            f"\nName: {entity.name}"
        )

        print(
            f"Type: {entity.entity_type}"
        )

        print(
            f"Reason: {entity.reason}"
        )

    # --------------------------------------------------
    # 3. Run People Agent
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("RUNNING PEOPLE AGENT")
    print("=" * 80)

    people_result = await people_agent_node(
        state
    )

    # --------------------------------------------------
    # 4. Display results
    # --------------------------------------------------

    tweets = people_result.get(
        "tweets",
        [],
    )

    print("\n" + "=" * 80)
    print("PEOPLE AGENT RESULT")
    print("=" * 80)

    print(
        f"\nEXTRACTED TWEETS: {len(tweets)}"
    )

    for i, tweet in enumerate(
        tweets,
        start=1,
    ):

        print("\n" + "-" * 70)
        print(f"TWEET {i}")

        if hasattr(tweet, "model_dump"):
            data = tweet.model_dump()
        else:
            data = tweet

        for key, value in data.items():

            print(
                f"{key.upper()}: {value}"
            )

    print("\nPROGRESS:")

    for item in people_result.get(
        "progress",
        [],
    ):

        print("-", item)


if __name__ == "__main__":
    asyncio.run(main())