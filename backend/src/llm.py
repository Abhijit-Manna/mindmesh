import logging
import os
from typing import Any

import crewai.llms.cache as _crewai_cache

from crewai import LLM
from crewai.llms.base_llm import BaseLLM

from src.config import settings


_crewai_cache.mark_cache_breakpoint = lambda msg: msg

logger = logging.getLogger(__name__)


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


# Error fragments that indicate a transient provider-side problem where the
# OpenRouter fallback should be attempted. Matched case-insensitively against
# the string form of the raised exception.
_TRANSIENT_ERROR_FRAGMENTS = (
    "429",
    "rate limit",
    "ratelimit",
    "quota",
    "resource_exhausted",
    "resource exhausted",
    "overloaded",
    "overload",
    "503",
    "502",
    "500",
    "timeout",
    "timed out",
    "temporarily unavailable",
    "service unavailable",
    "capacity",
    "demand",
    "internal server error",
    "bad gateway",
    "connection error",
    "connection reset",
    "connection refused",
    "api error",
    "server error",
)


def _is_transient_error(error: BaseException) -> bool:
    """Return True when the error looks like a transient provider failure."""
    text = str(error).lower()
    return any(fragment in text for fragment in _TRANSIENT_ERROR_FRAGMENTS)


class FallbackLLM(BaseLLM):
    """
    CrewAI-compatible LLM wrapper with an OpenRouter fallback.

    The primary LLM is attempted first. When its call fails with a transient
    provider error (demand spike, resource exhaustion, rate limit, outage,
    timeout, ...) the same request is retried on OpenRouter using the
    configured fallback model.

    Subclassing BaseLLM keeps the wrapper valid anywhere CrewAI expects an
    LLM (Agent.llm, task-level LLMs, evaluator crews, ...).
    """

    llm_type: str = "fallback"

    # Injected after construction (not pydantic fields, so they are never
    # serialized or validated by pydantic).
    _primary: BaseLLM = None  # type: ignore[assignment]
    _fallback: BaseLLM | None = None  # type: ignore[assignment]
    _fallback_on_all_errors: bool = True

    def __init__(
        self,
        primary: BaseLLM,
        fallback: BaseLLM | None,
        fallback_on_all_errors: bool = True,
        **data: Any,
    ) -> None:
        # Seed pydantic fields from the primary so attribute reads such as
        # .model, .temperature, .max_tokens, .stop, ... reflect the primary
        # configuration.
        seed = {
            "model": getattr(primary, "model", "fallback"),
            "temperature": getattr(primary, "temperature", None),
            "top_p": getattr(primary, "top_p", None),
            "max_tokens": getattr(primary, "max_tokens", None),
            "stream": getattr(primary, "stream", None),
            "stop": getattr(primary, "stop", None),
        }
        seed.update(data)
        super().__init__(**seed)
        object.__setattr__(self, "_primary", primary)
        object.__setattr__(self, "_fallback", fallback)
        object.__setattr__(self, "_fallback_on_all_errors", fallback_on_all_errors)

    @property
    def fallback_model_name(self) -> str:
        fallback = self._fallback
        if fallback is None:
            return "openrouter"
        model = getattr(fallback, "model", "openrouter")
        provider = getattr(fallback, "provider", None)
        if provider and provider not in model:
            return f"{provider}/{model}"
        return model

    def call(
        self,
        messages: Any,
        tools: Any = None,
        callbacks: Any = None,
        available_functions: Any = None,
        from_task: Any = None,
        from_agent: Any = None,
        response_model: Any = None,
    ) -> Any:
        """Call the primary LLM; on qualifying failures, use the fallback."""
        try:
            return self._primary.call(
                messages,
                tools=tools,
                callbacks=callbacks,
                available_functions=available_functions,
                from_task=from_task,
                from_agent=from_agent,
                response_model=response_model,
            )
        except Exception as primary_error:
            if not self._should_fallback(primary_error):
                raise

            logger.warning(
                "Primary LLM (%s) call failed (%s); falling back to %s.",
                getattr(self._primary, "model", "primary"),
                primary_error,
                self.fallback_model_name,
            )

            fallback = self._fallback
            if fallback is None:
                raise

            try:
                return fallback.call(
                    messages,
                    tools=tools,
                    callbacks=callbacks,
                    available_functions=available_functions,
                    from_task=from_task,
                    from_agent=from_agent,
                    response_model=response_model,
                )
            except Exception as fallback_error:
                logger.error(
                    "OpenRouter fallback (%s) also failed: %s",
                    self.fallback_model_name,
                    fallback_error,
                )
                # Surface the original error: it is the more meaningful
                # diagnosis for the primary provider the user configured.
                raise primary_error from fallback_error

    def _should_fallback(self, error: BaseException) -> bool:
        if self._fallback is None:
            return False
        if self._fallback_on_all_errors:
            return True
        return _is_transient_error(error)

    # ------------------------------------------------------------------
    # Transparent delegation for everything CrewAI may probe on the LLM.
    # ------------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        # Only called when normal attribute lookup fails, so pydantic fields
        # and methods defined on this class are unaffected.
        primary = object.__getattribute__(self, "_primary")
        try:
            return getattr(primary, name)
        except AttributeError:
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {name!r}"
            ) from None

    def supports_function_calling(self) -> bool:
        try:
            return bool(self._primary.supports_function_calling())
        except Exception:
            return False

    def supports_stop_words(self) -> bool:
        try:
            return bool(self._primary.supports_stop_words())
        except Exception:
            return False

    def get_context_window_size(self) -> int:
        try:
            return int(self._primary.get_context_window_size())
        except Exception:
            return 4096

    def call_llm(self, *args: Any, **kwargs: Any) -> Any:
        """Compatibility alias used by some CrewAI internals."""
        return self.call(*args, **kwargs)


