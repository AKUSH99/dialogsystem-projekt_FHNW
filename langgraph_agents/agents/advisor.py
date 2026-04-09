"""
advisor.py — General advice agent. Explains laptop buying concepts in simple,
non-technical language. Focuses on lifestyle benefits over technical specs.
"""

from __future__ import annotations

from typing import Dict, Optional

from langgraph_agents.agents._llm import call_llm

ADVISOR_SYSTEM_PROMPT = """You are Buy-Bot, a friendly and enthusiastic laptop shopping advisor. 🎯
Your mission: make laptop buying feel easy and exciting — not scary or overwhelming.

Rules:
- Use simple, everyday language. NO technical jargon.
- Translate everything into lifestyle terms: "great for Netflix evenings" not "1080p IPS display".
- Be encouraging and positive. Shopping should feel like an investment in happiness!
- Keep answers short: 2-4 sentences.
- If you don't know the answer, say so warmly and offer to help in another way.
- Always guide the conversation back to helping them find their perfect laptop.
"""


def give_general_advice(
    user_message: str,
    context: Optional[Dict[str, Optional[str]]] = None,
) -> str:
    """Give general laptop-buying advice in simple language."""
    context_text = ""
    if context:
        parts = [f"{k}: {v}" for k, v in context.items() if v]
        if parts:
            context_text = "\nUser context: " + ", ".join(parts)

    full_message = f"{user_message}{context_text}"

    try:
        return call_llm(
            system_prompt=ADVISOR_SYSTEM_PROMPT,
            user_message=full_message,
            temperature=0.8,
            max_tokens=300,
        )
    except Exception:
        return (
            "That's a wonderful question! 🌟 "
            "The most important thing when choosing a laptop is to match it to your lifestyle — "
            "not to get lost in numbers and specs. Tell me what you'll use it for, "
            "and I'll point you to the perfect match! 😊"
        )
