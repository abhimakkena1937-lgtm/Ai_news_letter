import asyncio

from nodes.discovery_agent import discover_web_results


async def main():
    time_window = "2026-09-05T16:10:04.556151+00:00 to 2026-09-06T16:10:04.556151+00:00"

    results = await discover_web_results(time_window)

    print("\n" + "=" * 80)
    print("DISCOVERY TEST COMPLETE")
    print("=" * 80)
    print("Results:", len(results))

    for result in results[:5]:
        print("\nTitle:", result.get("title"))
        print("URL:", result.get("url"))


if __name__ == "__main__":
    asyncio.run(main())