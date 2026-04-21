# CHANGELOG – Development Log

Simple log of completed work on Buy-Bot project.

---

## 2026-04-09

### Created Files
- ✅ `test-chat.py` - **TEST FILE ONLY** - Tests OpenRouter API, LangSmith tracing, LangGraph basics (NOT the actual Buy-Bot implementation)
- ✅ `requirements.txt` - Python dependencies (LangGraph, LangChain, LangSmith)
- ✅ `.env.example` - Environment variable template for API keys
- ✅ `SETUP.md` - Installation and testing guide
- ✅ `LLM.md` - AI assistant project reference guide
- ✅ `CHANGELOG.md` - This development log

### Fixes
- ✅ Updated `requirements.txt` with correct package versions (langgraph 0.2.54, langchain-core 0.3.0, langchain-openai 0.2.0, langsmith 0.2.0)
- ✅ Fixed `test-chat.py` - Removed LangGraph StateGraph and simplified to direct LLM invocation with message history
- ✅ Added `.env` file loading with `python-dotenv`
- ✅ Improved error handling for API calls and safeguards
- ✅ Added feedback messages for API initialization and errors

### Test Features Created
- ✅ LangGraph state machine pattern demonstration
- ✅ OpenRouter API integration example
- ✅ System prompt pattern example
- ✅ Input safeguards demonstration
- ✅ LangSmith tracing setup example
- ✅ Interactive CLI interface for testing
- ✅ Message history management pattern

### Documentation Completed
- ✅ Project context and personas
- ✅ Testing and setup instructions
- ✅ AI assistant reference guide
- ✅ Clear distinction: test-chat.py is NOT the actual implementation

---

### Architecture Documentation
- ✅ Created `ARCHITECTURE.md` - Comprehensive guide to Rasa + LangGraph agents
- ✅ Documented intended architecture: **Rasa NLU + LangGraph Agents**
- ✅ Explained two-stage approach:
  - Stage 1: Rasa extracts intent (budget, use case, mobility, etc.)
  - Stage 2: LangGraph routes to specialized agents (Uni, Gaming, Work)
- ✅ Detailed each agent type (Uni, Gaming, Work) with flows
- ✅ Created product database schema design
- ✅ Provided implementation roadmap (6 phases)
- ✅ Clarified test-chat.py is infrastructure testing only
- ✅ Updated README.md with architecture diagrams
- ✅ Updated LLM.md with Rasa + agents explanation

### Design Clarifications
- ✅ Budget is float value (e.g., 800.0, 1500.0) - NOT translated to low/medium/high
- ✅ Budget extracted directly by Rasa as numeric entity
- ✅ Frontend channels: **Streamlit app** + **Telegram bot** only
- ✅ No session management or feedback collection needed (simple interfaces)
- ✅ Updated product matching algorithm to use 20% budget margin
- ✅ Updated training data examples for budget extraction
- ✅ Updated architecture roadmap (Phase 6: Streamlit + Telegram only)

### Rasa + LangGraph Structure
- ✅ Updated requirements.txt with Rasa 3.6.21 + rasa-sdk 3.6.2
- ✅ Documented Rasa project structure:
  - `rasa_bot/domain.yml` – Intents, entities, slots, responses
  - `rasa_bot/config.yml` – NLU pipeline configuration
  - `rasa_bot/data/nlu.yml` – Training examples (EN + DE)
  - `rasa_bot/data/stories.yml` – Dialogue flows
  - `rasa_bot/data/rules.yml` – Conversation rules
  - `rasa_bot/actions/actions.py` – Custom Python actions
- ✅ Documented LangGraph agent files:
  - `langgraph_agents/graph.py` – Main orchestration
  - `langgraph_agents/agents/router.py` – Question classifier
  - `langgraph_agents/agents/product_expert.py` – Product Q&A
  - `langgraph_agents/agents/comparator.py` – Comparison
  - `langgraph_agents/agents/advisor.py` – General advice
  - `langgraph_agents/agents/rag_agent.py` – Policy Q&A (RAG)
