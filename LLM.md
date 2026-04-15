# LLM.md – Navigation Guide

Quick reference for AI assistants working on Buy-Bot.

---

## File Guide

| File | Purpose | Read If |
|---|---|---|
| **README.md** | Personas, example dialogs, problem/solution | Understanding project context and user needs |
| **ARCHITECTURE.md** | Full technical design, all agents, database | Implementing any part of the system |
| **SETUP.md** | Installation, dependencies, environment | Setting up the local environment |
| **CHANGELOG.md** | Development progress log | Tracking what has been done |
| **test-chat.py** | API connection test only | Testing OpenRouter + LangSmith integration |

---

## Pipeline Overview

```
Rasa NLU (intake)
    → Router LLM
        → Expert Agent (one of 4)
            → Search Agent (queries laptops.db)
                → Suggestion Agent (final recommendation)

QA Agent intercepts at any stage for off-script questions.
```

---

## Key Concepts

### Rasa Intake (Stage 1)
Collects 4 slots via structured forms, then hands off a payload:
```python
{ "budget": 900.0, "preferred_os": "windows", "use_case": "gaming", "mobility": "high" }
```

### Four Expert Agents (Stage 3)
| Agent | Target User | Key Focus |
|---|---|---|
| Uni Agent | Students | Battery, weight, value |
| Gaming Agent | Gamers | GPU tier, refresh rate, thermal |
| Professional Agent | Coders, editors, ML engineers | CPU/GPU power, display accuracy, RAM |
| Private/Office Agent | Home users, business | Build, webcam, security features |

### Language Adaptation
The suggestion agent reads the `user_profile` to calibrate tone:
- Technical users (mentioned specific software/games) → use specs directly
- Non-technical users → translate specs into lifestyle language
- No explicit flag needed — the LLM infers from context

### Budget Handling
- Extracted as float (e.g. `800.0`) — never translated to "low/medium/high"
- Search agent applies ±20% margin: `budget * 0.8` to `budget * 1.2`

### Product Database
- `data/laptops.db` — SQLite, 28 laptops, 84 columns
- `data/laptops.sql` — source schema + all INSERT statements
- `data/init_db.py` — rebuilds the DB: `python data/init_db.py`
- `laptop_use_cases` table — junction table for use-case tag filtering (198 rows)

---

## Implementation Status

| Phase | Scope | Status |
|---|---|---|
| 1 | Infrastructure: API, LangSmith | Done |
| 2 | Product database: 28 laptops, SQLite | Done |
| 3 | Rasa NLU: intents, slot forms, webhook | Next |
| 4 | LangGraph: router + 4 expert agents | Planned |
| 5 | Search agent + suggestion agent | Planned |
| 6 | QA agent | Planned |
| 7 | Frontend: Streamlit + Telegram | Planned |

---

## Important Constraints

- Budget always as float — never "low/medium/high"
- Search returns exactly 2 results: 1 primary + 1 alternative
- QA agent must be able to interrupt and resume any stage
- Language in bot responses adapts to user technical level — no fixed register

---

## Last Updated
2026-04-15
