"""
router.py — Classifies the incoming question so the graph can pick the right expert node.

Returns one of: "product", "comparison", "guarantee", "advisor"
"""

from __future__ import annotations

import os
from typing import Dict, Optional

from langgraph_agents.agents._llm import call_llm

ROUTER_SYSTEM_PROMPT = """You are a routing assistant for Buy-Bot, a laptop purchasing advisor.
Your only job is to classify the user's question into ONE of these categories:

- product: Questions about specific laptop features, recommendations, specs explained in simple terms
- comparison: Questions comparing two or more laptops or asking which one is better
- guarantee: Questions about warranty, return policy, shipping, delivery, refunds
- advisor: General advice about what to look for in a laptop, lifestyle tips, non-specific questions

Reply with ONLY the category word. No explanation, no punctuation — just the single word.
"""


def route_question(
    user_message: str,
    context: Optional[Dict[str, Optional[str]]] = None,
) -> str:
    """Classify the user's question and return a routing key."""
    context_text = ""
    if context:
        parts = [f"{k}: {v}" for k, v in context.items() if v]
        if parts:
            context_text = "\nUser context: " + ", ".join(parts)

    prompt = f"{user_message}{context_text}"

    try:
        answer = call_llm(
            system_prompt=ROUTER_SYSTEM_PROMPT,
            user_message=prompt,
            max_tokens=10,
            temperature=0.0,
        ).strip().lower()
    except Exception:
        return "advisor"

    valid = {"product", "comparison", "guarantee", "advisor"}
    for cat in valid:
        if cat in answer:
            return cat

    # Keyword heuristic fallback
    msg_lower = user_message.lower()
    if any(kw in msg_lower for kw in ["compare", "vs", "difference", "better", "versus", "which one"]):
        return "comparison"
    if any(kw in msg_lower for kw in ["warranty", "guarantee", "return", "refund", "ship", "delivery"]):
        return "guarantee"
    if any(kw in msg_lower for kw in ["spec", "battery", "screen", "storage", "processor", "recommend", "suggest"]):
        return "product"

    return "advisor"
