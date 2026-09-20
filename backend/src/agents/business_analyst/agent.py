from crewai import Agent

from src.llm import get_ba_llm
from src.tools import get_serper_tool
from .prompt import BUSINESS_ANALYST_PROMPT


def create_business_analyst() -> Agent:
    """
    Create and configure the Business Analyst agent.
    """

    return Agent(
        role="Business Analyst",
        goal=(
            "Analyze the user's business idea and constraints, "
            "identify clear business requirements, and define a "
            "realistic MVP scope without making technology decisions."
        ),
        backstory=BUSINESS_ANALYST_PROMPT,
        llm=get_ba_llm(),
        tools=[],
        allow_delegation=False,
        verbose=True,
    )