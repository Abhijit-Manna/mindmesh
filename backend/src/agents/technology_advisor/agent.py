from crewai import Agent

from src.llm import get_ta_llm
from src.tools import get_serper_tool

from .prompt import TECHNOLOGY_ADVISOR_PROMPT


def create_technology_advisor() -> Agent:
    """
    Create and configure the Technology Advisor agent.
    """

    return Agent(
        role="Technology Advisor",
        goal=(
            "Select a practical technology stack that satisfies the "
            "business requirements and proposed architecture."
        ),
        backstory=TECHNOLOGY_ADVISOR_PROMPT,
        llm=get_ta_llm(),
        tools=[get_serper_tool()],
        config={},
        allow_delegation=False,
        verbose=True,
    )