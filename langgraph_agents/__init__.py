"""
langgraph_agents — Buy-Bot LangGraph expert team.

Usage:
    from langgraph_agents import run_buybot_graph

    response = run_buybot_graph(
        user_message="What's the difference between these two laptops?",
        context={"budget": "800", "use_case": "university"},
    )
"""

from langgraph_agents.graph import run_buybot_graph

__all__ = ["run_buybot_graph"]
