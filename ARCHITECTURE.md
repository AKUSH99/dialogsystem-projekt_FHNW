# Buy-Bot Architecture

Technical design for Buy-Bot using Rasa NLU and a LangGraph multi-agent pipeline.

> See [README.md](README.md) for user personas and example conversations.

---

## Design Philosophy

Buy-Bot uses a **staged pipeline**: Rasa handles structured intake, then a chain of LangGraph agents progressively refines the user profile and generates a tailored recommendation. A QA agent is available at every stage to handle off-script questions.

Language adapts to the user. A user who mentions Premiere Pro or PyTorch gets spec-level detail (VRAM, CPU architecture, display color accuracy). A user who says "uni and Netflix" gets lifestyle language. The suggestion agent infers the right register from the `user_profile` built during the conversation — no explicit flag needed.

---

## System Architecture

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Stage 1 — Rasa NLU (intake)         │
│  Collects: budget, OS, use_case,     │
│  mobility via structured forms       │
└────────────┬─────────────────────────┘
             │  structured slot payload
             ▼
┌──────────────────────────────────────┐
│  Stage 2 — Router LLM                │
│  Routes to one of 4 expert agents    │
└──────┬─────────┬──────────┬──────────┘
       │         │          │         │
       ▼         ▼          ▼         ▼
  ┌────────┐ ┌──────┐ ┌──────────┐ ┌────────────┐
  │  Uni   │ │Gaming│ │ Profess- │ │  Private / │
  │ Agent  │ │Agent │ │  ional   │ │   Office   │
  │        │ │      │ │  Agent   │ │   Agent    │
  └────┬───┘ └──┬───┘ └────┬─────┘ └─────┬──────┘
       └────────┴──────────┴─────────────┘
             │  enriched user_profile
             ▼
┌──────────────────────────────────────┐
│  Stage 4 — Search Agent              │
│  Queries laptops.db                  │
│  Returns: 1 primary + 1 alternative  │
└────────────┬─────────────────────────┘
             │  2 laptop candidates + user_profile
             ▼
┌──────────────────────────────────────┐
│  Stage 5 — Suggestion Agent          │
│  Generates natural-language          │
│  recommendation (language adapted    │
│  to user technical level)            │
└──────────────────────────────────────┘

         ┌──────────────────────────────┐
         │  QA Agent (always-on)        │
         │  Intercepts at any stage:    │
         │  product questions,          │
         │  "why did you ask that?",    │
         │  spec explanations           │
         └──────────────────────────────┘
```

---

## Stage 1 — Rasa NLU (Intake)

Handles the opening turns. Uses slot-filling forms to extract exactly 4 values before handing off.

### Extracted Slots

| Slot | Type | Example |
|---|---|---|
| `budget` | float | `800.0`, `1500.0` |
| `preferred_os` | string | `windows`, `macos`, `no_preference` |
| `use_case` | string | `gaming`, `university`, `professional`, `office` |
| `mobility` | string | `high`, `medium`, `low` |

### Intent → Agent Routing

| Intent | Routed To |
|---|---|
| `university` | Uni Agent |
| `gaming` | Gaming Agent |
| `professional` | Professional Agent |
| `office` / `private` | Private/Office Agent |

### Handoff Payload

```python
{
    "budget": 900.0,
    "preferred_os": "windows",
    "use_case": "gaming",
    "mobility": "high"
}
```

---

## Stage 2 — Router LLM

Receives the Rasa payload and selects the appropriate expert agent. Handles ambiguous cases (e.g. "gaming and some coding") by picking the dominant use case or asking one clarifying question.

---

## Stage 3 — Expert Agents

Each agent asks domain-specific follow-up questions to build a detailed `user_profile`.

### Uni Agent
Target: students carrying the laptop daily to campus.

Follow-up questions:
- How long are your days away from a charger?
- Priority: battery life or display quality?
- Do you need it for any creative work (design, video)?

### Gaming Agent
Target: gamers, may also use for uni.

Follow-up questions:
- Which games? (esports titles like CS2/LoL vs. AAA like Cyberpunk)
- Desktop-replacement or carry it daily?
- Willing to trade weight for GPU power?

### Professional Agent
Target: coders, video/photo editors, 3D artists, ML engineers.

Follow-up questions:
- Which software? (Premiere Pro, DaVinci, VS Code, PyTorch, Blender, etc.)
- Do you need 4K export or real-time preview?
- macOS or Windows toolchain?
- External monitors used, or laptop screen is primary?

### Private / Office Agent
Target: home users, office workers, business travellers.

Follow-up questions:
- Mainly at a desk or on the move?
- Video calls important? (webcam quality, microphone)
- Any IT/security requirements (IR camera, fingerprint, Windows Hello)?

### Enriched user_profile after Stage 3

```python
{
    "budget": 900.0,
    "preferred_os": "windows",
    "use_case": "gaming",
    "mobility": "high",
    "games": ["CS2", "League of Legends"],
    "carry_daily": True,
    "gpu_priority": "medium"   # esports, not AAA
}
```

---

## Stage 4 — Search Agent

Queries `data/laptops.db` against the `user_profile`. Returns exactly 2 results.

### Filtering logic

```python
# Budget: +/- 20% margin
price_min = budget * 0.8
price_max = budget * 1.2

