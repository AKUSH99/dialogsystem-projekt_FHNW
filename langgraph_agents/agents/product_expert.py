"""
product_expert.py — Searches the laptop DB and answers product-specific questions
in lifestyle language (no technical jargon).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

from langgraph_agents.agents._llm import call_llm

DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "laptops.json"

PRODUCT_SYSTEM_PROMPT = """You are Buy-Bot, an enthusiastic and friendly laptop advisor. 🎉
Your personality: optimistic, sales-oriented, warm, and encouraging.

Rules:
- NEVER use technical jargon like RAM, CPU, GPU, GHz, DDR5, SSD, NVMe, etc.
- Translate specs into lifestyle benefits: "long battery" not "10-hour battery life", "fast" not "Intel i7".
- Keep responses short (2-4 sentences) and upbeat.
- If relevant laptop data is provided, use it. Otherwise, give general helpful advice.
- End with an encouraging statement or offer to help more.
"""


def _load_laptops() -> list:
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def answer_product_question(
    user_message: str,
    context: Optional[Dict[str, Optional[str]]] = None,
) -> str:
    """Answer a product-specific question using the laptop DB as context."""
    laptops = _load_laptops()

    # Build a compact product summary for the LLM
    product_summary = ""
    if laptops:
        lines = []
        for laptop in laptops[:8]:  # limit to avoid token overflow
            line = (
                f"- {laptop['name']} ({laptop['price_chf']} CHF): "
                f"{laptop['short_description']} "
                f"[good for: {', '.join(laptop.get('good_for', []))}]"
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
            system_prompt=PRODUCT_SYSTEM_PROMPT,
            user_message=full_message,
            temperature=0.7,
            max_tokens=300,
        )
    except Exception:
        return (
            "Great question! 💻 I'd love to give you more details. "
            "Based on your needs, I'd recommend looking at laptops optimised for everyday use — "
            "light, long-lasting battery, and perfect for study and streaming. Shall I find you some options?"
        )
