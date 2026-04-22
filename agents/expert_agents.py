# agents/expert_agents.py
"""
Expert Agents — Stage 3 of the Buy-Bot pipeline.

There are 4 expert agents (uni, gaming, professional, office). They all work
identically — the only difference is their role prompt and the questions they ask.

To avoid repeating the same code 4 times, all shared logic lives in
BaseExpertAgent. Each specific agent extends it and sets its own ROLE_PROMPT.

Flow:
  1. Expert agent asks domain-specific follow-up questions
  2. Each answer is merged into state.user_profile
  3. When the agent has enough info, it sets satisfied=True in its response
  4. The graph then routes to the search agent
"""

import json
import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, ValidationError

from agents.prompts import (
    BUYBOT_SYSTEM_PROMPT,
    UNI_AGENT_ROLE,
    GAMING_AGENT_ROLE,
    PROFESSIONAL_AGENT_ROLE,
    OFFICE_AGENT_ROLE,
)
from agents.state import BuyBotState


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

class ExpertResponse(BaseModel):
    """
    The shape of every LLM response during the expert agent stage.

    message             → what the bot says to the user
    satisfied           → True when the agent has enough info to recommend a laptop
    user_profile_update → new key-value pairs to merge into state.user_profile
    """
    message: str
    satisfied: bool = False
    user_profile_update: dict = {}


# ---------------------------------------------------------------------------
# Base class — shared logic for all 4 expert agents
# ---------------------------------------------------------------------------

class BaseExpertAgent:
    """
    Base class for all expert agents. Do not use this directly.
    Use UniAgent, GamingAgent, ProfessionalAgent, or OfficeAgent instead.

    Subclasses only need to set ROLE_PROMPT — everything else is handled here.
    """

    # Each subclass sets this to its own role prompt from prompts.py
    ROLE_PROMPT = ""

    def __init__(self, llm):
        """
        llm — a ChatOpenAI (or compatible) client pointed at OpenRouter.
        """
        self.llm = llm

    def run(self, state: BuyBotState) -> dict:
        """
        One conversation turn of the expert stage.

        Asks a follow-up question, collects the answer, and merges any new
        profile data into state.user_profile. When satisfied, signals the
        graph to move on to the search agent.
        """
        # Build the layered system prompt
        system_message = SystemMessage(content=self._build_system_prompt(state))
        messages = [system_message] + state.messages

        # Call the LLM and parse the response
        raw = self.llm.invoke(messages)
        response = self._parse_response(raw.content)

        # Merge the new profile data into the existing user_profile dict.
        # We read the full current profile and add the new keys on top.
        updated_profile = {**state.user_profile, **response.user_profile_update}

        # Build the state update
        update = {
            "messages": [AIMessage(content=response.message)],
            "user_profile": updated_profile,
            # Move to "search" when satisfied, stay on "expert" otherwise
            "current_stage": "search" if response.satisfied else "expert",
        }

        return update

    @staticmethod
    def is_complete(state: BuyBotState) -> bool:
        """
        Returns True when current_stage has been set to "search".
        The LangGraph conditional edge uses this to decide where to go next.
        """
        return state.current_stage == "search"

    def _parse_response(self, text: str) -> ExpertResponse:
        """
        Extracts the JSON object from the LLM's raw text and parses it
        into an ExpertResponse object.

        Uses raw_decode to walk the full text and collect every valid JSON
        object. The last one with a "message" key is used — reasoning models
        output their thinking first and the answer last, so the final object
        is always the real response.

        Falls back to the raw text as the message if nothing can be parsed.
        """
        # Strip <think> tags in case llm_builder didn't catch them
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

        # Walk the text with raw_decode to find all valid JSON objects
        decoder = json.JSONDecoder()
        candidates = []
        pos = 0
        while pos < len(text):
            try:
                obj, end = decoder.raw_decode(text, pos)
                if isinstance(obj, dict) and "message" in obj:
                    candidates.append(obj)
                pos = end
            except json.JSONDecodeError:
                pos += 1

        # Take the last candidate — it is the actual answer, not intermediate reasoning
        if candidates:
            try:
                return ExpertResponse(**candidates[-1])
            except ValidationError:
                pass

        # Second fallback: JSON was found but cut off (token limit hit mid-response).
        # Extract just the "message" value so the user sees a real reply, not raw reasoning.
        message_match = re.search(r'"message"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        if message_match:
            return ExpertResponse(message=message_match.group(1))

        # Last resort: treat entire response as the message
        return ExpertResponse(message=text.strip())

    def _build_system_prompt(self, state: BuyBotState) -> str:
        """
        Combines four layers into one system message:
          1. Global Buy-Bot persona    (from prompts.py)
          2. This agent's role prompt  (set by each subclass)
          3. Intake summary            (budget, OS, use case, mobility)
          4. Current user_profile      (what has been collected so far)
          5. JSON output format        (tells the LLM exactly what to return)
        """
        # Show the confirmed intake slots so the agent has full context
        intake_summary = (
            f"Confirmed from intake:\n"
            f"  language:     {state.language} — use this language for every response\n"
            f"  budget:       CHF {state.budget}\n"
            f"  preferred_os: {state.preferred_os}\n"
            f"  use_case:     {state.use_case}\n"
            f"  mobility:     {state.mobility}"
        )

        # Show what has already been collected in this expert stage
        if state.user_profile:
            profile_lines = "\n".join(
                f"  {k}: {v}" for k, v in state.user_profile.items()
            )
            profile_summary = f"Already collected:\n{profile_lines}"
        else:
            profile_summary = "Nothing collected yet — this is the first question."

        # Tell the LLM exactly what format to respond in.
        # The rules here are strict — the LLM must follow them precisely.
        json_format = """\
Respond ONLY with a JSON object — no markdown, no extra text before or after:
{
  "message": "exactly what you say to the user — one short question or acknowledgement only",
  "satisfied": false,
  "user_profile_update": {
    "key": "value"
  }
}

Critical rules for the message field:
  - Write ONLY what the bot says directly to the user
  - Ask ONE question per turn — never combine two questions
  - NO internal reasoning, NO analysis, NO thought process
  - NO laptop brand or model recommendations — those come later in the pipeline
  - Keep it short and conversational

Set satisfied=true only when you have collected enough information.
Use user_profile_update to store new facts the user just shared. Use {} if nothing new."""

        return (
            f"{BUYBOT_SYSTEM_PROMPT}\n\n"
            f"{self.ROLE_PROMPT}\n\n"
            f"{intake_summary}\n\n"
            f"{profile_summary}\n\n"
            f"{json_format}"
        )


# ---------------------------------------------------------------------------
# The 4 expert agents — each one just sets its role prompt
# ---------------------------------------------------------------------------

class UniAgent(BaseExpertAgent):
    """Expert agent for university students."""
    ROLE_PROMPT = UNI_AGENT_ROLE


class GamingAgent(BaseExpertAgent):
    """Expert agent for gamers."""
    ROLE_PROMPT = GAMING_AGENT_ROLE


class ProfessionalAgent(BaseExpertAgent):
    """Expert agent for professionals (coders, editors, ML engineers)."""
    ROLE_PROMPT = PROFESSIONAL_AGENT_ROLE


class OfficeAgent(BaseExpertAgent):
    """Expert agent for home/office users."""
    ROLE_PROMPT = OFFICE_AGENT_ROLE