_FALLBACK_STATUS_PRINTED = False


def _build_openrouter_fallback() -> LLM | None:
    """Build the OpenRouter fallback LLM when it is configured and enabled."""
    global _FALLBACK_STATUS_PRINTED

    if not bool(getattr(settings, "ENABLE_OPENROUTER_FALLBACK", True)):
        return None

    api_key = _read_setting("OPENROUTER_API_KEY", "OPENROUTER_API_KEY")
    if not api_key:
        if not _FALLBACK_STATUS_PRINTED:
            print(
                "[llm] OpenRouter fallback disabled: OPENROUTER_API_KEY is not set."
            )
            _FALLBACK_STATUS_PRINTED = True
        return None

    model = _read_setting(
        "OPENROUTER_FALLBACK_MODEL", "OPENROUTER_FALLBACK_MODEL"
    ) or "openrouter/google/gemini-2.0-flash-001"

    # Accept bare OpenRouter slugs (e.g. "nvidia/nemotron-3.5-lightning:free")
    # and normalize them to LiteLLM/CrewAI's "openrouter/<model>" routing
    # format. Without this prefix the model would be routed to its vendor's
    # own API (e.g. nvidia/) instead of OpenRouter.
    if not model.lower().startswith("openrouter/"):
        model = f"openrouter/{model}"

    if not _FALLBACK_STATUS_PRINTED:
        print(f"[llm] OpenRouter fallback active: {model}")
        _FALLBACK_STATUS_PRINTED = True

    return LLM(
        model=model,
        api_key=api_key,
        max_tokens=16384,
        temperature=0.4,
    )


def get_llm(
    api_key: str,
    model: str,
    temperature: float = 0.4,
    enable_fallback: bool = True,
) -> LLM:
    """Create an LLM instance with a specific API key, model, and optional
    OpenRouter fallback for transient provider failures."""
    safe_api_key = _require_value(api_key, "API key")
    safe_model = _require_value(model, "model")

    primary = LLM(
        model=safe_model,
        api_key=safe_api_key,
        max_tokens=16384,
        temperature=temperature,
    )

    if not enable_fallback:
        return primary

    fallback = _build_openrouter_fallback()
    if fallback is None:
        return primary

    return FallbackLLM(
        primary=primary,
        fallback=fallback,
        fallback_on_all_errors=bool(
            getattr(settings, "OPENROUTER_FALLBACK_ON_ALL_ERRORS", True)
        ),
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