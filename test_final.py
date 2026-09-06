import asyncio

from graph import app


async def main():

    print("\nStarting AI Newsletter pipeline...\n")

    result = await app.ainvoke({})

    print("\n" + "=" * 80)
    print("NEWSLETTER GENERATED")
    print("=" * 80)

    print(result.get("newsletter_markdown", ""))


if __name__ == "__main__":
    asyncio.run(main())