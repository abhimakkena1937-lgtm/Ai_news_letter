import asyncio

from graph import app


async def main():

    result = await app.ainvoke({})

    print("\n" + "=" * 80)
    print("FINAL NEWSLETTER")
    print("=" * 80)

    print(
        result.get(
            "newsletter_markdown",
            "No newsletter generated."
        )
    )


if __name__ == "__main__":
    asyncio.run(main())