import asyncio

from graph import app


async def main():

    print("=" * 80)
    print("RUNNING FULL NEWSLETTER GRAPH")
    print("=" * 80)

    result = await app.ainvoke({})

    print("\n" + "=" * 80)
    print("GRAPH FINISHED")
    print("=" * 80)

    ranked = result.get("ranked_context")

    if ranked:

        print("\nTOP NEWS:")
        for item in ranked.top_news:
            print("-", item)

        print("\nTOP STARTUPS:")
        for item in ranked.top_start_ups:
            print("-", item)

        print("\nTOP TWEETS:")
        for item in ranked.top_tweets:
            print("-", item)

        print("\nTOP GITHUB:")
        for item in ranked.top_github_repos:
            print("-", item)

        print("\nTOP PAPERS:")
        for item in ranked.top_papers:
            print("-", item)

        print("\nTOOL OF THE DAY:")
        print(ranked.tool_of_the_day)


if __name__ == "__main__":
    asyncio.run(main())