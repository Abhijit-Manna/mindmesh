import os

from dotenv import load_dotenv
from crewai import LLM

load_dotenv()


def get_llm() -> LLM:
    """Create the LLM used by the CrewAI agents."""

    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set.")

    if not model:
        raise ValueError("OPENROUTER_MODEL is not set.")

    return LLM(
        model=f"openrouter/{model}",
        api_key=api_key,
        max_tokens=4096,
    )