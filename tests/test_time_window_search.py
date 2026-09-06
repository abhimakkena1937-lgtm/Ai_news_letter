import asyncio

from tools.web_search import tavily_search


async def main():

    time_window = (
        "2026-08-23T12:00:00+00:00 "
        "to "
        "2026-08-24T12:00:00+00:00"
    )

    print("=" * 70)
    print("TIME WINDOW TEST")
    print("=" * 70)
    print("WINDOW:", time_window)

    results = await tavily_search(
        "latest AI news",
        max_results=5,
        time_window=time_window,
    )

    print("\nRESULTS:", len(results))

    for i, item in enumerate(results, 1):

        print("\n" + "-" * 70)
        print("RESULT:", i)
        print("TITLE:", item.get("title"))
        print("PUBLISHED:", item.get("published_at"))
        print("URL:", item.get("url"))


if __name__ == "__main__":
    asyncio.run(main())