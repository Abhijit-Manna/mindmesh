from crewai import Agent

from backend.src.llm import get_llm
from backend.src.tools import get_serper_tool
from .prompt import BUSINESS_ANALYST_SYSTEM_PROMPT


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
        backstory=BUSINESS_ANALYST_SYSTEM_PROMPT,
        llm=get_llm(),
        tools=[get_serper_tool()],
        allow_delegation=False,
        verbose=True,
    )