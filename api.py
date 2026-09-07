from pathlib import Path


from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr

from database import add_subscriber, unsubscribe
from fastapi import FastAPI, Query

app = FastAPI(title="AI Daily Newsletter API")




class SubscribeRequest(BaseModel):
    email: EmailStr


@app.get("/", response_class=HTMLResponse)
def home():
    return Path("templates/index.html").read_text(encoding="utf-8")


@app.post("/subscribe")
def subscribe(request: SubscribeRequest):
    added = add_subscriber(str(request.email))

    if not added:
        return {"message": "Email is already subscribed"}

    return {"message": "Successfully subscribed"}


@app.post("/unsubscribe")
def remove_subscriber(request: SubscribeRequest):
    removed = unsubscribe(str(request.email))

    if not removed:
        return {"message": "This email is not currently subscribed."}

    return {"message": "Successfully unsubscribed"}

@app.get("/unsubscribe", response_class=HTMLResponse)
def unsubscribe_user(email: EmailStr = Query(...)):
    removed = unsubscribe(str(email))

    if not removed:
        message = "This email is not currently subscribed."
    else:
        message = "You have been successfully unsubscribed from AI Daily."

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Daily - Unsubscribe</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f7fa;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }}

            .card {{
                background: white;
                padding: 40px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                max-width: 500px;
                margin: 20px;
            }}

            h1 {{
                margin-bottom: 15px;
            }}

            p {{
                color: #555;
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>AI Daily</h1>
            <p>{message}</p>
        </div>
    </body>
    </html>
    """