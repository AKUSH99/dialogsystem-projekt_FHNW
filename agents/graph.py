# agents/graph.py
"""
Buy-Bot LangGraph pipeline — wires all agents into a single compiled graph.

How it works:
  - Every user message triggers one graph invocation.
  - The graph starts at 'dispatch', which classifies the message and routes
    to the correct agent for the current pipeline stage.
  - After each agent runs, a conditional edge decides:
      → END:  bot replied, wait for the next user message
      → next node: the stage is complete, continue automatically
        (e.g. intake done → first expert question in the same turn;
               expert done → search + suggestion in the same turn)

Stage progression across turns:
  intake (multiple turns) → expert (multiple turns) → search → suggestion → done

QA interception:
  At any stage, if the user asks an off-script question, dispatch routes to
  qa_agent instead of the stage agent. current_stage is unchanged so the
  next turn picks up exactly where it left off.

State persistence:
  MemorySaver stores the full BuyBotState between turns so each invocation
  only needs to supply the new user message. Swap for SqliteSaver if you
  need persistence across Python restarts.
"""

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from agents.expert_agents import GamingAgent, OfficeAgent, ProfessionalAgent, UniAgent
from agents.intake_agent import IntakeAgent
from agents.qa_agent import QAAgent
from agents.router import Router
from agents.search_agent import SearchAgent
from agents.state import BuyBotState
from agents.suggestion_agent import SuggestionAgent


# Maps state.use_case → graph node name.
# Defined here (not in Router) because this is graph wiring, not routing logic.
_EXPERT_NODE = {
    "gaming":       "gaming_agent",
    "university":   "uni_agent",
    "professional": "professional_agent",
    "office":       "office_agent",
}


