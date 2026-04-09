"""
comparator.py — Compares two laptops side by side in simple, lifestyle-focused language.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from langgraph_agents.agents._llm import call_llm

DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "laptops.json"

COMPARATOR_SYSTEM_PROMPT = """You are Buy-Bot, an enthusiastic laptop advisor comparing options for a customer. 🔍
Your personality: clear, friendly, and helpful — like a knowledgeable friend.

Rules:
- NEVER use technical specs directly (RAM, CPU, GHz, etc.) — translate to lifestyle benefits.
- Structure your comparison clearly (e.g. "Option A is better for… Option B is better for…").
- Keep it concise: 3-5 sentences max.
- End with a recommendation based on what you know about the user.
- Be encouraging and supportive — help them feel confident in their choice!
"""


def _load_laptops() -> list:
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def compare_laptops(
    user_message: str,
    context: Optional[Dict[str, Optional[str]]] = None,
) -> str:
    """Compare laptops mentioned in the user's message."""
    laptops = _load_laptops()

    product_summary = ""
    if laptops:
        lines = []
        for laptop in laptops[:8]:
            line = (
                f"- {laptop['name']} ({laptop['price_chf']} CHF): "
                f"{laptop['short_description']} "
                f"[good for: {', '.join(laptop.get('good_for', []))}; "
                f"weight: {laptop['weight_kg']}kg; battery: {laptop['battery_hours']}h]"
            )
            lines.append(line)
        product_summary = "\n\nAvailable laptops:\n" + "\n".join(lines)

    context_text = ""
    if context:
        parts = [f"{k}: {v}" for k, v in context.items() if v]
        if parts:
            context_text = "\nUser profile: " + ", ".join(parts)

    full_message = f"{user_message}{context_text}{product_summary}"

    try:
        return call_llm(
            system_prompt=COMPARATOR_SYSTEM_PROMPT,
            user_message=full_message,
            temperature=0.5,
            max_tokens=350,
        )
    except Exception:
        return (
            "Great question — comparing options is super smart! 🧠 "
            "Generally speaking, lighter laptops are perfect if you're always on the go, "
            "while heavier ones often come with more power for gaming or demanding tasks. "
            "Want me to walk you through the specific options I suggested? Just say the word! 😊"
        )
