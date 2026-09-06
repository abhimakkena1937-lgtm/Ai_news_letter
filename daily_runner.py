import asyncio

from graph import app


async def run_daily_newsletter():

    print("\n" + "=" * 80)
    print("STARTING DAILY AI NEWSLETTER")
    print("=" * 80)

    try:

        result = await app.ainvoke({})

        print("\n" + "=" * 80)
        print("DAILY NEWSLETTER COMPLETED")
        print("=" * 80)

        print(result.get("progress", []))

        return result

    except Exception as e:

        print("\n" + "=" * 80)
        print("DAILY NEWSLETTER FAILED")
        print("=" * 80)

        print(e)

        raise


if __name__ == "__main__":
    asyncio.run(run_daily_newsletter())