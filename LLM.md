# LLM.md – Navigation Guide

Quick reference for AI assistants working on Buy-Bot.

---

## 📁 File Guide

| File | Purpose | Read If |
|------|---------|---------|
| **README.md** | Personas, example dialogs, problem/solution | Understanding the project context & user needs |
| **ARCHITECTURE.md** | Technical design, Rasa, agents, database | Implementing the system |
| **SETUP.md** | Installation, testing, dependencies | Setting up local environment |
| **CHANGELOG.md** | Development progress log | Tracking what's been done |
| **test-chat.py** | API connection test file | Testing OpenRouter + LangSmith integration |

---

## 🎯 Quick Start for AI Assistants

1. **Start here:** Read [README.md](README.md) for context
   - Personas (Laura, Maca)
   - Example dialogs
   - Bot personality
   - Problem/solution statement

2. **Then:** Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical design
   - Rasa NLU (intent extraction)
   - LangGraph agents (Uni, Gaming, Work)
   - Product database schema
   - Implementation roadmap

3. **Setup:** Follow [SETUP.md](SETUP.md) to install dependencies
   - Virtual environment
   - Requirements
   - Environment variables

4. **Track progress:** Check [CHANGELOG.md](CHANGELOG.md)
   - Completed work
   - Current status
   - Next steps

---

## 🔑 Key Concepts

### Two-Stage Architecture
1. **Rasa NLU** → Extracts: budget (float), use_case, mobility, performance
2. **LangGraph Agents** → Routes to: Uni Agent / Gaming Agent / Work Agent

### Budget Handling
- Extracted as **float** (e.g., 800.0, 1500.0)
- NOT translated to "low/medium/high"
- Used with 20% margin for product filtering (±20% from budget)

### Three Agent Types
| Agent | Optimized For | Key Attributes |
|-------|---------------|----------------|
| Uni Agent | Students | Lightweight, battery life, reliability |
| Gaming Agent | Gamers | GPU/CPU, refresh rate, performance |
| Work Agent | Professionals | Build quality, security, reliability |

### Frontend
- **Streamlit App** – Simple web interface for testing
- **Telegram Bot** – Chat-based access

---

## 📝 Important Implementation Details

### From README.md (Personas)
- **Laura:** Uni student, 800 CHF, needs light portable laptop
- **Maca:** Gaming student, 900 CHF, needs gaming performance

### From ARCHITECTURE.md (Technical)
- Rasa extracts entities into structured dict
- LangGraph routes based on intent
- Product matching uses 20% budget margin (budget * 0.8 to budget * 1.2)
- Each agent maintains conversation state with user_profile
- LangSmith logs all conversations automatically

### From test-chat.py (Infrastructure)
- Tests OpenRouter API connectivity
- Tests LangSmith tracing integration
- Demonstrates message history management
- Shows safeguard implementation

---

## 🚀 When to Reference Files

**Need to understand user needs?**
→ Read [README.md](README.md) personas and dialogs

**Need to implement Rasa NLU?**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md) Rasa section

**Need to build a LangGraph agent?**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md) Agent System section

**Need to understand the product database?**
→ Read [ARCHITECTURE.md](ARCHITECTURE.md) Product Database section

**Need to see example code?**
→ Check [test-chat.py](test-chat.py) for patterns

**Need to know what's done?**
→ Check [CHANGELOG.md](CHANGELOG.md)

---

## ⚠️ Key Constraints

✅ **Always keep:**
- Budget as float (800.0, not "low")
- 20% margin for product filtering
- Simple language (no technical jargon in Bot responses)
- 2-4 recommendations per conversation

❌ **Don't add:**
- Session management
- Feedback collection
- Complex authentication
- Advanced analytics

---

## 🔗 External Resources

- **LangGraph Docs:** https://langgraph.dev
- **Rasa Docs:** https://rasa.com/docs/
- **OpenRouter Docs:** https://openrouter.ai/docs
- **LangSmith Docs:** https://docs.smith.langchain.com

---

**Last Updated:** 2026-04-09  
**Status:** Active Development