- ✅ Documented data files:
  - `data/laptops.json` – 12 laptop options
  - `data/policies.md` – Store policies

### File Cleanup & Organization
- ✅ Removed all redundancy from README.md, ARCHITECTURE.md, LLM.md
- ✅ README.md: Personas, example dialogs, problem/solution + links to structure
- ✅ ARCHITECTURE.md: Pure technical design with file references
- ✅ SETUP.md: Installation, Rasa training, action server startup
- ✅ LLM.md: Complete file guide with all Rasa and LangGraph agents
- ✅ Cross-file references prevent duplication

## 2026-04-15

### Created Files
- ✅ `data/laptops.sql` — 84-column SQLite schema + full data for 28 laptops (6 MacBook, 12 everyday/work, 10 gaming); CHF retail prices 2024–2025; no marketing text — all factual specs
- ✅ `data/init_db.py` — builds `data/laptops.db` from `laptops.sql`; deletes existing DB, runs script, prints sanity-check counts
- ✅ `data/laptops.db` — compiled SQLite database (generated artifact, not committed)

### Database Coverage
- **MacBooks (laptop_001–006):** MacBook Air 13"/15" M4 (2025), MacBook Pro 14" M4 / M4 Pro, MacBook Pro 16" M4 Pro / M4 Max — CHF 1 299–3 999
- **Everyday/Work (laptop_007–018):** Acer Aspire 3, Lenovo IdeaPad Slim 3, HP 15s-fq5, Asus VivoBook 15 OLED, Dell Inspiron 15, Lenovo ThinkPad E16, Microsoft Surface Laptop 7 (Snapdragon X Elite), Asus Zenbook 14 OLED, Dell XPS 13, Lenovo Yoga 7i, HP EliteBook 845 G11, Asus ProArt Studiobook 16 OLED — CHF 599–1 999
- **Gaming (laptop_019–028):** Lenovo IdeaPad Gaming 3 (RTX 4050), Acer Nitro 16 (RTX 4060), HP Victus 16, Asus TUF A16 (RTX 4070), MSI Thin 15, Lenovo Legion 5i Pro, Asus ROG Zephyrus G16 (RTX 5080), Razer Blade 16 (RTX 5090), MSI Titan GT77 (RTX 4090), Asus ROG Strix SCAR 18 (RTX 5090) — CHF 849–4 299

### Schema Highlights
- CPU: brand, model, architecture (Zen 5 / Arrow Lake-HX / Apple M4 ARM), cores, threads, base/boost GHz, TDP
- GPU: type (integrated/dedicated), model, architecture (Ada Lovelace / Blackwell / RDNA 3.5), VRAM GB, TGP watts
- Display: resolution, refresh Hz, panel type (OLED / Mini-LED / IPS), nits, peak nits, sRGB%, DCI-P3%, HDR cert, VRR, aspect ratio
- Connectivity: Thunderbolt version (3/4/5 or NULL for USB4-only), per-port counts, Wi-Fi standard, BT version
- AI/NPU: `npu_tops` column (Copilot+ PC threshold = 40 TOPS)
- Scores: value, performance, portability, build quality, display (1–10)
- `laptop_use_cases` junction table: 198 rows mapping laptops to use-case tags

---

### Architecture Redesign
- Deleted old `rasa_bot/` and `langgraph_agents/` scaffolds (clean slate)
- Deleted `data/laptops.json` (replaced by SQLite)
- Redesigned to 6-stage pipeline: Rasa intake → Router LLM → 4 Expert Agents → Search Agent → Suggestion Agent + always-on QA Agent
- Added Professional Agent and Private/Office Agent (was 3 agents, now 4)
- Language adaptation: suggestion agent calibrates jargon level from user_profile (no fixed register)
- Updated ARCHITECTURE.md, README.md, LLM.md, SETUP.md to reflect new design

