# model_config.py
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
MODEL_FAST = "meta-llama/llama-3.2-3b-instruct:free"

# ---------------------------------------------------------------------------
# Strong model — used for the final recommendation, QA answers, and
# search ranking. Quality matters most here; use the best you can afford.
# ---------------------------------------------------------------------------
MODEL_STRONG = "openai/gpt-oss-120b:free"

# ---------------------------------------------------------------------------
# Fallback model — used automatically when fast or strong fail (e.g. rate
# limit, timeout, or model outage). Should be a small, reliable model.
# ---------------------------------------------------------------------------
MODEL_FALLBACK = "nvidia/nemotron-3-super-120b-a12b:free"   # Mistral's own infrastructure — independent of Venice and Google

# ---------------------------------------------------------------------------
# Token limits — raise if replies get cut off, lower to save cost/credits.
# ---------------------------------------------------------------------------
MAX_TOKENS_FAST     = 500
MAX_TOKENS_STRONG   = 1000
MAX_TOKENS_FALLBACK = 1000   # generous — must cover both fast and strong use cases

# ---------------------------------------------------------------------------
# Temperature — 0.0 = deterministic, 1.0 = very creative.
# Fast model benefits from lower temp (more predictable slot extraction).
# Strong model benefits from slightly higher temp (more natural final text).
# Fallback is kept neutral — it needs to handle both roles.
# ---------------------------------------------------------------------------
TEMPERATURE_FAST     = 0.3
TEMPERATURE_STRONG   = 0.7
TEMPERATURE_FALLBACK = 0.5
