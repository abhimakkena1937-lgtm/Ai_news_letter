import asyncio

from nodes.planner import planner_node
from nodes.github_agent import github_agent_node


async def main():

    state = {}

    # -------------------------------------------------
    # Planner
    # -------------------------------------------------

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

    # -------------------------------------------------
    # GitHub Agent
    # -------------------------------------------------

    print("=" * 80)
    print("RUNNING GITHUB AGENT")
    print("=" * 80)

    github_result = await github_agent_node(
        state
    )

    state.update(
        github_result
    )

    # -------------------------------------------------
    # Final output
    # -------------------------------------------------

    repositories = state.get(
        "github_repos",
        []
    )

    print("\n")
    print("=" * 80)
    print("FINAL NEW AI GITHUB REPOSITORIES")
    print("=" * 80)

    for i, repo in enumerate(
        repositories,
        start=1,
    ):

        print(f"\n{i}. {repo.repo_name}")

        print(
            "GitHub:",
            repo.url
        )

        print(
            "Description:",
            repo.description
        )

        print(
            "Reason:",
            repo.reason
        )

        if repo.stars is not None:
            print(
                "Stars:",
                repo.stars
            )

        if repo.language:
            print(
                "Language:",
                repo.language
            )

    print(
        "\nTOTAL:",
        len(repositories)
    )


if __name__ == "__main__":
    asyncio.run(main())