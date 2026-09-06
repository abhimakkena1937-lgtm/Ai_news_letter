import asyncio

from tools.freshness import check_freshness


async def main():

    event = """
    HEADLINE: Google introduces new Ironwood AI chip for inference workloads
    COMPANY: Google
    SUMMARY: Google unveiled its seventh-generation AI chip, Ironwood,
    designed to accelerate inference performance.
    PUBLISHED: 2025-04-09
    SOURCE: https://example.com/ironwood
    """

    result = await check_freshness(
        event_text=event,
        time_window="August 14, 2026 to August 24, 2026",
    )

    print("\nFRESHNESS RESULT")
    print("=" * 60)
    print("IS RECENT:", result.is_recent)
    print("EVENT DATE:", result.event_date)
    print("REASON:", result.reason)


if __name__ == "__main__":
    asyncio.run(main())