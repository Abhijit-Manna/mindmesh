import os

from crewai import LLM


def get_llm() -> LLM:
    """
    Create and return the CrewAI LLM configured to use OpenRouter.

    API credentials and model configuration are read from environment
    variables so that secrets are never hard-coded in the source code.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set in the environment."
        )

    if not model:
        raise ValueError(
            "OPENROUTER_MODEL is not set in the environment."
        )

    return LLM(
        model=f"openrouter/{model}",
        api_key=api_key,
    )