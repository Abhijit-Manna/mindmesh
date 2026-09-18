from crewai_tools import SerperDevTool
from src.config import settings


def get_serper_tool() -> SerperDevTool:
    """Create the shared Serper web-search tool."""
    return SerperDevTool(
        api_key=settings.SERPER_API_KEY,
        n_results=5,
    )