### Architecture Diagrams
- ✅ `docs/architecture.svg` — System Architecture diagram: full component view (user → Rasa → Router → 4 Expert Agents → Search → Suggestion), QA Agent as always-on right column, DB and LangSmith blocks, color-coded by layer with legend
- ✅ `docs/pipeline.svg` — Pipeline + DB Flow diagram: numbered stage-by-stage flow with exact payload labels on arrows, DB table structure with example rows and filter columns shown at Stage 4, user_profile dict shown growing through stages, QA Agent intercept note
- ✅ `docs/database.svg` — Database Schema diagram: full column listing for both tables color-coded by group (CPU / GPU / Memory / Storage / Display / Battery / Connectivity / Build / Scores), FK relationship, all 9 indexes, data summary (28 rows, price ranges per category), legend

## 2026-04-15 (continued)

### Database Normalized
- Replaced flat 84-column single-table schema with 6-table normalized design
- `data/build_sql.py` — Python generator script that produces `data/laptops.sql` from structured data lists; handles SQL quoting via `q()` helper
- New tables: `cpu_specs` (20 rows, 9 cols), `gpu_specs` (18 rows, 5 cols), `display_specs` (21 rows, 15 cols), `ram_specs` (16 rows, 7 cols), `storage_specs` (12 rows, 6 cols)
- `laptops` table: 52 columns (down from 84) — component specs replaced by FK references; `gpu_tgp_w` kept in `laptops` as it is a per-laptop power configuration, not a GPU property
- 15 indexes total across all tables for fast chatbot queries
- Verified clean build: all 28 laptops, 198 use-case rows, correct FK relationships

### Diagrams Updated
- `docs/database.svg` — redrawn to show all 7 tables with FK relationship arrows, column listings color-coded by table, index summary, legend

## 2026-04-17

### Architecture Pivot — Rasa dropped, full LangGraph pipeline built

Dropped Rasa NLU entirely. Rasa requires a separate training/server process and does not handle open-ended conversation well. Replaced with an LLM-based intake agent that extracts slots from free-form conversation and returns structured JSON. Simpler, no training step, handles edge cases ("I want apple", "800 to 1000 CHF") out of the box.

### Created Files

- `agents/__init__.py` — package marker
- `agents/state.py` — `BuyBotState` (Pydantic BaseModel); all fields typed and validated; budget coerces strings to float; messages use `Annotated[list, operator.add]` for LangGraph append semantics
- `agents/prompts.py` — all LLM prompts in one file: `BUYBOT_SYSTEM_PROMPT` (global persona, language rules, no-emoji rule) + 6 role prompts (intake, router, uni, gaming, professional, office, search, suggestion, QA)
- `agents/intake_agent.py` — `IntakeAgent`; collects 4 slots via natural conversation; manual JSON parsing (no `with_structured_output`) because free OpenRouter models don't support tool calling
- `agents/router.py` — `Router`; no LLM call, reads `use_case` from state and returns next node name; `ROUTES` dict maps use_case → agent node name
- `agents/expert_agents.py` — `BaseExpertAgent` + 4 subclasses (`UniAgent`, `GamingAgent`, `ProfessionalAgent`, `OfficeAgent`); shared logic in base class, only role prompt differs per agent; merges LLM-returned `user_profile_update` into state on each turn
- `agents/search_agent.py` — `SearchAgent`; two-step approach: SQL filters hard constraints (budget ±20%, OS, use-case tags via junction table, weight < 2 kg for high mobility), then LLM ranks candidates and picks primary + alternative; USE_CASE_TAGS and OS_FILTER mappings centralised at top of file
- `agents/suggestion_agent.py` — `SuggestionAgent`; plain-text LLM output (no JSON); connects specs to user's actual needs; handles no-results edge case with actionable suggestions
- `main.py` — sequential pipeline runner for CLI testing; `run_intake()` and `run_expert()` loops; prints stage headers and slot summaries between stages; not the LangGraph graph wiring (that is `graph.py`, not yet built)
- `CLAUDE.md` — project instructions for Claude Code: architecture, build order, coding standards, env setup
- `vaagi_thought.md` — design rationale document

### Key Design Decisions

