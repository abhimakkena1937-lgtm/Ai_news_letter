import asyncio

from graph import app


async def main():

    result = await app.ainvoke({})

    ranked_context = result.get("ranked_context")

    print("\n" + "=" * 80)
    print("IMAGE RESULTS")
    print("=" * 80)

    if not ranked_context:
        print("No ranked context found.")
        return

    for item in ranked_context.top_news:
        print("\nNEWS:")
        print("Title:", item.title)
        print("Image:", item.image_url)

    for item in ranked_context.top_start_ups:
        print("\nSTARTUP:")
        print("Name:", item.startup_name)
        print("Image:", item.image_url)

    for item in ranked_context.top_tweets:
        print("\nPERSON:")
        print("Person:", item.person)
        print("Image:", item.image_url)

    for item in ranked_context.top_github_repos:
        print("\nGITHUB:")
        print("Repo:", item.repo_name)
        print("Image:", item.image_url)

    for item in ranked_context.top_papers:
        print("\nPAPER:")
        print("Title:", item.title)
        print("Image:", item.image_url)


if __name__ == "__main__":
    asyncio.run(main())