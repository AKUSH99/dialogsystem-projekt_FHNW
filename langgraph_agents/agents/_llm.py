"""
_llm.py — Shared OpenRouter LLM client for all Buy-Bot agents.

Uses the same model-fallback pattern as test-chat.py.
"""

from __future__ import annotations

import os
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

_CANDIDATE_MODELS = [
    "google/gemma-3-27b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "deepseek/deepseek-r1:free",
]


def _build_clients(temperature: float = 0.7, max_tokens: int = 500) -> List[ChatOpenAI]:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    return [
        ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_tokens=max_tokens,
        )
        for model in _CANDIDATE_MODELS
    ]


def call_llm(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.7,
    max_tokens: int = 500,
) -> str:
    """
    Call the OpenRouter LLM with a system prompt and user message.
    Falls back through candidate models on rate-limit or unavailability.
    Raises RuntimeError if all models fail.
    """
    clients = _build_clients(temperature=temperature, max_tokens=max_tokens)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    last_error: Exception | None = None
    for client in clients:
        try:
            response = client.invoke(messages)
            return response.content
        except Exception as e:
            error_text = str(e).lower()
            if any(
                kw in error_text
                for kw in ["429", "rate-limit", "rate limit", "404", "no endpoints found"]
            ):
                last_error = e
                continue
            raise

    raise RuntimeError(f"All LLM models failed. Last error: {last_error}")
