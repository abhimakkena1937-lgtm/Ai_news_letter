import asyncio

from nodes.planner import planner_node
from nodes.discovery_agent import discovery_agent_node


async def main():

    # 1. Run Planner
    planner_state = await planner_node({})

    print("\n" + "=" * 70)
    print("PLANNER")
    print("=" * 70)
    print("DATE:", planner_state["date"])
    print("TIME WINDOW:", planner_state["time_window"])

    # 2. Pass Planner state to Discovery
    result = await discovery_agent_node(
        planner_state
    )

    entities = result.get(
        "discovered_entities",
        []
    )

    print("\n" + "=" * 70)
    print("DISCOVERY")
    print("=" * 70)
    print("ENTITIES:", len(entities))

    for entity in entities:
        print("\n" + "-" * 70)
        print("NAME:", entity.name)
        print("TYPE:", entity.entity_type)
        print("REASON:", entity.reason)

    print("\nPROGRESS:")

    for item in result.get("progress", []):
        print("-", item)


if __name__ == "__main__":
    asyncio.run(main())