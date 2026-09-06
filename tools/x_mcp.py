from __future__ import annotations

import base64
import hashlib
import http.server
import json
import os
import secrets
import threading
import time
import webbrowser
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
from dotenv import load_dotenv

load_dotenv()
X_CLIENT_ID = os.getenv("X_CLIENT_ID")
X_CLIENT_SECRET = os.getenv("X_CLIENT_SECRET")

X_AUTHORIZATION_ENDPOINT = "https://x.com/i/oauth2/authorize"
X_TOKEN_ENDPOINT = "https://api.x.com/2/oauth2/token"
X_MCP_URL = "https://api.x.com/mcp"

REDIRECT_URI = "http://localhost:8080/callback"

SCOPES = [
    "tweet.read",
    "users.read",
    "offline.access",
]


if not X_CLIENT_ID:
    raise RuntimeError("X_CLIENT_ID is missing")

if not X_CLIENT_SECRET:
    raise RuntimeError("X_CLIENT_SECRET is missing")


# ---------------------------------------------------------
# PKCE
# ---------------------------------------------------------


def parse_sse_response(text: str) -> list[dict]:

    messages = []

    for line in text.splitlines():

        line = line.strip()

        if not line.startswith("data:"):
            continue

        data = line[len("data:"):].strip()

        if not data:
            continue

        try:
            messages.append(json.loads(data))
        except json.JSONDecodeError:
            continue

    return messages
def create_pkce():

    verifier = (
        base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        )
        .decode()
        .rstrip("=")
    )

    challenge = (
        base64.urlsafe_b64encode(
            hashlib.sha256(
                verifier.encode()
            ).digest()
        )
        .decode()
        .rstrip("=")
    )

    return verifier, challenge


# ---------------------------------------------------------
# OAuth callback server
# ---------------------------------------------------------

class OAuthCallbackHandler(
    http.server.BaseHTTPRequestHandler
):

    code = None
    error = None

    def do_GET(self):

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "error" in params:
            OAuthCallbackHandler.error = (
                params["error"][0]
            )

        if "code" in params:
            OAuthCallbackHandler.code = (
                params["code"][0]
            )

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html",
        )
        self.end_headers()

        self.wfile.write(
            b"""
            <html>
            <body>
            <h2>X authorization received.</h2>
            <p>You can close this window.</p>
            </body>
            </html>
            """
        )

    def log_message(self, *args):
        pass


def wait_for_callback():

    OAuthCallbackHandler.code = None
    OAuthCallbackHandler.error = None

    server = http.server.HTTPServer(
        ("localhost", 8080),
        OAuthCallbackHandler,
    )

    thread = threading.Thread(
        target=server.handle_request,
        daemon=True,
    )

    thread.start()

    return server, thread


# ---------------------------------------------------------
# OAuth
# ---------------------------------------------------------

async def get_access_token():

    verifier, challenge = create_pkce()

    state = secrets.token_urlsafe(32)

    params = {
        "response_type": "code",
        "client_id": X_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }

    authorization_url = (
        X_AUTHORIZATION_ENDPOINT
        + "?"
        + urlencode(params)
    )

    server, thread = wait_for_callback()

    print("\nOpening X authorization...")
    print(authorization_url)

    webbrowser.open(
        authorization_url
    )

    print(
        "\nWaiting for X authorization..."
    )

    thread.join(timeout=300)

    server.server_close()

    if OAuthCallbackHandler.error:
        raise RuntimeError(
            "X OAuth error: "
            + OAuthCallbackHandler.error
        )

    code = OAuthCallbackHandler.code

    if not code:
        raise RuntimeError(
            "No authorization code received"
        )

    async with httpx.AsyncClient() as client:

        response = await client.post(
            X_TOKEN_ENDPOINT,
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
                "code_verifier": verifier,
            },
            auth=(
                X_CLIENT_ID,
                X_CLIENT_SECRET,
            ),
        )

        print(
            "TOKEN STATUS:",
            response.status_code,
        )

        if response.status_code != 200:
            print(response.text)

        response.raise_for_status()

        token_data = response.json()

    return token_data["access_token"]


# ---------------------------------------------------------
# MCP JSON-RPC
# ---------------------------------------------------------

async def mcp_request(
    client: httpx.AsyncClient,
    access_token: str,
    request_id: int,
    method: str,
    params: dict | None = None,
):

    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }

    if params is not None:
        payload["params"] = params

    response = await client.post(
        X_MCP_URL,
        headers={
            "Authorization":
                f"Bearer {access_token}",
            "Content-Type":
                "application/json",
            "Accept":
                "application/json, text/event-stream",
        },
        json=payload,
        timeout=60,
    )

    print(
        "MCP STATUS:",
        response.status_code,
    )

    if response.status_code != 200:
        print(response.text)

    response.raise_for_status()

    return response


# ---------------------------------------------------------
# Test MCP
# ---------------------------------------------------------

async def test_x_mcp():

    access_token = await get_access_token()

    async with httpx.AsyncClient() as client:

        # Initialize MCP
        response = await mcp_request(
            client,
            access_token,
            1,
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "ai-newsletter",
                    "version": "1.0.0",
                },
            },
        )

        print("\nINITIALIZE RESPONSE:")
        print(response.text)

        # List tools
        response = await mcp_request(
            client,
            access_token,
            2,
            "tools/list",
            {},
        )

        print("\nX MCP TOOLS:")

        messages = parse_sse_response(
            response.text
        )

        for message in messages:
            print(
                json.dumps(
                    message,
                    indent=2,
                )
            )
async def search_x_posts(
    query: str,
    time_window: str,
    max_results: int = 10,
) -> list[dict]:

    bearer_token = os.getenv("X_BEARER_TOKEN")

    if not bearer_token:
        raise RuntimeError(
            "X_BEARER_TOKEN is missing"
        )

    start_time, end_time = time_window.split(
        " to ",
        1,
    )

    async with httpx.AsyncClient() as client:

        await mcp_request(
            client,
            bearer_token,
            1,
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "ai-newsletter",
                    "version": "1.0.0",
                },
            },
        )

        response = await mcp_request(
            client,
            bearer_token,
            2,
            "tools/call",
            {
                "name": "search_posts_all",
                "arguments": {
                    "query": query,
                    "start_time": start_time,
                    "end_time": end_time,
                    "max_results": max_results,
                    "sort_order": "recency",
                    "post.fields": (
                        "id,text,created_at,author_id"
                    ),
                    "user.fields": (
                        "id,name,username"
                    ),
                },
            },
        )

        return parse_sse_response(
            response.text
        )

if __name__ == "__main__":

    import asyncio

    asyncio.run(
        test_x_mcp()
    )