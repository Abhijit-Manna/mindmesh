import crewai.llms.cache as _crewai_cache
from crewai import LLM
from src.config import settings

_crewai_cache.mark_cache_breakpoint = lambda msg: msg


def get_llm() -> LLM:
    """Create the primary LLM instance using OpenRouter configuration."""
    return LLM(
        model=f"openrouter/{settings.OPENROUTER_MODEL}",
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        max_tokens=2000,
    )


#def get_eval_llm() -> LLM:
    #"""Create the evaluation LLM instance using OpenRouter configuration."""
    #return LLM(
     #   model=f"openrouter/{settings.EVALUATION_MODEL}",
    #    api_key=settings.OPENROUTER_API_KEY,
   #     base_url="https://openrouter.ai/api/v1",
  #      max_tokens=1000,
 #   )