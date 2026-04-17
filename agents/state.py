
# agents/state.py
"""
Defines BuyBotState — the single shared state object for the entire pipeline.

Every agent reads from this state and writes updates back to it.
Think of it as the "memory" of one conversation: it starts mostly empty
and gets filled in as the user moves through each pipeline stage.

Why Pydantic BaseModel instead of a plain TypedDict?
  → Pydantic validates values at runtime. If an agent accidentally sets
    use_case="video_editing" (not a valid option), it fails immediately
    with a clear error instead of silently breaking 3 stages later.
"""

import operator
import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, field_validator


class BuyBotState(BaseModel):
    """
    One instance of BuyBotState represents one full conversation.

    Fields are grouped by which pipeline stage fills them:
      - Session fields:  always set at the start
      - Stage 1 (Intake): budget, preferred_os, use_case, mobility
      - Stage 3 (Expert): user_profile (grows as expert agent asks questions)
      - Stage 4 (Search): laptop_primary, laptop_alternative
    """

    # arbitrary_types_allowed → lets Pydantic work with the Annotated messages field
    # validate_assignment=True → runs validators when a field is updated after creation
    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------

    # Unique ID for this conversation.
    # Used as the LangGraph thread ID so all turns are grouped in LangSmith.
    session_id: str

    # Full message history (all user + bot turns in order).
    # Annotated with operator.add so LangGraph APPENDS new messages
    # instead of replacing the whole list on every state update.
    messages: Annotated[list, operator.add] = []

    # Which pipeline stage is currently active.
    # Logged to LangSmith so we can see where conversations drop off.
    current_stage: str = "intake"  # "intake" | "router" | "expert" | "search" | "suggestion"

    # ------------------------------------------------------------------
    # Stage 1 — Intake
    # Collected by intake_agent. All None at the start of a conversation.
    # ------------------------------------------------------------------

    # Language the user chose at the start of the conversation.
    # All agents use this to ensure consistent language throughout.
    language: Literal["english", "german"] | None = None

    # How much the user wants to spend (in CHF).
    # Always stored as a float — never translated to "low/medium/high".
    # The search agent applies a ±20% margin when querying the database.
    budget: float | None = None

    # Which operating system the user prefers.
    preferred_os: Literal["windows", "macos", "no_preference"] | None = None

    # What the user mainly needs the laptop for.
    # Determines which expert agent the router sends them to.
    use_case: Literal["gaming", "university", "professional", "office"] | None = None

    # How portable the laptop needs to be.
    # "high" → weight filter applied in search (< 2.0 kg preferred)
    mobility: Literal["high", "medium", "low"] | None = None

    # ------------------------------------------------------------------
    # Stage 3 — Expert agent enrichment
    # ------------------------------------------------------------------

    # Extra details collected by the expert agent (uni/gaming/professional/office).
    # Stored as a plain dict because the shape differs per use case:
    #   gaming      → {"games": ["CS2", "LoL"], "gpu_priority": "medium", "carry_daily": True}
    #   professional → {"software": ["Premiere Pro"], "external_monitors": True}
    # The search agent always reads these with .get() so missing keys are safe.
    user_profile: dict = {}

    # ------------------------------------------------------------------
    # Stage 4 — Search results
    # ------------------------------------------------------------------

    # Set by search_agent after querying laptops.db.
    # primary   → best match for the user's requirements
    # alternative → a different trade-off (e.g. lighter, cheaper, one tier higher)
    laptop_primary: dict | None = None
    laptop_alternative: dict | None = None

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("budget")
    @classmethod
    def budget_must_be_positive(cls, v):
        """Ensures budget is always a positive number.
        Also coerces strings like "900" to float 900.0 automatically.
        """
        if v is not None:
            v = float(v)  # coerce string input to float
            if v <= 0:
                raise ValueError("Budget must be a positive number")
        return v


def create_initial_state(session_id: str | None = None) -> BuyBotState:
    """
    Creates a blank BuyBotState for the start of a new conversation.

    Call this once when a user opens a new chat session.
    All fields start as None or empty — the agents fill them in.
    A random session_id is generated automatically if none is provided.

    Example:
        state = create_initial_state()
        state = create_initial_state(session_id="test-session-1")
    """
    return BuyBotState(session_id=session_id or str(uuid.uuid4()))
