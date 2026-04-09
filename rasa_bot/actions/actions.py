"""
actions.py — Custom Rasa actions for Buy-Bot.

Actions:
- ValidateLaptopRecommendationForm: validates form slots
- ActionRecommendLaptop: filters laptop DB and returns recommendations
- ActionCallLanggraph: routes free-form questions to LangGraph agents
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Text
import subprocess

from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

# Resolve the project root so imports work regardless of working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "laptops.json"
LANGGRAPH_PATH = PROJECT_ROOT / "langgraph_agents"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Helper: load laptop database
# ---------------------------------------------------------------------------

def _load_laptops() -> List[Dict]:
    """Load the laptop product database from JSON."""
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Form validation
# ---------------------------------------------------------------------------

class ValidateLaptopRecommendationForm(FormValidationAction):
    """Validates the slots collected by laptop_recommendation_form."""

    def name(self) -> Text:
        return "validate_laptop_recommendation_form"

    def validate_budget(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate that budget is a reasonable numeric value."""
        if slot_value is None:
            dispatcher.utter_message(
                text="I didn't catch your budget. Could you tell me how much you'd like to spend in CHF? 💰"
            )
            return {"budget": None}

        # Strip non-numeric characters and try to parse
        cleaned = "".join(c for c in str(slot_value) if c.isdigit() or c == ".")
        try:
            amount = float(cleaned)
        except ValueError:
            dispatcher.utter_message(
                text="Hmm, I couldn't understand that budget. Could you give me a number, like 800 CHF? 💰"
            )
            return {"budget": None}

        if amount < 300:
            dispatcher.utter_message(
                text="That budget is quite low for a laptop. I'd suggest at least 400–500 CHF for a decent one. What's the minimum you can go? 💸"
            )
            return {"budget": None}

        if amount > 5000:
            dispatcher.utter_message(
                text="Wow, that's a generous budget! Just to confirm — you're willing to spend up to {:.0f} CHF? 💎".format(amount)
            )

        return {"budget": str(int(amount))}

    def validate_use_case(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Accept any use case description."""
        if not slot_value or len(str(slot_value).strip()) == 0:
            dispatcher.utter_message(
                text="Could you tell me what you'll mainly use the laptop for? For example: university, Netflix, gaming... 🎓"
            )
            return {"use_case": None}
        return {"use_case": str(slot_value).strip()}

    def validate_portability(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Map yes/no portability responses."""
        if slot_value is None:
            return {"portability": None}

        text = str(slot_value).lower()
        positive = ["yes", "yeah", "yep", "sure", "always", "every", "daily", "carry", "bring", "commute", "travel", "light", "portable", "on the go"]
        negative = ["no", "nope", "desk", "home", "stays", "not", "don't", "mainly at home"]

        for word in positive:
            if word in text:
                return {"portability": "yes"}
        for word in negative:
            if word in text:
                return {"portability": "no"}

        # Default: accept whatever was said
        return {"portability": str(slot_value).strip()}

    def validate_gaming(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Map yes/no gaming responses."""
        if slot_value is None:
            return {"gaming": None}

        text = str(slot_value).lower()
        positive = ["yes", "yeah", "yep", "sure", "play", "game", "gaming", "cs", "counter", "league", "lol", "fps", "esport", "gta", "fifa", "fortnite"]
        negative = ["no", "nope", "nah", "don't", "not", "never"]

        for word in positive:
            if word in text:
                return {"gaming": "yes"}
        for word in negative:
            if word in text:
                return {"gaming": "no"}

        return {"gaming": str(slot_value).strip()}


# ---------------------------------------------------------------------------
# Laptop recommendation
# ---------------------------------------------------------------------------

class ActionRecommendLaptop(Action):
    """Reads from the laptop DB, filters by user criteria, and returns 2–3 matches."""

    def name(self) -> Text:
        return "action_recommend_laptop"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        budget_str = tracker.get_slot("budget")
        use_case = tracker.get_slot("use_case") or ""
        portability = tracker.get_slot("portability") or ""
        gaming = tracker.get_slot("gaming") or ""

        laptops = _load_laptops()
        if not laptops:
            dispatcher.utter_message(
                text="I'm sorry, I couldn't load our product database right now. Please try again later! 🙏"
            )
            return []

        # Parse budget
        try:
            budget = float(budget_str) if budget_str else 9999
        except (ValueError, TypeError):
            budget = 9999

        wants_gaming = "yes" in str(gaming).lower() or any(
            kw in use_case.lower() for kw in ["gaming", "game", "games", "cs", "counter", "league"]
        )
        wants_portable = "yes" in str(portability).lower()

        # Score each laptop
        scored = []
        for laptop in laptops:
            score = 0

            # Budget filter: must not exceed budget by more than 10%
            if laptop["price_chf"] <= budget * 1.10:
                score += 3
                if laptop["price_chf"] <= budget:
                    score += 2  # bonus for being within budget

            # Gaming preference
            if wants_gaming and laptop.get("gaming_capability") in ["medium", "heavy"]:
                score += 4
            elif not wants_gaming and laptop.get("gaming_capability") == "none":
                score += 2

            # Portability preference
            if wants_portable and laptop.get("weight_kg", 99) <= 1.8:
                score += 3
            elif not wants_portable and laptop.get("weight_kg", 99) > 2.0:
                score += 1

            # Use-case match
            good_for = [g.lower() for g in laptop.get("good_for", [])]
            for keyword in ["study", "university", "work", "netflix", "streaming", "browsing", "gaming"]:
                if keyword in use_case.lower() and keyword in good_for:
                    score += 2

            if score > 0:
                scored.append((score, laptop))

        # Sort by score descending, then price ascending
        scored.sort(key=lambda x: (-x[0], x[1]["price_chf"]))
        top = scored[:3]

        if not top:
            dispatcher.utter_message(
                text=(
                    "I couldn't find a perfect match in our current inventory, but don't worry — "
                    "let me suggest something close! 😊 You might also want to consider adjusting your budget slightly."
                )
            )
            # Fall back to cheapest options within 20% over budget
            fallback = [l for l in laptops if l["price_chf"] <= budget * 1.20]
            fallback.sort(key=lambda l: l["price_chf"])
            top = [(0, l) for l in fallback[:2]]

        if not top:
            dispatcher.utter_message(
                text="I'm really sorry, we don't have anything matching your criteria right now. Check back soon! 🛒"
            )
            return []

        dispatcher.utter_message(
            text="🎉 Great news! Here are my top picks for you:\n"
        )

        for rank, (_, laptop) in enumerate(top, start=1):
            msg = (
                f"**{rank}. {laptop['name']}** — {laptop['price_chf']} CHF\n"
                f"{laptop['short_description']}\n"
                f"🔋 Battery: up to {laptop['battery_hours']}h | "
                f"⚖️ Weight: {laptop['weight_kg']}kg\n"
            )
            dispatcher.utter_message(text=msg)

        dispatcher.utter_message(
            text="Would you like to see more details on any of these, or compare two options? Just ask! 😊"
        )
        return []


# ---------------------------------------------------------------------------
# LangGraph integration
# ---------------------------------------------------------------------------

class ActionCallLanggraph(Action):
    """Routes free-form / complex questions to the LangGraph agent graph."""

    def name(self) -> Text:
        return "action_call_langgraph"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text", "")

        # Gather current slot context to give LangGraph agents more information
        context = {
            "budget": tracker.get_slot("budget"),
            "use_case": tracker.get_slot("use_case"),
            "portability": tracker.get_slot("portability"),
            "gaming": tracker.get_slot("gaming"),
        }

        # LangGraph runs in the .venv (Python 3.13) which has pydantic v2.
        # The rasa_venv uses pydantic v1, so we call LangGraph via subprocess.
        venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
        script = (
            "import sys, json; sys.path.insert(0, sys.argv[1]);"
            "from langgraph_agents.graph import run_buybot_graph;"
            "ctx = json.loads(sys.argv[3]);"
            "print(run_buybot_graph(sys.argv[2], ctx))"
        )
        try:
            result = subprocess.run(
                [str(venv_python), "-c", script, str(PROJECT_ROOT), user_message, json.dumps(context)],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "PYTHONUTF8": "1"},
            )
            response = result.stdout.strip()
            if not response:
                raise RuntimeError(result.stderr[:200] if result.stderr else "empty output")
            dispatcher.utter_message(text=response)
        except Exception as e:
            dispatcher.utter_message(
                text="Hmm, I ran into a little hiccup there. Could you rephrase your question? I'm here to help you find the perfect laptop! 😊"
            )

        return []
