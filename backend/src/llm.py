import os
import crewai.llms.cache as _crewai_cache
from crewai import LLM
from src.config import settings

_crewai_cache.mark_cache_breakpoint = lambda msg: msg


def get_llm(api_key: str) -> LLM:
    """Create an LLM instance with a specific API key."""
    return LLM(
        model=settings.GEMINI_MODEL,
        api_key=api_key,
        max_tokens=8192,
    )


def get_ba_llm() -> LLM:
    return get_llm(os.getenv("GEMINI_API_KEY_BA", settings.GEMINI_API_KEY_BA))


def get_sa_llm() -> LLM:
    return get_llm(os.getenv("GEMINI_API_KEY_SA", settings.GEMINI_API_KEY_SA))


def get_ta_llm() -> LLM:
    return get_llm(os.getenv("GEMINI_API_KEY_TA", settings.GEMINI_API_KEY_TA))


def get_dp_llm() -> LLM:
    return get_llm(os.getenv("GEMINI_API_KEY_DP", settings.GEMINI_API_KEY_DP))


def get_do_llm() -> LLM:
    api_key = os.getenv("GEMINI_API_KEY_DO") or settings.GEMINI_API_KEY_DO or os.getenv("GEMINI_API_KEY_TA", settings.GEMINI_API_KEY_TA)
    return get_llm(api_key)


def get_rw_llm() -> LLM:
    api_key = os.getenv("GEMINI_API_KEY_RW") or settings.GEMINI_API_KEY_RW or os.getenv("GEMINI_API_KEY_DP", settings.GEMINI_API_KEY_DP)
    return get_llm(api_key)


def get_ev_llm() -> LLM:
    api_key = os.getenv("GEMINI_API_KEY_EV") or settings.GEMINI_API_KEY_EV or os.getenv("GEMINI_API_KEY_BA", settings.GEMINI_API_KEY_BA)
    model_name = settings.EVALUATION_MODEL or settings.GEMINI_MODEL
    return LLM(
        model=model_name,
        api_key=api_key,
        max_tokens=8192,
    )