# Buy-Bot — Architecture Thought Process

Design decisions and reasoning made during the LangGraph pipeline planning phase.

---

## 1. Why We Dropped Rasa

Original plan: Rasa NLU for intake (collecting 4 slots), then hand off to LangGraph.

**Problem:** Rasa 3.6.x (open source) requires Python 3.8–3.10. The project runs Python 3.12. Rasa Pro supports newer Python versions but requires a commercial license — not suitable for a student project.

**Alternatives considered:**
- `pyenv` to install Python 3.10 (separate venv just for Rasa) — works but adds environment complexity
- Docker (`rasa/rasa:3.6.21`) — reproducible but overhead for a demo project
- Skip Rasa entirely — cleanest option

**Decision:** Skip Rasa. Build the entire pipeline with LangGraph agents. For 4 slots, a full Rasa setup is overengineering — a single LangGraph intake agent with structured LLM output does the same job with less infrastructure.

---

## 2. Intake Agent Design

The intake agent replaces the Rasa block. Its only job: collect the 4 slots before handing off to the router.

**Slots to collect:**
| Slot | Type | Valid Values |
|---|---|---|
| `budget` | float | e.g. `900.0` |
| `preferred_os` | str | `windows`, `macos`, `no_preference` |
| `use_case` | str | `gaming`, `university`, `professional`, `office` |
| `mobility` | str | `high`, `medium`, `low` |

**Extraction approach:** Structured output — one LLM call per user turn returns both the chat message and any newly detected slot values. Already-filled slots are never overwritten. The LLM is told which slots are still missing each turn.

**Ambiguity handling:** "gaming and uni" → routes to `gaming` (dominant use case). The LLM resolves this naturally from the system prompt instruction.

---

## 3. Two-Layer Prompt Structure

**Problem:** Defining Buy-Bot's persona in every agent's system prompt leads to duplication. Changing the tone would mean editing 6+ files.

**Solution:** Two layers for every LLM call:

```
Layer 1 — BUYBOT_SYSTEM_PROMPT    (global, same for every agent)
Layer 2 — AGENT_ROLE_PROMPT       (specific to what this agent is doing right now)
```

**Layer 1** defines: who Buy-Bot is, personality, tone, language adaptation rules.

**Layer 2** defines: what this specific agent's current job is, what it needs to collect or produce.

All prompts live in `agents/prompts.py`. One edit to the persona affects all agents simultaneously.

---

## 4. Shared State Design

**Problem:** Multiple agents each know different things. The search agent needs everything — intake slots, expert agent enrichments, and DB query parameters. Fragmented state means the search agent either gets nothing or you end up passing JSON files between processes.

**Solution:** One `BuyBotState` TypedDict that flows through the entire graph. Every agent reads from it and writes back to it. No files, no inter-process communication.

```python
class BuyBotState(TypedDict):
    session_id: str           # ties all traces for one conversation together
    messages: list            # full conversation history, shared by all agents
    current_stage: str        # "intake" | "router" | "expert" | "search" | "suggestion"

    # Stage 1 — Intake (always typed, always present after intake completes)
    budget: float | None
    preferred_os: str | None
    use_case: str | None
    mobility: str | None

    # Stage 3 — Expert agent enrichment (grows dynamically, shape varies by use case)
    user_profile: dict

    # Stage 4 — Search results
    laptop_primary: dict | None
    laptop_alternative: dict | None
```

**Why `user_profile` is a plain dict:**
The 4 intake slots are guaranteed and always the same shape → typed as top-level fields.
Expert agent enrichments differ by use case:
- Gaming agent adds `games`, `gpu_priority`, `carry_daily`
- Professional agent adds `software`, `external_monitors`, `export_needs`

A typed TypedDict can't express this variability cleanly. A plain dict lets each expert agent write what it knows, and the search agent reads with `.get()` for optional keys.

**What the search agent sees:**
```python
# Guaranteed — top-level, always set after intake
state["budget"]
state["preferred_os"]
state["use_case"]
state["mobility"]

# Optional — expert enrichment, read defensively
state["user_profile"].get("games")
state["user_profile"].get("gpu_priority")
```

---

## 5. Monitoring and Tracing

**LangSmith** is the tracing layer. It is already configured in the project. With LangGraph, tracing is automatic — every node execution, LLM call, and state transition is captured without extra code.

**What LangSmith gives us:**
- Full conversation trace per session (grouped by `session_id` / thread ID)
- Latency and token usage per agent node
- State snapshot before and after each node
- Error logs with full stack traces
- Works in production — env vars are sufficient

**The gap vs Voiceflow:**
Voiceflow has built-in business-level analytics (completion rate, drop-off points, intent success). LangSmith is developer-level — it does not automatically know whether the bot successfully recommended a laptop.

**How we close the gap:**
Explicit custom feedback logged at conversation end:

```python
from langsmith import Client

client = Client()
client.create_feedback(run_id, key="recommendation_made", score=1.0 if state["laptop_primary"] else 0.0)
client.create_feedback(run_id, key="use_case", value=state["use_case"])
client.create_feedback(run_id, key="drop_off_stage", value=state["current_stage"])
```

This enables filtering in LangSmith: "how many sessions ended with a recommendation", "which stage had the most drop-offs", "recommendation rate per use case". Sufficient for the FHNW assessment and a production deployment.

---

## 6. Build Order

| Step | File | Reason |
|---|---|---|
| 1 | `agents/state.py` | Foundation — every other file imports from here |
| 2 | `agents/prompts.py` | Global persona + all agent role prompts in one place |
| 3 | `agents/intake_agent.py` | First working agent — validates the state + prompt design |
| 4 | `agents/router.py` | Routes intake payload to correct expert agent |
| 5 | `agents/[uni/gaming/professional/office]_agent.py` | Expert agents — enrich `user_profile` |
| 6 | `agents/search_agent.py` | Queries `laptops.db` using full state |
| 7 | `agents/suggestion_agent.py` | Generates recommendation from laptops + user_profile |
| 8 | `agents/qa_agent.py` | Always-on interruption handler |
| 9 | `agents/graph.py` | Wires all agents into one LangGraph graph |
| 10 | `frontend/` | Streamlit + Telegram after pipeline is verified |
