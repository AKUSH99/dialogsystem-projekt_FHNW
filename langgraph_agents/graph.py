"""
graph.py — Main LangGraph graph for Buy-Bot's expert team.

The graph routes incoming questions to specialised agent nodes:
  router → product_expert | comparator | rag_agent | advisor

Each node calls the OpenRouter LLM with a focused system prompt and returns
a friendly, jargon-free response in the Buy-Bot persona.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

load_dotenv()

# ---------------------------------------------------------------------------
# State schema
# ---------------------------------------------------------------------------

class BotState(TypedDict):
    user_message: str
    context: Dict[str, Optional[str]]   # Rasa slot values
    agent_type: str                      # filled by router
    response: str                        # final answer


# ---------------------------------------------------------------------------
# Node implementations (import from agents sub-package)
# ---------------------------------------------------------------------------

from langgraph_agents.agents.router import route_question
from langgraph_agents.agents.product_expert import answer_product_question
from langgraph_agents.agents.comparator import compare_laptops
from langgraph_agents.agents.rag_agent import answer_policy_question
from langgraph_agents.agents.advisor import give_general_advice


def router_node(state: BotState) -> BotState:
    """Classify the incoming question and set agent_type."""
    agent_type = route_question(state["user_message"], state["context"])
    return {**state, "agent_type": agent_type}


def product_expert_node(state: BotState) -> BotState:
    response = answer_product_question(state["user_message"], state["context"])
    return {**state, "response": response}


def comparator_node(state: BotState) -> BotState:
    response = compare_laptops(state["user_message"], state["context"])
    return {**state, "response": response}


def rag_agent_node(state: BotState) -> BotState:
    response = answer_policy_question(state["user_message"], state["context"])
    return {**state, "response": response}


def advisor_node(state: BotState) -> BotState:
    response = give_general_advice(state["user_message"], state["context"])
    return {**state, "response": response}


# ---------------------------------------------------------------------------
# Routing logic (conditional edge)
# ---------------------------------------------------------------------------

def route_edge(state: BotState) -> str:
    """Map agent_type string to the next node name."""
    mapping = {
        "product": "product_expert",
        "comparison": "comparator",
        "guarantee": "rag_agent",
        "advisor": "advisor",
    }
    return mapping.get(state.get("agent_type", "advisor"), "advisor")


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def _build_graph() -> Any:
    builder = StateGraph(BotState)

    builder.add_node("router", router_node)
    builder.add_node("product_expert", product_expert_node)
    builder.add_node("comparator", comparator_node)
    builder.add_node("rag_agent", rag_agent_node)
    builder.add_node("advisor", advisor_node)

    builder.set_entry_point("router")

    builder.add_conditional_edges(
        "router",
        route_edge,
        {
            "product_expert": "product_expert",
            "comparator": "comparator",
            "rag_agent": "rag_agent",
            "advisor": "advisor",
        },
    )

    builder.add_edge("product_expert", END)
    builder.add_edge("comparator", END)
    builder.add_edge("rag_agent", END)
    builder.add_edge("advisor", END)

    return builder.compile()


_graph = None


def _get_graph() -> Any:
    global _graph
    if _graph is None:
        _graph = _build_graph()
    return _graph


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_buybot_graph(
    user_message: str,
    context: Optional[Dict[str, Optional[str]]] = None,
) -> str:
    """
    Run the Buy-Bot LangGraph pipeline.

    Args:
        user_message: The free-form question from the user.
        context: Optional dict of Rasa slot values (budget, use_case, …).

    Returns:
        A friendly, jargon-free answer string.
    """
    if context is None:
        context = {}

    initial_state: BotState = {
        "user_message": user_message,
        "context": context,
        "agent_type": "",
        "response": "",
    }

    graph = _get_graph()
    final_state = graph.invoke(initial_state)
    return final_state.get("response", "I'm not sure about that one — could you rephrase? 😊")
