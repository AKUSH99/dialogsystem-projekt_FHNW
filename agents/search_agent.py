# agents/search_agent.py
"""
SearchAgent — Stage 4 of the Buy-Bot pipeline.

Two-step process:
  1. SQL query  → filters laptops.db down to a candidate pool using hard
                  constraints (budget ±20%, OS, use-case tags, weight)
  2. LLM ranking → reads the candidates + full user_profile, picks the
                   best primary match and one meaningful alternative

Why both steps?
  SQL is reliable for exact constraints (price range, OS, DB joins).
  LLM is better for nuanced ranking (e.g. "CS2 player who carries it daily"
  needs light weight + esports GPU tier — not just the highest score).
"""

import json
import os
import re
import sqlite3

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ValidationError

from agents.prompts import BUYBOT_SYSTEM_PROMPT, SEARCH_AGENT_ROLE
from agents.state import BuyBotState


# ---------------------------------------------------------------------------
# Mappings from intake slot values → database values
# ---------------------------------------------------------------------------

# Maps our 4 use_case values to the relevant tags in the laptop_use_cases table.
# A laptop only needs to match ONE of these tags to be included as a candidate.
USE_CASE_TAGS = {
    "gaming":       ["gaming", "esports", "heavy_gaming", "4k_gaming"],
    "university":   ["university", "study", "note_taking", "everyday"],
    "professional": ["programming", "video_editing", "photo_editing", "design",
                     "machine_learning", "3d_rendering", "vfx", "music_production",
                     "4k_editing"],
    "office":       ["office", "work", "business", "working_from_home", "video_calls"],
}

# Maps our preferred_os slot values to SQL WHERE conditions.
OS_FILTER = {
    "windows":       "l.os LIKE 'Windows%'",
    "macos":         "l.os = 'macOS'",
    "no_preference": None,  # no filter applied
}


# ---------------------------------------------------------------------------
# LLM ranking response schema
# ---------------------------------------------------------------------------

