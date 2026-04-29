w# model_config.py
"""
Central model configuration for Buy-Bot.

To switch models, change the strings below — that's it.
Both main.py (CLI) and frontend/app.py (Streamlit) import from here,
so you only ever need to edit one file.

Find available models (including free ones) at:
    https://openrouter.ai/models?q=free
"""

# ---------------------------------------------------------------------------
# Fast model — used for slot extraction, expert follow-ups, and routing.
# Speed matters more than depth here. A 7B–27B model is usually enough.
# ---------------------------------------------------------------------------
MODEL_FAST = "google/gemma-4-26b-a4b-it"

# ---------------------------------------------------------------------------
# Strong model — used for the final recommendation, QA answers, and
# search ranking. Quality matters most here; use the best you can afford.
# ---------------------------------------------------------------------------
MODEL_STRONG = "google/gemma-4-26b-a4b-it"

# ---------------------------------------------------------------------------
# Fallback model — used automatically when fast or strong fail (e.g. rate
# limit, timeout, or model outage). Should be a small, reliable model.
# ---------------------------------------------------------------------------
MODEL_FALLBACK = "google/gemma-4-26b-a4b-it"

# ---------------------------------------------------------------------------
# Token limits — raise if replies get cut off, lower to save cost/credits.
# Fast is set high because reasoning models spend tokens thinking before
# outputting the required JSON — 500 was too low and caused cut-off responses.
# ---------------------------------------------------------------------------
MAX_TOKENS_FAST     = 1500
MAX_TOKENS_STRONG   = 1500
MAX_TOKENS_FALLBACK = 1500

# ---------------------------------------------------------------------------
# Temperature — 0.0 = deterministic, 1.0 = very creative.
# Fast model benefits from lower temp (more predictable slot extraction).
# Strong model benefits from slightly higher temp (more natural final text).
# Fallback is kept neutral — it needs to handle both roles.
# ---------------------------------------------------------------------------
TEMPERATURE_FAST     = 0.3
TEMPERATURE_STRONG   = 0.7
TEMPERATURE_FALLBACK = 0.5
