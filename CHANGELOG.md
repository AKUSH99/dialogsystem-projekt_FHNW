# CHANGELOG – Development Log

Simple log of completed work on Buy-Bot project.

---

## 2026-04-09 — Rasa + LangGraph Scaffold Implementation

### Created Files — Rasa Bot (`rasa_bot/`)
- ✅ `rasa_bot/domain.yml` — Intents, entities, slots, forms, responses, actions
- ✅ `rasa_bot/config.yml` — NLU pipeline (DIETClassifier, FallbackClassifier) and policies (Memoization, Rule, TED)
- ✅ `rasa_bot/endpoints.yml` — Action server endpoint (localhost:5055)
- ✅ `rasa_bot/credentials.yml` — REST and SocketIO channels
- ✅ `rasa_bot/data/nlu.yml` — Training data with 13 intents, 15+ examples each, EN + DE, entity annotations
- ✅ `rasa_bot/data/stories.yml` — Stories: Laura path, Maca path, free question mid-flow, comparison, guarantee, goodbye
- ✅ `rasa_bot/data/rules.yml` — Rules: greeting, goodbye, form activation/completion, LangGraph routing, fallback
- ✅ `rasa_bot/actions/__init__.py` — Empty init file
- ✅ `rasa_bot/actions/actions.py` — Custom actions: ValidateLaptopRecommendationForm, ActionRecommendLaptop, ActionCallLanggraph

### Created Files — LangGraph Agents (`langgraph_agents/`)
- ✅ `langgraph_agents/__init__.py` — Exports `run_buybot_graph`
- ✅ `langgraph_agents/graph.py` — LangGraph StateGraph with router → expert nodes pipeline
- ✅ `langgraph_agents/agents/__init__.py` — Empty init file
- ✅ `langgraph_agents/agents/_llm.py` — Shared OpenRouter LLM client with model fallback
- ✅ `langgraph_agents/agents/router.py` — Classifies questions into: product, comparison, guarantee, advisor
- ✅ `langgraph_agents/agents/product_expert.py` — Answers product questions using laptop DB context
- ✅ `langgraph_agents/agents/comparator.py` — Compares laptops in simple lifestyle language
- ✅ `langgraph_agents/agents/advisor.py` — General advice in simple, non-technical language
- ✅ `langgraph_agents/agents/rag_agent.py` — Policy Q&A with policies.md context (RAG placeholder)

### Created Files — Product Database (`data/`)
- ✅ `data/laptops.json` — 12 laptops: budget everyday (599–799 CHF), budget gaming (849–999 CHF), professional (1199–1299 CHF)
- ✅ `data/policies.md` — Store policies: warranty, returns, shipping (RAG knowledge base placeholder)

### Updated Files
- ✅ `requirements.txt` — Added rasa==3.6.20, rasa-sdk==3.6.2, requests==2.31.0
- ✅ `.env.example` — Created template with OPENROUTER_API_KEY, LANGSMITH_API_KEY, LANGSMITH_TRACING, LANGSMITH_PROJECT
- ✅ `README.md` — Updated architecture section with Rasa + LangGraph diagram and project structure
- ✅ `SETUP.md` — Full setup instructions: install, configure, train, run action server, run Rasa
- ✅ `CHANGELOG.md` — This entry

### Architecture Implemented
- Rasa handles structured dialogue via intents, entities, slots, and forms
- LangGraph "expert team" handles free-form/complex questions via 4 specialised agent nodes
- Graceful degradation: bot works standalone (without LangGraph) for basic flows
- All responses use simple lifestyle language — no technical jargon

---

## 2026-04-09 — Initial Setup

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

---

## Current Status
🟢 **Rasa + LangGraph scaffold complete — ready for team to build upon**
🟢 **Testing infrastructure ready — test-chat.py can verify API connections**

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
