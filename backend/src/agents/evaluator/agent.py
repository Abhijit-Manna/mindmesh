from crewai import Agent

from src.llm import get_ev_llm
from .prompt import EVALUATOR_PROMPT


def create_evaluator() -> Agent:
    """
    Create and configure the Evaluation & Quality Gate agent.
    """
    return Agent(
        role="Quality & Evaluation Auditor",
        goal=(
            "Critically evaluate consulting agent deliverables against required constraints, "
            "completeness, and realism, providing an objective quality score and actionable feedback."
        ),
        backstory=EVALUATOR_PROMPT,
        llm=get_ev_llm(),
        allow_delegation=False,
        verbose=True,
    )