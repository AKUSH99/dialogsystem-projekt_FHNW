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
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

# Enable LangSmith tracing
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "buy-bot"


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


def main():
    """Test the API connections."""

    print("=" * 60)
    print("Buy-Bot - Testing API Connections")
    print("=" * 60)
    print("Type 'quit' to exit\n")

    # Initialize OpenRouter LLM
    try:
        llm = ChatOpenAI(
            model="google/gemma-3-27b-it:free",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=500,
        )
        print("✅ OpenRouter API initialized successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize OpenRouter API: {e}\n")
        return

    # Initialize message history
    messages = []

    # Test conversation loop
    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit"]:
            print("Bot: Thanks for testing! Goodbye! 👋")
            break

        if not user_input:
            continue

        # Test safeguard
        is_safe, reason = safeguard_input(user_input)
        if not is_safe:
            print(f"\n❌ Bot: I can't respond to that. {reason}\n")
            continue

        # Add user message to history
        messages.append(HumanMessage(content=user_input))

        # Call LLM with message history
        try:
            response = llm.invoke(messages)
            bot_response = response.content

            # Add bot response to history
            messages.append(AIMessage(content=bot_response))

            print(f"\nBot: {bot_response}\n")

        except Exception as e:
            print(f"\n❌ Error calling LLM: {e}\n")
            # Remove the user message if LLM call failed
            messages.pop()


if __name__ == "__main__":
    main()
