from crewai import Agent

from src.llm import get_rw_llm
from .prompt import REPORT_WRITER_PROMPT


def create_report_writer() -> Agent:
    """
    Create and configure the Report Writer agent.
    """
    return Agent(
        role="Lead Solution Consultant & Technical Writer",
        goal=(
            "Synthesize all upstream agent findings into a polished, consistent, "
            "and complete 14-section Enterprise Solution Blueprint in executive Markdown format."
        ),
        backstory=REPORT_WRITER_PROMPT,
        llm=get_rw_llm(),
        config={},
        allow_delegation=False,
        verbose=True,
    )