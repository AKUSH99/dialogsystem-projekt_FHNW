# agents/intake_agent.py
"""
IntakeAgent — Stage 1 of the Buy-Bot pipeline.

Replaces Rasa NLU. Uses an LLM to:
  1. Have a natural conversation with the user
  2. Extract the 4 required slots: budget, preferred_os, use_case, mobility
  3. Signal when all slots are filled so the graph can move to the router

Why manual JSON parsing instead of with_structured_output()?
  with_structured_output() relies on tool calling, which many free OpenRouter
  models do not support. Instead, we ask the LLM to respond in JSON via the
  system prompt, then parse it ourselves. This works with any model.
"""

import json
import os
import re

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError
from typing import Literal

from agents.prompts import BUYBOT_SYSTEM_PROMPT, INTAKE_ROLE
from agents.state import BuyBotState, create_initial_state


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

class IntakeResponse(BaseModel):
    """
    The expected shape of every LLM response during intake.
    Parsed from the JSON the LLM returns.

    message      → what the bot says to the user (always present)
    slot fields  → values detected in the latest user message.
                   None if the slot was not mentioned this turn.
    """
    message: str
    language: Literal["english", "german"] | None = None
    budget: float | None = None
    preferred_os: Literal["windows", "macos", "no_preference"] | None = None
    use_case: Literal["gaming", "university", "professional", "office"] | None = None
    mobility: Literal["high", "medium", "low"] | None = None


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class IntakeAgent:
    """
    Collects the 4 required slots through natural conversation.

    Usage as a LangGraph node:
        agent = IntakeAgent(llm)
        graph.add_node("intake", agent.run)

    The graph calls agent.run(state) on every user turn until
    IntakeAgent.is_complete(state) returns True.
    """

    def __init__(self, llm):
        """
        llm — a ChatOpenAI (or compatible) client pointed at OpenRouter.
        No wrapper needed — we parse the raw text response ourselves.
        """
        self.llm = llm

    def run(self, state: BuyBotState) -> dict:
        """
        One conversation turn of the intake stage.

        Reads the current state, calls the LLM, parses the JSON response,
        extracts any new slot values, and returns a partial state update dict.
        """
        # Build the layered system prompt (persona + role + slot status + JSON format)
        system_message = SystemMessage(content=self._build_system_prompt(state))

        # If this is the very first turn, seed the conversation so the LLM
        # knows to generate an opening greeting (no user message exists yet).
        if not state.messages:
            seed = HumanMessage(content="[start]")
            messages = [system_message, seed]
        else:
            messages = [system_message] + state.messages

        # Call the LLM — we expect a JSON response back
        raw = self.llm.invoke(messages)

        # Parse the raw text into an IntakeResponse object
        response = self._parse_response(raw.content)

        # Start building the state update with the bot's reply
        update = {
            "messages": [AIMessage(content=response.message)],
            "current_stage": "intake",
        }

        # Merge newly extracted slots into state.
        # Only write a slot if the LLM detected a new value AND it was not already set.
        # This prevents later messages from overwriting already confirmed slots.
        if response.language is not None and state.language is None:
            update["language"] = response.language
        if response.budget is not None and state.budget is None:
            update["budget"] = response.budget
        if response.preferred_os is not None and state.preferred_os is None:
            update["preferred_os"] = response.preferred_os
        if response.use_case is not None and state.use_case is None:
            update["use_case"] = response.use_case
        if response.mobility is not None and state.mobility is None:
            update["mobility"] = response.mobility

        return update

    @staticmethod
    def is_complete(state: BuyBotState) -> bool:
        """
        Returns True when all 5 slots are filled (including language).

        The LangGraph conditional edge calls this after every intake turn
        to decide: stay in intake, or hand off to the router.
        """
        return (
            state.language is not None
            and state.budget is not None
            and state.preferred_os is not None
            and state.use_case is not None
            and state.mobility is not None
        )

    def _parse_response(self, text: str) -> IntakeResponse:
        """
        Extracts the JSON block from the LLM's raw text response and
        parses it into an IntakeResponse object.

        If parsing fails for any reason, falls back to treating the
        entire text as the bot message with no slot updates.
        This prevents the agent from crashing on a malformed response.
        """
        # Find the first {...} block in the response (ignore any surrounding text)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return IntakeResponse(**data)
            except (json.JSONDecodeError, ValidationError):
                # JSON found but couldn't be parsed — fall through to fallback
                pass

        # Fallback: return the raw text as the message, no slots extracted
        return IntakeResponse(message=text.strip())

    def _build_system_prompt(self, state: BuyBotState) -> str:
        """
        Combines four layers into one system message:
          1. Global Buy-Bot persona     (from prompts.py)
          2. Intake role description    (from prompts.py)
          3. Dynamic slot status        (which are known / still missing)
          4. JSON output format         (tells the LLM exactly what to return)

        Showing current slot status prevents the LLM from re-asking for
        information the user already provided.
        """
        known = []
        missing = []

        if state.language is not None:
            known.append(f"language: {state.language}")
        else:
            missing.append('language — ask first: "English or German?" / "Englisch oder Deutsch?"')

        if state.budget is not None:
            known.append(f"budget: CHF {state.budget}")
        else:
            missing.append("budget — ask for a CHF amount (number only)")

        if state.preferred_os is not None:
            known.append(f"preferred_os: {state.preferred_os}")
        else:
            missing.append('preferred_os — "windows" / "macos" / "no_preference"')

        if state.use_case is not None:
            known.append(f"use_case: {state.use_case}")
        else:
            missing.append('use_case — "gaming" / "university" / "professional" / "office"')

        if state.mobility is not None:
            known.append(f"mobility: {state.mobility}")
        else:
            missing.append('mobility — "high" / "medium" / "low"')

        # Format the slot status block
        status_parts = []
        if known:
            status_parts.append(
                "Already confirmed:\n" + "\n".join(f"  ✓ {k}" for k in known)
            )
        if missing:
            status_parts.append(
                "Still needed:\n" + "\n".join(f"  ? {m}" for m in missing)
            )

        status = "\n\n".join(status_parts)

        # Tell the LLM exactly what format to respond in.
        # Only set a slot field if the user clearly stated that value this turn.
        json_format = """\
Respond ONLY with a JSON object — no markdown, no extra text before or after:
{
  "message": "your conversational reply to the user",
  "language": null or "english" / "german",
  "budget": null or a positive number (e.g. 900.0),
  "preferred_os": null or "windows" / "macos" / "no_preference",
  "use_case": null or "gaming" / "university" / "professional" / "office",
  "mobility": null or "high" / "medium" / "low"
}
Only set a slot field if the user clearly stated that value in their latest message.
Leave it as null if it was not mentioned this turn."""

        return f"{BUYBOT_SYSTEM_PROMPT}\n\n{INTAKE_ROLE}\n\n{status}\n\n{json_format}"


