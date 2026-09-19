from crewai import Agent

from src.llm import get_do_llm
from src.tools import get_serper_tool
from .prompt import DEVOPS_ARCHITECT_PROMPT


def create_devops_architect() -> Agent:
    """
    Create and configure the DevOps Architect agent.
    """
    return Agent(
        role="DevOps Architect",
        goal=(
            "Design the cloud infrastructure, CI/CD pipeline, environments, "
            "and zero-downtime release strategy tailored to the recommended stack."
        ),
        backstory=DEVOPS_ARCHITECT_PROMPT,
        llm=get_do_llm(),
        tools=[get_serper_tool()],
        allow_delegation=False,
        verbose=True,
    )