import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite",
)

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")
GITHUB_MCP_URL=os.getenv("GITHUB_MCP_URL")
GITHUB_MCP_TOKEN=os.getenv("GITHUB_MCP_TOKEN")
X_MCP_URL=os.getenv("X_MCP_URL")
X_MCP_AUTH_TOKEN=os.getenv("X_MCP_AUTH_TOKEN")
EXA_API_KEY = os.getenv("EXA_API_KEY")

