from state import NewsLetterState
from database import get_active_subscribers
from email_sender import send_newsletter


async def email_node(state: NewsLetterState) -> dict:

    print("\n" + "=" * 80)
    print("RUNNING EMAIL NODE")
    print("=" * 80)

    html = state["newsletter_html"]
    date = state["date"]

    subject = f"AI Daily — {date}"

    subscribers = get_active_subscribers()

    if not subscribers:
        print("No active subscribers.")

        return {
            "progress": [
                "email: no active subscribers"
            ]
        }

    sent = 0
    failed = 0

    for email in subscribers:

        try:

            send_newsletter(
                to_email=email,
                subject=subject,
                html=html
            )

            sent += 1

            print(
                f"Email sent: {email}"
            )

        except Exception as e:

            failed += 1

            print(
                f"Email failed: {email} -> {e}"
            )

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