"""
rag_agent.py — Answers policy questions (guarantee, return, shipping) using
a Markdown knowledge base. This is a placeholder for a full PDF-based RAG pipeline.

Current implementation: loads policies.md and passes it as context to the LLM.
Future: replace with a proper vector store + retrieval chain.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from langgraph_agents.agents._llm import call_llm

POLICIES_PATH = Path(__file__).resolve().parents[3] / "data" / "policies.md"

RAG_SYSTEM_PROMPT = """You are Buy-Bot, a friendly laptop store assistant answering customer questions
about store policies, warranties, returns, and shipping. 📦

Rules:
- Be warm, reassuring, and clear.
- If the answer is in the provided policy document, use it directly.
- If you don't find the answer, say so honestly and suggest the customer contact support.
- Keep answers concise: 2-4 sentences.
- Do NOT invent policy details you are not sure about.
"""


def _load_policies() -> str:
    if not POLICIES_PATH.exists():
        return ""
    with open(POLICIES_PATH, encoding="utf-8") as f:
        return f.read()


def answer_policy_question(
    user_message: str,
    context: Optional[Dict[str, Optional[str]]] = None,
) -> str:
    """Answer a policy question using the policies knowledge base."""
    policies_text = _load_policies()

    policy_section = ""
    if policies_text:
        policy_section = f"\n\n--- STORE POLICIES ---\n{policies_text}\n--- END POLICIES ---"

    full_message = f"{user_message}{policy_section}"

    try:
        return call_llm(
            system_prompt=RAG_SYSTEM_PROMPT,
            user_message=full_message,
            temperature=0.3,
            max_tokens=300,
        )
    except Exception:
        return (
            "Great question about our policies! 🛡️ "
            "Our store offers a standard warranty and easy returns within 30 days. "
            "For specific details, I'd recommend reaching out to our support team — "
            "they'll be happy to help you out! 😊"
        )