# Filter by use_case via laptop_use_cases table
# Filter by preferred_os if not no_preference
# Filter by gaming_tier if use_case == gaming
# Filter by weight_kg if mobility == high (< 2.0 kg preferred)
```

### Output
- **Primary match** — best fit for stated requirements
- **Alternative** — different trade-off (e.g. lighter, cheaper, or one tier higher spec)

---

## Stage 5 — Suggestion Agent

Receives the 2 laptops and full `user_profile`. Generates a natural-language recommendation.

### Language adaptation
The agent reads the `user_profile` to calibrate vocabulary:
- User mentioned Blender / PyTorch / Premiere → use specs (VRAM, CPU cores, color gamut %)
- User mentioned "uni and Netflix" → use lifestyle language, no jargon
- Mixed profile (gaming + coding) → lead with relevant spec, explain others briefly

### Output format
- Brief explanation of why the primary match fits
- Key specs called out (in appropriate language)
- What the alternative trades off and why someone would choose it
- One closing prompt (e.g. "Want to compare these two side by side?")

---

## QA Agent (Always-On)

Intercepts messages at any stage when the user asks something off the main flow.

### Handled question types
- **"Why are you asking that?"** — explains relevance of the last question to the recommendation
- **Product questions** — "Does this have Thunderbolt?", "How much VRAM does it have?"
- **Spec explanations** — "What is refresh rate?", "What does OLED mean?"
- **Policy questions** — warranty, returns, shipping (via knowledge base / RAG)

After answering, the QA agent hands back to wherever the main flow was interrupted.

---

## Product Database

`data/laptops.db` — SQLite, 28 laptops, 84 columns.

| Category | Count | Price range (CHF) |
|---|---|---|
| MacBook | 6 | 1 299 – 3 999 |
| Everyday / Work | 12 | 599 – 1 999 |
| Gaming | 10 | 849 – 4 299 |

Key filterable columns: `price_chf`, `category`, `gaming_tier`, `weight_kg`, `battery_life_hours`, `ram_gb`, `npu_tops`, `display_panel_type`, `gpu_model`, `gpu_tgp_w`.

Use-case filtering via `laptop_use_cases` junction table (198 rows).

Rebuild DB at any time:
```bash
python data/init_db.py
```

---

## Tech Stack

| Component | Technology |
|---|---|
| NLU / intake | Rasa (slot-filling forms, intents, entities) |
| Agent orchestration | LangGraph |
| LLM API | OpenRouter |
| Conversation tracing | LangSmith |
| Product database | SQLite (`laptops.db`) |
| Frontend — web | Streamlit |
| Frontend — chat | Telegram Bot |

---

## Project Structure (target)

```
dialogsystem-projekt_FHNW/
├── rasa_bot/                    # Rasa intake layer
│   ├── domain.yml               # Intents, slots, responses
│   ├── config.yml               # NLU pipeline and policies
│   ├── data/
│   │   ├── nlu.yml              # Training examples
│   │   ├── stories.yml
│   │   └── rules.yml
│   └── actions/
│       └── actions.py           # Webhook: triggers LangGraph pipeline
├── agents/                      # LangGraph pipeline
│   ├── graph.py                 # Graph definition and stage wiring
│   ├── router.py                # Routes Rasa payload to expert agent
│   ├── uni_agent.py
│   ├── gaming_agent.py
│   ├── professional_agent.py
│   ├── office_agent.py
│   ├── search_agent.py          # Queries laptops.db
│   ├── suggestion_agent.py      # Generates recommendation text
│   └── qa_agent.py              # Always-on QA / interruption handler
├── data/
│   ├── laptops.sql              # Source schema + data
│   ├── laptops.db               # Compiled SQLite database
│   ├── init_db.py               # Rebuilds laptops.db from laptops.sql
│   └── policies.md              # Store policies for RAG (QA agent)
├── frontend/
│   ├── streamlit_app.py
│   └── telegram_bot.py
├── test-chat.py                 # API connection test only
├── requirements.txt
└── .env.example
```

---

## Implementation Roadmap

| Phase | Scope | Status |
|---|---|---|
| 1 | Infrastructure: API connections, LangSmith tracing | Done |
| 2 | Product database: schema, 28 laptops, SQLite | Done |
| 3 | Rasa NLU: intents, slot forms, handoff webhook | Next |
| 4 | LangGraph pipeline: router + 4 expert agents | Planned |
| 5 | Search agent + suggestion agent | Planned |
| 6 | QA agent (always-on interruption handler) | Planned |
| 7 | Frontend: Streamlit + Telegram | Planned |
