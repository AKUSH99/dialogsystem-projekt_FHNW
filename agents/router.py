# agents/router.py
"""
Router — decides which expert agent handles this conversation.

No LLM call needed here. The intake agent already resolved any ambiguity
(e.g. "gaming and uni" → "gaming"). The router simply reads use_case from
state and returns the name of the next node for LangGraph to route to.

Usage in graph.py:
    router = Router()
    graph.add_conditional_edges("intake", router.route, {
        "gaming":       "gaming_agent",
        "university":   "uni_agent",
        "professional": "professional_agent",
        "office":       "office_agent",
    })
"""

from agents.state import BuyBotState


class Router:
    """
    Routes the conversation to the correct expert agent after intake.

    Acts as a LangGraph conditional edge: returns a string that LangGraph
    uses to pick the next node in the graph.
    """

    # Maps every valid use_case value to the node name in the graph.
    # Defined here so it's easy to see and update in one place.
    ROUTES = {
        "gaming":       "gaming_agent",
        "university":   "uni_agent",
        "professional": "professional_agent",
        "office":       "office_agent",
    }

    def route(self, state: BuyBotState) -> str:
        """
        Reads use_case from state and returns the matching agent node name.

        Raises ValueError if use_case is somehow not set or not recognised.
        This should never happen if intake completed correctly — but failing
        loudly here is better than silently routing to the wrong agent.
        """
        use_case = state.use_case

        if use_case not in self.ROUTES:
            raise ValueError(
                f"Router received unexpected use_case: '{use_case}'. "
                f"Expected one of: {list(self.ROUTES.keys())}"
            )

        return self.ROUTES[use_case]
