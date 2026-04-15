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

### File Cleanup & Organization
- ✅ Removed all redundancy from README.md, ARCHITECTURE.md, LLM.md
- ✅ README.md: Personas, example dialogs, problem/solution (human-friendly)
- ✅ ARCHITECTURE.md: Pure technical design (Rasa, agents, database schema)
- ✅ LLM.md: Navigation guide for AI assistants (links to other files)
- ✅ Each file is now specialized with no duplication
- ✅ Cross-file references to prevent copy-paste content

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

## Current Status
🟢 **Infrastructure ready — API connections and LangSmith tracing verified**
🟢 **Product database complete — 28 laptops, normalized 7-table SQLite schema**
🟢 **Architecture documented — 6-stage pipeline with 4 expert agents**
🟢 **Architecture diagrams complete — SVGs in docs/**
🔵 **Next: Rasa NLU — intents, slot forms, handoff webhook**
🔵 **Then: LangGraph pipeline — router + expert agents + search + suggestion + QA**
🔵 **Then: Frontend — Streamlit + Telegram**

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
