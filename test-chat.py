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

from langchain_core.messages import HumanMessage, AIMessage
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

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY is missing. Add it to .env first.\n")
        return

    # Try models in order and fall back when a provider is rate-limited.
    candidate_models = [
        "google/gemma-3-27b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "deepseek/deepseek-r1:free",
    ]

    llm_clients = [
        ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=500,
        )
        for model_name in candidate_models
    ]

    print("✅ OpenRouter API initialized successfully")
    print(f"ℹ️  Model fallback order: {', '.join(candidate_models)}\n")

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

        # Call LLM with fallback across candidate models
        bot_response = None
        last_error = None

        for llm in llm_clients:
            try:
                response = llm.invoke(messages)
                bot_response = response.content
                print(f"\nℹ️  Responded with model: {llm.model_name}")
                break
            except Exception as e:
                error_text = str(e).lower()
                last_error = e

                if (
                    "429" in error_text
                    or "rate-limit" in error_text
                    or "rate limit" in error_text
                    or "404" in error_text
                    or "no endpoints found" in error_text
                ):
                    print(f"\n⚠️  Model unavailable or rate-limited: {llm.model_name}. Trying next model...")
                    continue

                # Non-rate-limit error: stop trying additional models.
                break

        if bot_response is not None:
            # Add bot response to history
            messages.append(AIMessage(content=bot_response))
            print(f"Bot: {bot_response}\n")
            continue

        print(f"\n❌ Error calling LLM: {last_error}\n")
        # Remove the user message if all model calls failed
        messages.pop()


if __name__ == "__main__":
    main()