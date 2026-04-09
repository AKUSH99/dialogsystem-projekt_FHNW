cre
# LLM.md – Buy-Bot Project Reference

This document provides a comprehensive overview of the Buy-Bot project for AI assistants and CLI tools. Read this first to understand the project context, architecture, and codebase.

---

## 📌 Project Overview

**Buy-Bot** is an intelligent laptop purchasing advisor chatbot designed for an e-commerce platform. It guides customers without technical knowledge through the laptop selection process using conversational AI.

### Core Problem Statement
- High cart abandonment rates due to customer uncertainty
- High return rates from mismatched purchases
- Customers overwhelmed by technical specs (RAM, CPU, GPU, etc.)
- Lack of personalized guidance in e-commerce

### Solution
Buy-Bot provides:
- Friendly, personalized laptop recommendations
- Questions focused on lifestyle and use case (not specs)
- 2-4 tailored options per customer
- Transparent pricing and trade-off explanations
- Simple language, never technical jargon

---

## 🤖 Bot Personality & Behavior

### Buy-Bot Persona
| Attribute | Value |
|-----------|-------|
| **Name** | Buy-Bot |
| **Personality** | Optimistic, sales-oriented, friendly, proactive |
| **Tone** | Professional with light charm |
| **Mission** | "Buying should feel like investing in happiness, not just spending" |
| **Language** | Simple, accessible, non-technical |
| **Focus** | Lifestyle and use cases, NOT technical specs |

### Core Behaviors
1. Greet warmly and establish rapport
2. Ask targeted questions about:
   - Budget constraints
   - Primary use case (study, work, gaming, entertainment)
   - Portability/mobility needs
   - Gaming/performance requirements
   - Personal preferences
3. Make 2-4 recommendations with clear reasoning
4. Explain trade-offs transparently
5. Motivate the customer to purchase

### Conversation Guidelines
- **Never use jargon** - Avoid "RAM", "CPU", "DDR5", "GPU", "Hz"
- **Use lifestyle language** - "Great for Netflix and browsing", "Handles gaming smoothly"
- **Be transparent** - Always explain price differences and trade-offs
- **Ask clarifying questions** - Don't assume; validate understanding
- **Keep responses concise** - Engaging brevity over lengthy explanations
- **Be sales-oriented** - Motivate the customer, don't just inform

---

## 👥 User Personas

### Persona 1: Laura Müller (Student, Age 23)
- **Goal**: Light everyday laptop for uni + Netflix
- **Budget**: ~800 CHF
- **Challenge**: Overwhelmed by filters and specs
- **Desire**: Clear human-language advice, confidence in choice
- **Key Need**: Portability + daily reliability

### Persona 2: Maca Damian (Student, Age 18)
- **Goal**: Laptop for uni + gaming (CS:GO, League of Legends)
- **Budget**: ~900 CHF
- **Challenge**: Limited budget, time-constrained
- **Desire**: Youth-appropriate language, interactive decisions
- **Key Need**: Gaming performance + affordability

**Impact**: Design dialogs and system prompt to address both personas equally.

---

## 📁 Project File Structure

```
dialogsystem-projekt_FHNW/
├── README.md              # Project overview, personas, example dialogs
├── SETUP.md               # Installation guide for testing
├── LLM.md                 # THIS FILE - AI assistant project reference
├── CHANGELOG.md           # Development log of completed work
├── test-chat.py           # TEST FILE ONLY - Tests API connections (not actual implementation)
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore             # Git exclusions
├── .git/                  # Version control
├── .venv/                 # Python virtual environment
└── .idea/                 # IDE configuration (JetBrains)
```

### File Purposes

| File | Purpose |
|------|---------|
| `README.md` | Full project definition, personas, example dialogs, grading criteria |
| `SETUP.md` | How to install, configure, and run the test file |
| `LLM.md` | AI/CLI reference guide for understanding the project |
| `test-chat.py` | **TEST FILE ONLY** - Tests OpenRouter API, LangSmith tracing, and LangGraph basics (not the actual project implementation) |
| `requirements.txt` | Python package dependencies |
| `.env.example` | Template for API credentials (OpenRouter, LangSmith) |

---

## 🏗️ Architecture & Technology Stack

### Core Technology Stack
- **Framework**: LangGraph (LangChain orchestration framework)
- **LLM Provider**: OpenRouter (aggregates open-source and commercial models)
- **LLM Models**: Llama 2 70B (free), Mistral, GPT-3.5 Turbo (available)
- **Tracing**: LangSmith (conversation logging, debugging, analytics)
- **Safety**: Input safeguards (content filtering)
- **Language**: Python 3.10+

### Test File Architecture Diagram (test-chat.py)

**Note**: This diagram shows the test file structure, not the actual Buy-Bot implementation.