# ---------------------------------------------------------------------------
# Quick CLI test  (run with: python -m agents.intake_agent)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    load_dotenv()

    # Enable LangSmith tracing so every run is visible in the dashboard
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = "buy-bot"

    # Set up the LLM — using a free OpenRouter model
    llm = ChatOpenAI(
        model="openai/gpt-oss-120b:free",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=500,
    )

    agent = IntakeAgent(llm)
    state = create_initial_state()

    print("=" * 55)
    print("Buy-Bot — Intake Agent Test")
    print("Type 'quit' to exit")
    print("=" * 55)

    # First turn: agent generates the opening greeting (no user input yet)
    result = agent.run(state)
    for key, value in result.items():
        if key == "messages":
            print(f"\nBuy-Bot: {value[-1].content}\n")
        else:
            setattr(state, key, value)

    # Conversation loop: keep going until all 4 slots are filled
    while not IntakeAgent.is_complete(state):
        user_input = input("You: ").strip()

        if user_input.lower() in ("quit", "exit"):
            print("Exiting.")
            break

        if not user_input:
            continue

        # Add the user's message to conversation history
        state.messages.append(HumanMessage(content=user_input))

        # Run one intake turn and apply the state update
        result = agent.run(state)
        for key, value in result.items():
            if key == "messages":
                state.messages.extend(value)
                print(f"\nBuy-Bot: {value[-1].content}\n")
            else:
                setattr(state, key, value)

    # Show the collected slots once intake is complete
    if IntakeAgent.is_complete(state):
        print("\n--- Intake complete ---")
        print(f"  language:     {state.language}")
        print(f"  budget:       CHF {state.budget}")
        print(f"  preferred_os: {state.preferred_os}")
        print(f"  use_case:     {state.use_case}")
        print(f"  mobility:     {state.mobility}")
        print("\nReady to route to expert agent.")