- **BuyBotState as Pydantic BaseModel** instead of TypedDict — runtime validation catches bad values immediately
- **Manual JSON parsing** in all agents — more portable across free-tier OpenRouter models that lack tool-calling
- **Two-step search** (SQL + LLM ranking) — SQL handles exact constraints reliably; LLM handles nuanced trade-offs
- **Single `BUYBOT_SYSTEM_PROMPT`** for all agents — change personality once, applies everywhere

### Bugs Fixed

- Language detection in `SuggestionAgent`: LLM was defaulting to German (Swiss university context) because `state.messages` was not passed to the invoke call. Fixed by passing `[system_message, *state.messages, final_instruction]` so the LLM sees the full English conversation.
- Emojis in bot output: added `- Never use emojis` to `BUYBOT_SYSTEM_PROMPT`; rule now applies to all agents from one place.

---

## 2026-04-17 (continued)

### Pipeline improvements

- **Language selection**: added `language` as a first intake slot. Bot now opens with a bilingual question ("English or German? / Englisch oder Deutsch?") and all downstream agents receive the chosen language explicitly in their system prompt. Added `language` field to `BuyBotState`, `IntakeResponse`, slot tracking, `is_complete`, and JSON format.
- **UniAgent questions**: rewrote `UNI_AGENT_ROLE` to ask about field of study first (determines hardware needs more than anything else), then let the conversation flow naturally based on what the user reveals. Removed rigid numbered list — agent now uses judgment to skip questions whose answers are already obvious.
- **Language bug fix**: `SuggestionAgent` was defaulting to German because it didn't pass `state.messages` to the LLM. Fixed by invoking with `[system_message, *state.messages, final_instruction]`.
- **Emoji fix**: added `- Never use emojis` to `BUYBOT_SYSTEM_PROMPT` — applies to all agents from one place.
- **Off-topic and NSFW guardrail**: added global rule to `BUYBOT_SYSTEM_PROMPT` restricting Buy-Bot to laptop purchasing only.

### Created Files

- `agents/qa_agent.py` — `QAAgent`; three responsibilities: `classify_message()` (three-way: `on_script` / `qa` / `off_topic`), `run()` (answers laptop-related off-script questions, plain text, does not change `current_stage`), `handle_off_topic()` (hardcoded refusal — NSFW/unrelated content is never forwarded to the LLM).
- `agents/graph.py` — full LangGraph `StateGraph` wiring; `build_graph(llm)` returns a compiled graph with `MemorySaver` checkpointer; dispatch conditional edge from START classifies every incoming message and routes to the correct agent; intake and expert agents chain automatically when their stage completes (same turn); search → suggestion always sequential; QA and off-topic intercept without changing `current_stage` so the pipeline resumes correctly.

### Key Design Decisions

- **Three-way message classifier** (`ON_SCRIPT` / `QA` / `OFF_TOPIC`) — separate routing for laptop questions vs completely unrelated content; off-topic never reaches the LLM for a response
- **Hardcoded off-topic refusals** — one string per language, no LLM call; avoids feeding harmful content into the model
- **`current_stage` never touched by QA/off-topic nodes** — graph routes back to the interrupted stage automatically on the next turn
- **`main.py` updated to run through the graph** — now tests dispatch, conditional edges, QA interception, and off-topic rejection; previous version was a sequential runner that bypassed all graph logic

---

## 2026-04-17 (continued)

### Created Files

- `frontend/app.py` — Streamlit chat frontend; `@st.cache_resource` builds the graph once per server process; per-session state (session ID, message history, done flag) lives in `st.session_state`; spinner shown while the bot thinks; "New conversation" button in sidebar resets session; input disabled once pipeline is done. Run with `streamlit run frontend/app.py` from the project root.

### Improvements