```
┌─────────────────────────────────────────────────────────┐
│                    User Input (CLI)                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│          Safeguard Filter (safeguard_input)             │
│  - Blocks unsafe keywords (illegal, hack, abuse, etc.)  │
│  - Checks message length (< 5000 chars)                 │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│       LangGraph State Management (State class)          │
│  - Maintains message history (messages list)            │
│  - Uses add_messages reducer for concatenation          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│           Chat Node (chat_node function)                │
│  - Tests basic LLM integration                          │
│  - Calls OpenRouter API                                 │
│  - Returns response                                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│        LangSmith Tracing (Automatic)                    │
│  - Logs all inputs, outputs, latency, tokens            │
│  - Accessible via smith.langchain.com dashboard         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Bot Response (CLI)                    │
└─────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. System Prompt (SYSTEM_PROMPT constant)
- Defines Buy-Bot's personality and guidelines
- Instructs the LLM on conversation style and goals
- Emphasizes simple language and lifestyle focus
- Located in `test-chat.py` lines ~22-49

#### 2. State Class (State TypedDict)
- Holds conversation history as list of messages
- Uses LangGraph's `add_messages` reducer for proper merging
- Maintains full context across turns

#### 3. Safeguard Function (safeguard_input)
- Validates user input before LLM processing
- Blocks ~10 unsafe keywords
- Rejects messages > 5000 characters
- Returns tuple: (is_safe: bool, reason: str)

#### 4. Chat Node (chat_node function)
- Central processing node in the LangGraph
- Initializes OpenRouter ChatOpenAI client
- Injects system prompt
- Calls LLM and returns response
- Parameters:
  - **model**: `openrouter/meta-llama/llama-2-70b-chat`
  - **temperature**: 0.7 (moderate creativity)
  - **max_tokens**: 500 (concise responses)

#### 5. Graph Building (build_graph function)
- Creates StateGraph with State as schema
- Adds chat_node
- Connects START → chat → END
- Compiles into runnable graph

---

## 🔑 API Keys & Configuration

### Required Environment Variables

```env
# OpenRouter API Key (REQUIRED)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# LangSmith Configuration (OPTIONAL but recommended)
LANGSMITH_API_KEY=ls_xxxxxxxxxxxxx
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=buy-bot
```

### Where to Get Keys

| Service | URL | Steps |
|---------|-----|-------|
| OpenRouter | https://openrouter.ai | Sign up → Keys section → Create key |
| LangSmith | https://smith.langchain.com | Sign up → Settings → API Keys → Create key |

### LangSmith Tracing
- **Automatic**: Enabled by environment variables, no code changes needed
- **Dashboard**: Visit smith.langchain.com after running chatbot
- **Project**: Traces grouped under project name "buy-bot"
- **Benefits**: Debug conversations, analyze latency, track token usage

---

## 🚀 Testing API Connections

> **Important**: This section describes how to run `test-chat.py`, which is a TEST FILE ONLY for verifying API connections. It does NOT represent the actual Buy-Bot implementation.

### Installation
```bash
# Activate venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure .env
cp .env .env
# Edit .env with your OPENROUTER_API_KEY
```

### Running the Test
```bash
python test-chat.py
```

### Test Output
```
========================================================
Buy-Bot Chatbot - Testing API Connections
========================================================
Type 'quit' to exit

You: Hello
Bot: [Response from OpenRouter LLM]
...
```

**This tests**:
- OpenRouter API connectivity
- LangSmith tracing setup
- LangGraph state management
- Basic safeguard functionality

---

## 💡 Example Conversation Flow

### Laura Müller Scenario (Student)
```
Bot: Hello! I'm Buy-Bot. What's your budget for a laptop?
User: Around 800 CHF
Bot: Nice! What's the main use case - study, work, gaming, or a mix?
User: Study and watching Netflix
Bot: Perfect! Do you carry it around daily, like to lectures and cafes?
User: Yes, portability matters
Bot: Got it! Do you need gaming performance, or is everyday smoothness enough?
User: Just everyday use, no gaming
Bot: I'd recommend a lightweight 14-15" everyday laptop. Great for battery life, 
     video streaming, and daily tasks. Here are my top picks:
     [Recommendation with brief explanation]