def build_graph(llm_fast, llm_strong, db_path: str = "data/laptops.db"):
    """
    Builds and compiles the full Buy-Bot pipeline as a LangGraph StateGraph.

    Args:
        llm_fast:   Small/fast model — intake, expert agents, classifier.
        llm_strong: Large/quality model — QA answers, search ranking, suggestion.
        db_path:    Path to the SQLite product database.

    Returns:
        A compiled LangGraph graph ready to invoke.

    Usage:
        graph  = build_graph(llm_fast, llm_strong)
        config = {"configurable": {"thread_id": session_id}}

        # First turn — no user message yet, triggers opening greeting
        result = graph.invoke({"session_id": session_id}, config)

        # Subsequent turns — supply only the new user message
        result = graph.invoke({"messages": [HumanMessage(content=user_input)]}, config)

        # The last bot message is always the final entry in result["messages"]
        reply = result["messages"][-1].content
    """

    # ------------------------------------------------------------------
    # Instantiate all agents
    # ------------------------------------------------------------------

    # Fast model: structured slot extraction and follow-up questions
    intake       = IntakeAgent(llm_fast)
    router       = Router()                               # no LLM — pure logic
    uni          = UniAgent(llm_fast)
    gaming       = GamingAgent(llm_fast)
    professional = ProfessionalAgent(llm_fast)
    office       = OfficeAgent(llm_fast)

    # Strong model: nuanced answers and the final recommendation
    search      = SearchAgent(llm_strong, db_path=db_path)
    suggestion  = SuggestionAgent(llm_strong)
    qa          = QAAgent(llm_strong)

    # ------------------------------------------------------------------
    # Graph definition
    # ------------------------------------------------------------------

    g = StateGraph(BuyBotState)

    # Register every agent as a node.
    # Each node function receives the full BuyBotState and returns a partial
    # update dict — LangGraph merges the update into the existing state.
    g.add_node("intake",             intake.run)
    g.add_node("uni_agent",          uni.run)
    g.add_node("gaming_agent",       gaming.run)
    g.add_node("professional_agent", professional.run)
    g.add_node("office_agent",       office.run)
    g.add_node("search_agent",       search.run)
    g.add_node("suggestion_agent",   suggestion.run)
    g.add_node("qa_agent",           qa.run)
    g.add_node("off_topic",          qa.handle_off_topic)

    # ------------------------------------------------------------------
    # Entry point — dispatch
    # ------------------------------------------------------------------
    # Every invocation starts here. The dispatch function classifies the
    # user's latest message and routes to the right node.

    def dispatch(state: BuyBotState) -> str:
        """
        Routes each incoming turn to the correct agent.

        Three cases:
          1. No messages yet → first ever turn → go straight to intake
             (intake generates the opening language-choice greeting)
          2. off_topic or qa → intercept with the QA agent
          3. on_script → send to the agent for the current pipeline stage
        """
        # First ever turn — skip classification, go straight to intake
        if not state.messages:
            return "intake"

        # Classify the user's latest message — fast model is enough here
        route = QAAgent.classify_message(state, llm_fast)

        if route == "off_topic":
            return "off_topic"

        if route == "qa":
            return "qa_agent"

        # on_script — route to the agent for the current pipeline stage
        if state.current_stage == "intake":
            return "intake"

        if state.current_stage == "expert":
            # use_case was set during intake and tells us which expert is active
            return _EXPERT_NODE.get(state.use_case, "intake")

        # "search" and "suggestion" stages are triggered automatically within
        # a turn (see after_expert below) and never arrive at dispatch directly.
        # Routing to intake here is a safe fallback that should not occur.
        return "intake"

    g.add_conditional_edges(START, dispatch, {
        "intake":             "intake",
        "uni_agent":          "uni_agent",
        "gaming_agent":       "gaming_agent",
        "professional_agent": "professional_agent",
        "office_agent":       "office_agent",
        "qa_agent":           "qa_agent",
        "off_topic":          "off_topic",
    })

    # ------------------------------------------------------------------
    # After intake
    # ------------------------------------------------------------------
    # If all 5 slots are filled: router picks the expert node and the graph
    # continues immediately (first expert question in the same turn).
    # Otherwise: END — bot asked a question, wait for the user's reply.

    def after_intake(state: BuyBotState) -> str:
        if IntakeAgent.is_complete(state):
            return router.route(state)  # e.g. "uni_agent"
        return END

    g.add_conditional_edges("intake", after_intake, {
        "uni_agent":          "uni_agent",
        "gaming_agent":       "gaming_agent",
        "professional_agent": "professional_agent",
        "office_agent":       "office_agent",
        END:                  END,
    })

    # ------------------------------------------------------------------
    # After each expert agent
    # ------------------------------------------------------------------
    # The expert agent sets current_stage = "search" when it has enough info.
    # On that turn, the graph continues automatically: search → suggestion.
    # Otherwise: END — expert asked a follow-up, wait for the user's reply.

    def after_expert(state: BuyBotState) -> str:
        if state.current_stage == "search":
            return "search_agent"
        return END

    for expert_node in ["uni_agent", "gaming_agent", "professional_agent", "office_agent"]:
        g.add_conditional_edges(expert_node, after_expert, {
            "search_agent": "search_agent",
            END:            END,
        })

    # ------------------------------------------------------------------
    # Search → suggestion (always sequential, no user input between them)
    # ------------------------------------------------------------------

    g.add_edge("search_agent", "suggestion_agent")

    # ------------------------------------------------------------------
    # Terminal edges — end the current turn
    # ------------------------------------------------------------------
    # After the suggestion, QA answer, or off-topic refusal, the bot has
    # replied. END suspends the graph until the next user message arrives.

    g.add_edge("suggestion_agent", END)
    g.add_edge("qa_agent",         END)
    g.add_edge("off_topic",        END)

    # ------------------------------------------------------------------
    # Compile with checkpointer
    # ------------------------------------------------------------------
    # MemorySaver keeps state in memory for the lifetime of the process.
    # For a production deployment, replace with SqliteSaver:
    #   from langgraph.checkpoint.sqlite import SqliteSaver
    #   memory = SqliteSaver.from_conn_string("checkpoints.db")

    memory = MemorySaver()
    return g.compile(checkpointer=memory)
