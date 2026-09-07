import os
import re
import mimetypes
import base64

import requests
import resend

from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")


def prepare_inline_images(html: str):

    image_urls = re.findall(
        r'<img[^>]+src=["\'](https?://[^"\']+)["\']',
        html,
        flags=re.IGNORECASE,
    )

    attachments = []

    for index, image_url in enumerate(image_urls, start=1):

        cid = f"newsletter-image-{index}"

        try:
            response = requests.get(
                image_url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            response.raise_for_status()

            content_type = (
                response.headers.get("Content-Type")
                or mimetypes.guess_type(image_url)[0]
                or "image/jpeg"
            )

            content_type = content_type.split(";")[0]

            extension = mimetypes.guess_extension(
                content_type
            ) or ".jpg"

            filename = f"newsletter-image-{index}{extension}"

            attachments.append({
                "content": base64.b64encode(
                    response.content
                ).decode("utf-8"),
                "filename": filename,
                "content_id": cid,
                "content_type": content_type,
            })

            html = html.replace(
                image_url,
                f"cid:{cid}"
            )

            print(
                f"Embedded image {index}: {image_url}"
            )

        except Exception as e:
            print(
                f"Image download failed: "
                f"{image_url} -> {e}"
            )

    return html, attachments


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

    html, attachments = prepare_inline_images(html)

    response = resend.Emails.send({
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html,
        "attachments": attachments,
    })

    return response