- **QA classifier accuracy**: classifier was failing on short answers like "uni" because it only saw the user's message in isolation. Fixed by passing the bot's last question alongside the user's reply (`"Bot: ...\nUser: ..."`) and adding concrete examples to the prompt covering exactly these cases.
- **Two-model architecture (structure ready)**: `build_graph()` now accepts `llm_fast` and `llm_strong` separately. Fast model → intake, expert agents, classifier. Strong model → QA answers, search ranking, suggestion. Both currently point to the same model — swap `llm_fast` to a smaller model in `main.py` and `frontend/app.py` (one line each, marked with `TODO`).
- **`max_tokens` tuned per model**: `llm_fast` uses 500 tokens (slot extraction needs less), `llm_strong` uses 1000 (recommendation needs more).

### Key Design Decisions

- **Two models, not one** — quality where it matters (recommendation, QA), speed everywhere else
- **Classifier gets conversation context** — bot question + user reply, not just the user reply alone; short answers are always ambiguous without knowing what was asked
- **Graph-backed `main.py`** — CLI runner now goes through the real LangGraph graph, not a hand-rolled sequential loop; tests dispatch, QA interception, and off-topic rejection

---

## 2026-04-21

### Created Files

- `model_config.py` — central model configuration; defines `MODEL_FAST`, `MODEL_STRONG`, `MODEL_FALLBACK` and their token limits and temperatures; both CLI and Streamlit import from here so swapping a model requires editing one file only
- `agents/llm_builder.py` — `ModelWithFallback` class + `build_llms()` function; single source of truth for LLM construction shared by `main.py` and `frontend/app.py`

### Features Implemented

- **Model config file**: all model names, token limits, and temperatures moved out of `main.py` / `frontend/app.py` into `model_config.py`; separate temperature per model (`TEMPERATURE_FAST = 0.3`, `TEMPERATURE_STRONG = 0.7`, `TEMPERATURE_FALLBACK = 0.5`)
- **Automatic fallback model**: `ModelWithFallback` wraps any primary LLM with a fallback; if the primary fails (rate limit, outage, timeout), the call is transparently retried on the fallback and a `[fallback]` line is printed to the terminal; explicit `try/except` rather than LangChain's `with_fallbacks()` so both primary and fallback errors are reported independently

### Refactoring

- `main.py` — removed inline `build_llms()` and all model-config imports; now imports `build_llms` from `agents.llm_builder`
- `frontend/app.py` — removed inline LLM construction block from `get_graph()`; now calls `build_llms()` from `agents.llm_builder`; removed `ChatOpenAI`, `load_dotenv`, and model-config imports

### Key Design Decisions

- **One file to change models** — `model_config.py` is the only file that needs editing when swapping models; neither runner file needs to be touched
- **Explicit fallback over LangChain's `with_fallbacks()`** — `with_fallbacks()` re-raises the primary's error when the fallback also fails, masking whether the fallback was tried at all; `ModelWithFallback` reports each failure independently and always surfaces the fallback's error if it too fails
- **Fallback from a different provider** — fallback model (`nvidia/nemotron-3-super-120b-a12b:free`) intentionally runs on a different provider than the primary models to survive provider-level outages

---

## Current Status

🟢 **Infrastructure ready — API connections and LangSmith tracing verified**
🟢 **Product database complete — 28 laptops, normalized 7-table SQLite schema**
🟢 **Architecture documented — 6-stage pipeline with 4 expert agents**
🟢 **Architecture diagrams complete — SVGs in docs/**
🟢 **Full LangGraph pipeline complete — all agents wired, graph compiled**
🟢 **Streamlit frontend live — `streamlit run frontend/app.py`**
🟢 **End-to-end testable via CLI (`python main.py`) and browser**
🟢 **Model config centralised — swap any model by editing `model_config.py` only**
🟢 **Automatic fallback model — rate limits and outages handled transparently**
🔵 **Next: LangSmith feedback logging at conversation end**

---

## How to Use This Log
Each AI assistant or team member should add their completed work here when they finish:

```
### YYYY-MM-DD

### Created Files
- ✅ `filename.py` - Description

### Features Implemented
- ✅ Feature name - Description

### Bugs Fixed
- ✅ Bug description - Solution

### Documentation Updated
- ✅ File - Changes made
```
