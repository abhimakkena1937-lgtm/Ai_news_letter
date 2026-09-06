import asyncio

from nodes.planner import planner_node
from nodes.discovery_agent import discovery_agent_node
from nodes.startup_agent import startup_agent_node


async def main():

    # 1. Planner
    planner_state = await planner_node({})

    print("\n" + "=" * 70)
    print("PLANNER")
    print("=" * 70)
    print("TIME WINDOW:", planner_state["time_window"])

    # 2. Discovery
    discovery_result = await discovery_agent_node(
        planner_state
    )

    entities = discovery_result.get(
        "discovered_entities",
        []
    )

    print("\n" + "=" * 70)
    print("DISCOVERED ENTITIES:", len(entities))
    print("=" * 70)

    for entity in entities:
        print(
            f"{entity.name} | "
            f"{entity.entity_type}"
        )

    # 3. Startup Agent
    state = {
        "discovered_entities": entities,
        "time_window": planner_state["time_window"],
    }

    result = await startup_agent_node(state)

    startups = result.get(
        "startups",
        []
    )

    print("\n" + "=" * 70)
    print("EXTRACTED STARTUPS:", len(startups))
    print("=" * 70)

    for i, startup in enumerate(startups, 1):

        print("\n" + "-" * 70)
        print(f"STARTUP {i}")
        print("NAME:", startup.startup_name)
        print("DESCRIPTION:", startup.description)
        print("FUNDING:", startup.funding)
        print("INVESTORS:", startup.investors)
        print("SOURCE:", startup.source)
        print("URL:", startup.url)
        print("EVIDENCE ID:", startup.evidence_id)

    print("\nPROGRESS:")

    for item in result.get("progress", []):
        print("-", item)


if __name__ == "__main__":
    asyncio.run(main())