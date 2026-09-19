from crewai import Agent

from src.llm import get_sa_llm
from src.tools import get_serper_tool

from .prompt import SOLUTION_ARCHITECT_PROMPT


def create_solution_architect() -> Agent:
    """
    Create and configure the Solution Architect agent.
    """

    return Agent(
        role="Solution Architect",
        goal=(
            "Design a scalable, secure, and realistic high-level "
            "architecture based on the Business Analyst requirements."
        ),
        backstory=SOLUTION_ARCHITECT_PROMPT,
        llm=get_sa_llm(),
        tools=[get_serper_tool()],
        allow_delegation=False,
        verbose=True,
    )