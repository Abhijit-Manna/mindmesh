import os

import crewai.llms.cache as _crewai_cache

from crewai import LLM

from src.config import settings


_crewai_cache.mark_cache_breakpoint = lambda msg: msg


def _read_setting(env_name: str, settings_name: str) -> str:
    """Read the first available non-empty setting value."""
    env_value = os.getenv(env_name, "").strip()
    if env_value:
        return env_value

    settings_value = getattr(settings, settings_name, "")
    if isinstance(settings_value, str):
        return settings_value.strip()

    return ""


def _require_value(value: str, label: str) -> str:
    if not value or not value.strip():
        raise ValueError(
            f"Missing {label}. Set the environment variable or configure the corresponding setting."
        )
    return value.strip()


def get_llm(api_key: str, model: str, temperature: float = 0.4) -> LLM:
    """Create an LLM instance with a specific API key and model."""
    safe_api_key = _require_value(api_key, "API key")
    safe_model = _require_value(model, "model")

    return LLM(
        model=safe_model,
        api_key=safe_api_key,
        max_tokens=16384,
        temperature=temperature,
    )


def get_ba_llm() -> LLM:
    return get_llm(
        api_key=_read_setting("GEMINI_API_KEY_BA", "GEMINI_API_KEY_BA"),
        model=_read_setting("BA_MODEL", "BA_MODEL"),
    )


def get_sa_llm() -> LLM:
    return get_llm(
        api_key=_read_setting("GEMINI_API_KEY_SA", "GEMINI_API_KEY_SA"),
        model=_read_setting("SA_MODEL", "SA_MODEL"),
    )


def get_ta_llm() -> LLM:
    return get_llm(
        api_key=_read_setting("GEMINI_API_KEY_TA", "GEMINI_API_KEY_TA"),
        model=_read_setting("TA_MODEL", "TA_MODEL"),
    )


def get_dp_llm() -> LLM:
    return get_llm(
        api_key=_read_setting("GEMINI_API_KEY_DP", "GEMINI_API_KEY_DP"),
        model=_read_setting("DP_MODEL", "DP_MODEL"),
    )


def get_rw_llm() -> LLM:
    return get_llm(
        api_key=_read_setting("GEMINI_API_KEY_RW", "GEMINI_API_KEY_RW"),
        model=_read_setting("RW_MODEL", "RW_MODEL"),
    )


def get_ev_llm() -> LLM:
    return get_llm(
        api_key=_read_setting("GEMINI_API_KEY_EV", "GEMINI_API_KEY_EV"),
        model=_read_setting("EVALUATION_MODEL", "EVALUATION_MODEL"),
    )