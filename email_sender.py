import os
import resend

from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv("FROM_EMAIL")


def send_newsletter(
    to_email: str,
    subject: str,
    html: str
):

    if not resend.api_key:
        raise RuntimeError(
            "RESEND_API_KEY is missing"
        )

    if not FROM_EMAIL:
        raise RuntimeError(
            "FROM_EMAIL is missing"
        )

    response = resend.Emails.send({
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html,
    })

    return response