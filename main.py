# main.py
"""
Buy-Bot — full pipeline CLI runner.

Runs the complete LangGraph pipeline in the terminal so you can test the
end-to-end conversation without a frontend.

Usage:
    source .venv/bin/activate
    python main.py

What this tests:
  - Language selection (first question)
  - Intake slot collection
  - Routing to the correct expert agent
  - Expert follow-up questions
  - Search agent (SQL + LLM ranking)
  - Suggestion agent (final recommendation)
  - QA interception (try asking "what does OLED mean?" mid-conversation)
  - Off-topic rejection (try asking "what's the weather?")
"""

import os

from langchain_core.messages import HumanMessage

from agents.graph import build_graph
from agents.llm_builder import build_llms
from agents.state import create_initial_state


def main():
    # Enable LangSmith tracing — every run appears in the dashboard
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = "buy-bot"

    print("=" * 55)
    print("Buy-Bot — Laptop Advisor (full pipeline test)")
    print("Type 'quit' at any time to exit")
    print("Try asking 'what does OLED mean?' at any point to")
    print("test QA interception, or 'what's the weather?' for")
    print("off-topic rejection.")
    print("=" * 55)

    llm_fast, llm_strong = build_llms()

    # Build the full LangGraph pipeline
    graph = build_graph(llm_fast, llm_strong)

    # Create a new session — session_id is the LangGraph thread ID
    # All turns in this conversation share the same thread_id
    state = create_initial_state()
    config = {"configurable": {"thread_id": state.session_id}}

    # --- First turn: no user message yet ---
    # Dispatch sees empty messages and routes straight to intake,
    # which generates the opening language-choice greeting.
    result = graph.invoke({"session_id": state.session_id}, config)
    print(f"\nBuy-Bot: {result['messages'][-1].content}\n")

    # --- Conversation loop ---
    # Each iteration: read user input → invoke graph → print bot reply.
    # The graph restores full state from the checkpointer on each invoke,
    # so we only need to pass the new user message.
    while result.get("current_stage") != "done":
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Bye!")
            break

        # Pass only the new message — checkpointer restores the rest
        result = graph.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config,
        )

        print(f"\nBuy-Bot: {result['messages'][-1].content}\n")

    if result.get("current_stage") == "done":
        print("=" * 55)
        print("Pipeline complete.")
        print(f"  Primary:     {result.get('laptop_primary', {}).get('name', 'n/a')}")
        print(f"  Alternative: {result.get('laptop_alternative', {}).get('name', 'n/a')}")


if __name__ == "__main__":
    main()
