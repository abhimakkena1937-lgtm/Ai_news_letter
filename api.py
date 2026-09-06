from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from fastapi.responses import HTMLResponse
from pathlib import Path

from database import (
    init_db,
    add_subscriber,
    unsubscribe,
)


app = FastAPI(
    title="AI Daily Newsletter API"
)


init_db()


class SubscribeRequest(BaseModel):
    email: EmailStr


@app.get("/", response_class=HTMLResponse)
def home():

    html_file = Path(
        "templates/index.html"
    )

    return html_file.read_text(
        encoding="utf-8"
    )


@app.post("/subscribe")
def subscribe(
    request: SubscribeRequest
):

    added = add_subscriber(
        str(request.email)
    )

    if not added:
        return {
            "message": "Email is already subscribed"
        }

    return {
        "message": "Successfully subscribed"
    }


@app.post("/unsubscribe")
def remove_subscriber(
    request: SubscribeRequest
):

    unsubscribe(
        str(request.email)
    )

    return {
        "message": "Successfully unsubscribed"
    }