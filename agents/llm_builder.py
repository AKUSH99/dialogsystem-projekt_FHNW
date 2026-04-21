# agents/llm_builder.py
"""
Builds the two LLM clients used throughout the Buy-Bot pipeline.

Imported by both main.py (CLI) and frontend/app.py (Streamlit) so model
setup is defined in exactly one place. To change a model, edit model_config.py.
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from model_config import (
    MODEL_FAST, MODEL_STRONG, MODEL_FALLBACK,
    MAX_TOKENS_FAST, MAX_TOKENS_STRONG, MAX_TOKENS_FALLBACK,
    TEMPERATURE_FAST, TEMPERATURE_STRONG, TEMPERATURE_FALLBACK,
)


class ModelWithFallback:
    """
    Wraps a primary LLM with an automatic fallback model.

    If the primary fails for any reason (rate limit, outage, timeout),
    the same call is transparently retried on the fallback.

    All agents only call .invoke() — this class is a drop-in replacement
    for any ChatOpenAI instance.
    """

    def __init__(self, primary: ChatOpenAI, fallback: ChatOpenAI):
        # Keep both so invoke() can try them in order
        self.primary = primary
        self.fallback = fallback

    def invoke(self, input, config=None, **kwargs):
        """Try the primary model; on any error, retry with the fallback."""
        try:
            return self.primary.invoke(input, config, **kwargs)
        except Exception as e:
            # Print so the error is visible in the terminal / Streamlit logs
            print(
                f"[fallback] {self.primary.model_name} failed "
                f"({type(e).__name__}: {e}), retrying with {self.fallback.model_name}"
            )
            return self.fallback.invoke(input, config, **kwargs)


def build_llms() -> tuple[ModelWithFallback, ModelWithFallback]:
    """
    Returns (llm_fast, llm_strong) — both wrapped with the fallback model.

    Calls load_dotenv() so callers don't need to remember to do it first.
    """
    load_dotenv()

    # Shared OpenRouter connection settings
    common = dict(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )

    # Fallback — tried automatically when fast or strong fail
    llm_fallback = ChatOpenAI(
        model=MODEL_FALLBACK,
        max_tokens=MAX_TOKENS_FALLBACK,
        temperature=TEMPERATURE_FALLBACK,
        **common,
    )

    llm_fast = ModelWithFallback(
        primary=ChatOpenAI(
            model=MODEL_FAST,
            max_tokens=MAX_TOKENS_FAST,
            temperature=TEMPERATURE_FAST,
            **common,
        ),
        fallback=llm_fallback,
    )

    llm_strong = ModelWithFallback(
        primary=ChatOpenAI(
            model=MODEL_STRONG,
            max_tokens=MAX_TOKENS_STRONG,
            temperature=TEMPERATURE_STRONG,
            **common,
        ),
        fallback=llm_fallback,
    )

    return llm_fast, llm_strong