class RankResponse(BaseModel):
    """
    What the LLM returns after reviewing the candidate pool.

    primary_id       → id of the best matching laptop
    alternative_id   → id of a meaningful alternative (different trade-off)
    primary_reason   → brief reason why the primary fits (used by suggestion agent)
    alternative_reason → brief reason why someone would pick the alternative instead
    """
    primary_id: str
    alternative_id: str
    primary_reason: str
    alternative_reason: str


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class SearchAgent:
    """
    Queries laptops.db and returns the two best matches for the user.

    Usage as a LangGraph node:
        agent = SearchAgent(llm, db_path="data/laptops.db")
        graph.add_node("search_agent", agent.run)
    """

    def __init__(self, llm, db_path: str = "data/laptops.db"):
        """
        llm     — ChatOpenAI client for the ranking step
        db_path — path to the SQLite database
        """
        self.llm = llm
        self.db_path = db_path

    def run(self, state: BuyBotState) -> dict:
        """
        Runs the full two-step search: SQL filter → LLM ranking.
        Returns a state update with laptop_primary and laptop_alternative set.
        """
        # Step 1: Filter to a candidate pool using SQL
        candidates = self._query_candidates(state, budget_margin=0.20)

        # If the strict budget gives too few results, widen the margin and retry
        if len(candidates) < 3:
            candidates = self._query_candidates(state, budget_margin=0.40)

        # If still no results, return empty — suggestion agent will handle this
        if not candidates:
            return {
                "laptop_primary": None,
                "laptop_alternative": None,
                "current_stage": "suggestion",
            }

        # If only one result, use it as both (edge case for very narrow budgets)
        if len(candidates) == 1:
            return {
                "laptop_primary": candidates[0],
                "laptop_alternative": candidates[0],
                "current_stage": "suggestion",
            }

        # Step 2: LLM ranks the candidates and picks primary + alternative
        ranked = self._rank_candidates(candidates, state)

        # Look up the full laptop dicts by the IDs the LLM chose
        candidates_by_id = {c["id"]: c for c in candidates}
        primary = candidates_by_id.get(ranked.primary_id, candidates[0])
        alternative = candidates_by_id.get(ranked.alternative_id, candidates[1])

        # Attach the LLM's reasoning so the suggestion agent can use it
        primary["match_reason"] = ranked.primary_reason
        alternative["match_reason"] = ranked.alternative_reason

        return {
            "laptop_primary": primary,
            "laptop_alternative": alternative,
            "current_stage": "suggestion",
        }

    def _query_candidates(self, state: BuyBotState, budget_margin: float) -> list[dict]:
        """
        Queries laptops.db with hard constraints and returns matching laptops.

        Filters applied:
          - price_chf within budget ±margin
          - use_case matches one of the relevant DB tags
          - os filter if user has a preference
          - weight_kg < 2.0 if mobility is "high"

        Returns a list of laptop dicts, ordered by value_score descending.
        Capped at 10 candidates to keep the LLM prompt manageable.
        """
        price_min = state.budget * (1 - budget_margin)
        price_max = state.budget * (1 + budget_margin)

        # Get the relevant use-case tags for this user's intake use_case
        use_case_tags = USE_CASE_TAGS.get(state.use_case, [])
        # Build SQL placeholders: (?, ?, ?) for the IN clause
        tag_placeholders = ", ".join("?" * len(use_case_tags))

        # Build optional filter clauses
        extra_clauses = []
        extra_params = []

        os_condition = OS_FILTER.get(state.preferred_os)
        if os_condition:
            extra_clauses.append(os_condition)

        if state.mobility == "high":
            # Gaming laptops are inherently heavier — use a softer threshold.
            # The expert agent already discussed the weight vs GPU trade-off with the user.
            weight_limit = 2.5 if state.use_case == "gaming" else 2.0
            extra_clauses.append(f"l.weight_kg < {weight_limit}")

        # Combine extra clauses into a WHERE fragment
        extra_sql = ""
        if extra_clauses:
            extra_sql = "AND " + " AND ".join(extra_clauses)

        query = f"""
            SELECT
                l.id, l.name, l.brand, l.price_chf, l.category,
                l.weight_kg, l.battery_life_hours, l.gaming_tier, l.os,
                l.disp_panel_type, l.disp_refresh_hz, l.disp_nits,
                l.disp_color_p3_pct, l.gpu_tgp_w,
                l.fingerprint_reader, l.webcam_resolution, l.npu_tops,
                l.value_score, l.performance_score,
                l.portability_score, l.build_quality_score, l.display_score,
                r.gb         AS ram_gb,
                s.gb         AS storage_gb,
                g.model      AS gpu_model,
                g.vram_gb    AS gpu_vram_gb,
                c.model      AS cpu_model,
                c.cores      AS cpu_cores
            FROM laptops l
            JOIN laptop_use_cases uc ON l.id = uc.laptop_id
            LEFT JOIN ram_specs    r ON l.ram_id     = r.ram_id
            LEFT JOIN storage_specs s ON l.storage_id = s.storage_id
            LEFT JOIN gpu_specs     g ON l.gpu_id     = g.gpu_id
            LEFT JOIN cpu_specs     c ON l.cpu_id     = c.cpu_id
            WHERE
                l.price_chf BETWEEN ? AND ?
                AND uc.use_case IN ({tag_placeholders})
                {extra_sql}
            GROUP BY l.id
            ORDER BY l.value_score DESC
            LIMIT 10
        """

        params = [price_min, price_max] + use_case_tags + extra_params

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # lets us access columns by name
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        # Convert each Row to a plain dict
        return [dict(row) for row in rows]

    def _rank_candidates(self, candidates: list[dict], state: BuyBotState) -> RankResponse:
        """
        Sends the candidate pool and full user profile to the LLM.
        The LLM picks the best primary match and a meaningful alternative.

        Returns a RankResponse with the chosen IDs and brief reasoning.
        Falls back to the top two candidates by value_score if parsing fails.
        """
        system_message = SystemMessage(content=self._build_ranking_prompt(state))
        user_message = HumanMessage(content=json.dumps(candidates, indent=2))

        raw = self.llm.invoke([system_message, user_message])
        return self._parse_response(raw.content, fallback_candidates=candidates)

    def _parse_response(self, text: str, fallback_candidates: list[dict]) -> RankResponse:
        """
        Parses the LLM's JSON ranking response into a RankResponse object.
        Falls back to the top two candidates by DB order if parsing fails.
        """
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return RankResponse(**data)
            except (json.JSONDecodeError, ValidationError):
                pass

        # Fallback: top two from SQL ordering (already sorted by value_score)
        return RankResponse(
            primary_id=fallback_candidates[0]["id"],
            alternative_id=fallback_candidates[1]["id"],
            primary_reason="Best overall value score for your requirements.",
            alternative_reason="Second best overall match.",
        )

    def _build_ranking_prompt(self, state: BuyBotState) -> str:
        """
        Builds the system prompt for the LLM ranking step.
        Includes the full user profile so the LLM can make a nuanced choice.
        """
        profile_text = json.dumps(
            {
                "budget": state.budget,
                "preferred_os": state.preferred_os,
                "use_case": state.use_case,
                "mobility": state.mobility,
                **state.user_profile,
            },
            indent=2,
        )

        json_format = """\
Respond ONLY with a JSON object — no markdown, no extra text:
{
  "primary_id": "laptop_XXX",
  "alternative_id": "laptop_XXX",
  "primary_reason": "one sentence explaining why this is the best fit",
  "alternative_reason": "one sentence explaining the trade-off and who would prefer this"
}"""

        return (
            f"{BUYBOT_SYSTEM_PROMPT}\n\n"
            f"{SEARCH_AGENT_ROLE}\n\n"
            f"User profile:\n{profile_text}\n\n"
            f"Review the laptop list below and pick the best primary match "
            f"and one meaningful alternative.\n\n"
            f"{json_format}"
        )
