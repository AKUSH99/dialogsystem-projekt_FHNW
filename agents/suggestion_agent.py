# agents/suggestion_agent.py
"""
SuggestionAgent — Stage 5 of the Buy-Bot pipeline.

Receives the two laptops chosen by the search agent and the full user profile,
then writes a natural-language recommendation tailored to this specific user.

This is the only agent that returns plain text — no JSON parsing needed.
The LLM just writes the recommendation directly.

Key behaviour:
  - Language adapts to the user's technical level (inferred from user_profile)
  - Always connects specs to what the user actually does ("great for CS2" not "144Hz")
  - Handles the edge case where no laptops were found
"""

import json

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from agents.prompts import BUYBOT_SYSTEM_PROMPT, SUGGESTION_AGENT_ROLE
from agents.state import BuyBotState


class SuggestionAgent:
    """
    Generates the final laptop recommendation for the user.

    Usage as a LangGraph node:
        agent = SuggestionAgent(llm)
        graph.add_node("suggestion_agent", agent.run)
    """

    def __init__(self, llm):
        self.llm = llm

    def run(self, state: BuyBotState) -> dict:
        """
        Generates a natural-language recommendation and returns it as a state update.
        Sets current_stage to "done" so the graph knows the pipeline is complete.
        """
        # Handle edge case: search agent found nothing
        if state.laptop_primary is None:
            message = self._no_results_message(state)
            return {
                "messages": [AIMessage(content=message)],
                "current_stage": "done",
            }

        # Normal case: generate the recommendation
        system_message = SystemMessage(content=self._build_system_prompt(state))

        # Include the full conversation history so the LLM can detect the user's language.
        # Without this, the LLM has no signal that the user wrote in English (or German)
        # and tends to default to German for Swiss-context queries.
        laptops_text = self._format_laptops(state)
        final_instruction = HumanMessage(content=laptops_text)

        raw = self.llm.invoke([system_message, *state.messages, final_instruction])

        return {
            "messages": [AIMessage(content=raw.content)],
            "current_stage": "done",
        }

    def _build_system_prompt(self, state: BuyBotState) -> str:
        """
        Combines the global persona, the suggestion role, and the full user
        profile into one system message.

        The user profile is included so the LLM can reference specific things
        the user said (e.g. "you mentioned CS2" or "you need Premiere Pro").
        """
        # Build the full user profile including intake slots
        full_profile = {
            "language": state.language,  # always use this language for the recommendation
            "budget_chf": state.budget,
            "preferred_os": state.preferred_os,
            "use_case": state.use_case,
            "mobility": state.mobility,
            **state.user_profile,  # expert agent enrichments
        }

        profile_text = json.dumps(full_profile, indent=2)

        return (
            f"{BUYBOT_SYSTEM_PROMPT}\n\n"
            f"{SUGGESTION_AGENT_ROLE}\n\n"
            f"User profile (reference this when explaining your recommendation):\n"
            f"{profile_text}\n\n"
            f"Important formatting rules:\n"
            f"  - Show the price in CHF clearly at the top of each laptop section\n"
            f"  - Lead with the laptop name and price before anything else\n"
            f"  - Connect every spec to what the user actually does — no raw spec dumps"
        )

    def _format_laptops(self, state: BuyBotState) -> str:
        """
        Formats both laptops as a readable block for the LLM.
        Includes the match_reason added by the search agent so the LLM
        has a starting point for its explanation.
        """
        def laptop_block(label: str, laptop: dict) -> str:
            lines = [f"--- {label} ---"]
            for key, value in laptop.items():
                if value is not None:
                    lines.append(f"  {key}: {value}")
            return "\n".join(lines)

        primary_block = laptop_block("PRIMARY RECOMMENDATION", state.laptop_primary)

        # Alternative might be the same laptop if only one result was found
        if state.laptop_alternative and state.laptop_alternative["id"] != state.laptop_primary["id"]:
            alt_block = laptop_block("ALTERNATIVE", state.laptop_alternative)
        else:
            alt_block = "--- ALTERNATIVE ---\nNo distinct alternative found within budget."

        return f"{primary_block}\n\n{alt_block}"

    def _no_results_message(self, state: BuyBotState) -> str:
        """
        Returns a friendly message when the search agent found no laptops.
        Suggests adjusting budget or preferences rather than just saying "no results".
        """
        return (
            f"I searched our full catalogue but couldn't find a laptop that fits "
            f"all your criteria within CHF {state.budget} (±20%). "
            f"A few options to try:\n"
            f"- Raise the budget slightly — even CHF 100–150 more opens up more options\n"
            f"- Relax the OS preference if you set one\n"
            f"- Let me know and I'll search again with adjusted criteria."
        )