```

---

## 🛡️ Safety & Guardrails

### Input Filtering (safeguard_input)
**Blocks**: illegal, hack, crack, malware, virus, abuse, hate, violence, kill, bomb

**Characteristics**:
- Case-insensitive keyword matching
- Message length limit: 5000 characters
- Prevents spam and malicious prompts

**Response on Block**:
```
Buy-Bot: I can't respond to that. Message contains unsafe content: [keyword]
```

### Best Practices
- Never remove or weaken safeguards without explicit user approval
- Document any new safeguard rules added
- Test safeguards before deployment
- Monitor LangSmith traces for attempted attacks

---

## 🧪 Testing & Debugging (test-chat.py)

> **Note**: This section describes testing the `test-chat.py` file, which is for API connection testing only. It does NOT represent the actual Buy-Bot implementation.

### Testing API Connections
1. Run `python test-chat.py`
2. Type test inputs
3. Verify responses are generated
4. Check LangSmith traces appear in dashboard

### LangSmith Trace Debugging
1. Go to https://smith.langchain.com/projects/buy-bot
2. Click on any trace to view:
   - Input (user message)
   - Output (LLM response)
   - Latency
   - Token usage
   - API errors (if any)

### Common Connection Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "OPENROUTER_API_KEY not found" | Missing .env or key not set | Create .env with valid API key |
| "API key is invalid" | Wrong OpenRouter key | Get key from https://openrouter.ai/keys |
| No traces in LangSmith | LANGSMITH_API_KEY wrong or missing | Get key from https://smith.langchain.com |
| Connection timeout | Network issue or API overload | Check internet, try again later |
| Empty responses | LLM issue | Check OpenRouter status page |

---

## 📊 Test File Verification Checklist

When testing `test-chat.py`, verify:

- [ ] OpenRouter API key is valid and working
- [ ] LangSmith tracing is enabled
- [ ] Traces appear in LangSmith dashboard
- [ ] Safeguards are active (test with "hack", "illegal", etc.)
- [ ] Message history is captured correctly
- [ ] LLM responses are generated without errors
- [ ] API connection is stable
- [ ] No authentication errors appear
- [ ] Response latency is acceptable

---

## 🔧 Test File Customization (test-chat.py only)

> **Note**: These customizations are for the test file only, to test different configurations.

### Test Different System Prompts
Edit `SYSTEM_PROMPT` in `test-chat.py` to test various prompts (this is NOT for the actual project implementation).

### Test Different Safeguard Rules
Extend `safeguard_input()` function to test new safety rules:
```python
def safeguard_input(message: str) -> tuple[bool, str]:
    # Add test rules here
    if some_condition:
        return False, "reason"
    return True, ""
```

### Test Different LLM Models
Replace in `chat_node()`:
```python
llm = ChatOpenAI(
    model="openrouter/mistralai/mistral-7b-instruct",  # ← Test different models
    ...
)
```

### Test Different Generation Parameters
```python
ChatOpenAI(
    temperature=0.5,      # ← Test different values
    max_tokens=1000,      # ← Test response length
    top_p=0.9,           # ← Test sampling
    ...
)
```

---

## 📋 Project Context

### Grading Criteria (FHNW Module)
| Criterion | Weight | Focus |
|-----------|--------|-------|
| Define, UX, Personas | 10% | User research, domain understanding |
| Conversational Design | 25% | Natural dialogs, clear flow |
| Architecture & Info Need | 10% | System design, API integration |
| Build, Release, Operate | 20% | NLU/LLM use, working system |
| Overall & Artifacts | 20% | Complete documentation |
| Presentation | 15% | Demo quality, clarity |

### Team
- Almidin Bangoji (Collaborator)
- Vaagisan Vadivel (Collaborator)
- Damian Martin (Collaborator)

### Related Artifacts
- [Conversational AI Canvas (Miro)](https://miro.com/app/board/uXjVG2xTs8c=/)
- [GitHub Repository](https://github.com/AKUSH99/dialogsystem-projekt_FHNW)

---

## 🎓 Key Concepts for AI Assistants

### System Prompt Injection
The `SYSTEM_PROMPT` is the source of truth for Buy-Bot behavior. It should:
- Never be weakened or made generic
- Always maintain the lifestyle/UX focus
- Prevent users from jailbreaking into other personas
- Be tested against the README example dialogs

### Message History Management
LangGraph's `add_messages` reducer:
- Automatically concatenates messages
- Prevents duplicate message IDs
- Maintains proper conversation context
- Required for stateful conversations

### Token Economy
- **max_tokens=500**: Keeps responses concise and cost-effective
- **temperature=0.7**: Balances creativity (persona) with consistency (recommendations)
- Monitor LangSmith for token usage trends

### Safeguard Philosophy
- **Defensive**, not paranoid: Filter clear threats, don't over-filter
- **Transparent**: Tell user why message was blocked
- **Evolving**: Add rules based on real attack patterns
- **Tested**: Always verify safeguards don't break legitimate use

---

## 📚 References

- **README.md**: Full project definition, personas, example dialogs
- **SETUP.md**: Installation and configuration guide
- **test-chat.py**: Implementation details and code comments
- **LangGraph Docs**: https://langgraph.dev
- **OpenRouter Docs**: https://openrouter.ai/docs
- **LangSmith Docs**: https://docs.smith.langchain.com

---

## ✅ Checklist for Working with This Project

Before making changes:
1. Read this LLM.md file completely
2. Review the README.md for personas and example dialogs
3. Check the current SYSTEM_PROMPT in test-chat.py
4. Review safeguard_input() function for context
5. Understand how LangGraph State works
6. Verify API keys are configured in .env

When implementing features:
1. Validate against README personas and dialogs
2. Test system prompt changes against example flows
3. Ensure all responses avoid technical jargon
4. Run chatbot locally and test interactions
5. Check LangSmith traces for quality
6. Document any architectural changes

---

**Version**: 1.0
**Last Updated**: 2026-04-09
**Maintained by**: Buy-Bot Development Team
