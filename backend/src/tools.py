import os

from dotenv import load_dotenv
from crewai_tools import SerperDevTool

load_dotenv()


def get_serper_tool() -> SerperDevTool:
    """Create the shared Serper web-search tool."""

    api_key = os.getenv("SERPER_API_KEY")

    if not api_key:
        raise ValueError("SERPER_API_KEY is not set.")

    return SerperDevTool(n_results=5)