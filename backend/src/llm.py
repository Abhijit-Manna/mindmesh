import os

import crewai.llms.cache as _crewai_cache

from crewai import LLM

from src.config import settings


_crewai_cache.mark_cache_breakpoint = lambda msg: msg


def get_llm(api_key: str, model: str) -> LLM:
    """Create an LLM instance routed through OmniRoute."""
    return LLM(
        model="openai/gemini-fallout",
        api_key=settings.OMNIROUTE_API_KEY,
        base_url=settings.OMNIROUTE_BASE_URL,
        max_tokens=1000,
    )


def get_ba_llm() -> LLM:
    return get_llm(
        api_key=os.getenv("GEMINI_API_KEY_BA", settings.GEMINI_API_KEY_BA),
        model=settings.BA_MODEL,
    )


def get_sa_llm() -> LLM:
    return get_llm(
        api_key=os.getenv("GEMINI_API_KEY_SA", settings.GEMINI_API_KEY_SA),
        model=settings.SA_MODEL,
    )


def get_ta_llm() -> LLM:
    return get_llm(
        api_key=os.getenv("GEMINI_API_KEY_TA", settings.GEMINI_API_KEY_TA),
        model=settings.TA_MODEL,
    )


def get_dp_llm() -> LLM:
    return get_llm(
        api_key=os.getenv("GEMINI_API_KEY_DP", settings.GEMINI_API_KEY_DP),
        model=settings.DP_MODEL,
    )



def get_rw_llm() -> LLM:
    return get_llm(
        api_key=os.getenv("GEMINI_API_KEY_RW", settings.GEMINI_API_KEY_RW),
        model=settings.RW_MODEL,
    )


def get_ev_llm() -> LLM:
    return get_llm(
        api_key=os.getenv("GEMINI_API_KEY_EV", settings.GEMINI_API_KEY_EV),
        model=settings.EVALUATION_MODEL,
    )