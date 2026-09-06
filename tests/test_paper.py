import asyncio

from nodes.planner import planner_node
from nodes.paper_agent import paper_agent_node


async def main():

    state = {}

    # -------------------------------
    # Planner
    # -------------------------------

    print("=" * 80)
    print("RUNNING PLANNER")
    print("=" * 80)

    planner_result = await planner_node(
        state
    )

    state.update(
        planner_result
    )

    print("\nPLANNER TIME WINDOW:")
    print(
        state["time_window"]
    )

    # -------------------------------
    # Paper Agent
    # -------------------------------

    print("=" * 80)
    print("RUNNING PAPER AGENT")
    print("=" * 80)

    paper_result = await paper_agent_node(
        state
    )

    state.update(
        paper_result
    )

    # -------------------------------
    # Final output
    # -------------------------------

    papers = state.get(
        "research_papers",
        []
    )

    print("\n")
    print("=" * 80)
    print("FINAL NEW AI RESEARCH PAPERS")
    print("=" * 80)

    for i, paper in enumerate(
        papers,
        start=1,
    ):

        print(
            f"\n{i}. {paper.title}"
        )

        print(
            "Authors:",
            paper.authors
        )

        print(
            "URL:",
            paper.url
        )

        print(
            "Summary:",
            paper.summary
        )

        print(
            "Reason:",
            paper.reason
        )

    print(
        "\nTOTAL:",
        len(papers)
    )


if __name__ == "__main__":
    asyncio.run(main())