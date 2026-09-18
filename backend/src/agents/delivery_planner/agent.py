from crewai import Agent

from src.llm import get_llm
from src.tools import get_serper_tool

from .prompt import DELIVERY_PLANNER_PROMPT


def create_delivery_planner() -> Agent:
    """
    Create and configure the Delivery Planner agent.
    """

    return Agent(
        role="Delivery Planner",
        goal=(
            "Create a realistic implementation plan that delivers "
            "the agreed MVP within the requested timeline."
        ),
        backstory=DELIVERY_PLANNER_PROMPT,
        llm=get_llm(),
        tools=[get_serper_tool()],
        allow_delegation=False,
        verbose=True,
    )