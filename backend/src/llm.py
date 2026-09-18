import os

from dotenv import load_dotenv

from crewai import LLM

import crewai.llms.cache as _crewai_cache

_crewai_cache.mark_cache_breakpoint = lambda msg: msg


load_dotenv()


def get_llm() -> LLM:
    """Create the LLM used by the CrewAI agents."""

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")

    if not model:
        raise ValueError("GROQ_MODEL is not set.")

    return LLM(
        model=f"groq/{model}",
        api_key=api_key,
        max_tokens=500,
    )