import asyncio
from urllib.parse import quote

from state import NewsLetterState
from database import get_active_subscribers
from email_sender import send_newsletter


async def email_node(state: NewsLetterState) -> dict:
    print("\n" + "=" * 80)
    print("RUNNING EMAIL AGENT")
    print("=" * 80)

    html = state["newsletter_html"]
    date = state["date"]
    subject = f"AI Daily — {date}"

    subscribers = get_active_subscribers()

    if not subscribers:
        print("No active subscribers.")
        return {"progress": ["email: no active subscribers"]}

    sent = 0
    failed = 0

    for email in subscribers:

        unsubscribe_url = (
            "https://ai-news-letter-y02i.onrender.com/unsubscribe"
            f"?email={quote(email)}"
        )

        email_html = html + f"""
        <hr>
        <p style="text-align:center; font-size:12px; color:#777;">
            Don't want to receive these emails?
            <a href="{unsubscribe_url}">Unsubscribe</a>
        </p>
        """

        max_retries = 3
        email_sent = False

        for attempt in range(1, max_retries + 1):
            try:
                send_newsletter(
                    to_email=email,
                    subject=subject,
                    html=email_html
                )

                sent += 1
                email_sent = True

                print(
                    f"Email sent: {email} "
                    f"(attempt {attempt})"
                )

                break

            except Exception as e:
                print(
                    f"Email attempt {attempt}/{max_retries} "
                    f"failed: {email} -> {e}"
                )

                if attempt < max_retries:
                    await asyncio.sleep(2)

        if not email_sent:
            failed += 1
            print(f"Email permanently failed: {email}")

    print("\nEMAIL SUMMARY")
    print("Subscribers:", len(subscribers))
    print("Sent:", sent)
    print("Failed:", failed)

    return {
        "progress": [
            f"email: sent to {sent} subscribers",
            f"email: {failed} failures"
        ]
    }