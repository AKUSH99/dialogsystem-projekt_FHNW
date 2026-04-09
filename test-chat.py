"""
test-chat.py - Testing API Connections Only

This is a TEST FILE for verifying that OpenRouter API and LangSmith tracing work correctly.
It does NOT represent the actual Buy-Bot implementation for the project.

Use this to test:
- OpenRouter API connectivity
- LangSmith tracing setup
- LangGraph state management
- Basic safeguards

The actual Buy-Bot project implementation will be created separately.
"""

import os
from typing import Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# Enable LangSmith tracing
os.environ["LANGSMITH_TRACING"] = "true"

# Configure LangSmith project
os.environ["LANGSMITH_PROJECT"] = "buy-bot"

# System prompt for the Buy-Bot
SYSTEM_PROMPT = """You are Buy-Bot, a helpful and optimistic laptop sales advisor for an e-commerce platform.

Your personality:
- Optimistic, friendly, and sales-oriented
- Speak in simple, non-technical language
- Focus on lifestyle and use cases, not technical specs
- Professional but with light charm

Your goal:
1. Greet the customer warmly
2. Ask targeted questions to understand their needs (budget, use case, preferences)
3. Recommend 2-4 laptop options that match their requirements
4. Explain your recommendations clearly and motivate them to buy

Guidelines:
- Always speak in simple language - avoid technical jargon
- Consider budget, portability, performance needs, and personal preferences
- Be transparent about prices and trade-offs
- Ask clarifying questions when needed
- Keep responses concise and engaging

Example conversation flow:
1. Greet and ask about budget
2. Ask about primary use case (study, work, gaming, etc.)
3. Ask about portability needs and other preferences
4. Make recommendations with brief explanations
5. Offer alternatives if they want to explore further
"""


class State(TypedDict):
    """State for the Buy-Bot conversation."""
    messages: Annotated[list[BaseMessage], add_messages]


def safeguard_input(message: str) -> tuple[bool, str]:
    """
    Basic safeguard to filter inappropriate content.
    Returns (is_safe, reason)
    """
    unsafe_keywords = [
        "illegal", "hack", "crack", "malware", "virus",
        "abuse", "hate", "violence", "kill", "bomb"
    ]

    message_lower = message.lower()

    for keyword in unsafe_keywords:
        if keyword in message_lower:
            return False, f"Message contains unsafe content: {keyword}"

    # Check for excessively long messages (potential spam)
    if len(message) > 5000:
        return False, "Message too long"

    return True, ""


def chat_node(state: State) -> dict:
    """
    Main chat node that calls OpenRouter LLM with system prompt.
    Includes input safeguards.
    """
    messages = state["messages"]

    # Safeguard the latest user message
    if messages:
        last_message = messages[-1]
        if isinstance(last_message, HumanMessage):
            is_safe, reason = safeguard_input(last_message.content)
            if not is_safe:
                return {
                    "messages": [
                        AIMessage(content=f"I can't respond to that. {reason}")
                    ]
                }

    # Initialize OpenRouter LLM
    llm = ChatOpenAI(
        model="openrouter/meta-llama/llama-2-70b-chat",  # Or any OpenRouter model
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=500,
    )

    # Create messages with system prompt
    system_message = {"role": "system", "content": SYSTEM_PROMPT}

    # Call LLM with tracing (automatic via LangSmith)
    response = llm.invoke(messages)

    return {"messages": [response]}


def build_graph() -> StateGraph:
    """Build the LangGraph state machine for Buy-Bot."""

    graph = StateGraph(State)

    # Add chat node
    graph.add_node("chat", chat_node)

    # Define flow: START -> chat -> END
    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)

    return graph.compile()


def main():
    """Test the Buy-Bot."""

    # Build the graph
    app = build_graph()

    print("=" * 60)
    print("Buy-Bot Chatbot - LangGraph Implementation")
    print("=" * 60)
    print("Type 'quit' to exit\n")

    # Initialize state with empty messages
    state = {"messages": []}

    # Initial greeting
    greeting_response = app.invoke(
        {"messages": [HumanMessage(content="Hello")]}
    )

    print(f"Buy-Bot: {greeting_response['messages'][-1].content}\n")

    # Conversation loop
    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit"]:
            print("Buy-Bot: Thanks for chatting! Goodbye! 👋")
            break

        if not user_input:
            continue

        # Add user message to state
        state["messages"].append(HumanMessage(content=user_input))

        # Invoke the graph
        response = app.invoke(state)

        # Extract and display response
        bot_message = response["messages"][-1].content
        print(f"\nBuy-Bot: {bot_message}\n")

        # Update state with the bot's response
        state["messages"] = response["messages"]


if __name__ == "__main__":
    main()
