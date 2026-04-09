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

## Current Status
🟢 **Testing infrastructure ready - test-chat.py verifies API connections**
🟢 **Documentation complete and well-organized**
🔵 **Rasa + LangGraph agent implementation next**
🔵 **Product database and RAG integration needed**
🔵 **Streamlit + Telegram frontends to be built**

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
