# Buy-Bot Setup Guide

## Prerequisites

- Python 3.10+
- Virtual environment (venv)

---

## Quick Start — Rasa Buy-Bot

### 1. Activate Virtual Environment

```bash
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: Rasa requires Python 3.10. If you're using a newer Python version,
> consider using `pyenv` or a conda environment.

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Then edit `.env` with your API keys:

```
OPENROUTER_API_KEY=sk-or-v1-xxxxx
LANGSMITH_API_KEY=ls_xxxxx
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=buy-bot
```

### 4. Train the Rasa Model

```bash
cd rasa_bot
rasa train
```

This will generate a trained model in `rasa_bot/models/`. Training takes a few minutes.

### 5. Start the Action Server

Open a **new terminal** and run:

```bash
cd rasa_bot
rasa run actions
```

This starts the custom action server on port 5055 (required for recommendations and LangGraph integration).

### 6. Start the Rasa Server

Open another terminal and run:

```bash
cd rasa_bot
rasa run --cors "*"
```

Or, to chat directly in the terminal shell:

```bash
cd rasa_bot
rasa shell
```

---

## Project Structure

```
dialogsystem-projekt_FHNW/
├── rasa_bot/                    # Rasa dialogue manager
│   ├── domain.yml               # Intents, entities, slots, responses
│   ├── config.yml               # NLU pipeline and policies
│   ├── endpoints.yml            # Action server endpoint
│   ├── credentials.yml          # REST/SocketIO channels
│   ├── data/
│   │   ├── nlu.yml              # Training examples (EN + DE)
│   │   ├── stories.yml          # Dialogue stories
│   │   └── rules.yml            # Conversation rules
│   └── actions/
│       └── actions.py           # Custom actions (recommendation, LangGraph)
├── langgraph_agents/            # LangGraph expert team
│   ├── graph.py                 # Main graph definition
│   └── agents/
│       ├── router.py            # Question classifier
│       ├── product_expert.py    # Product Q&A agent
│       ├── comparator.py        # Laptop comparison agent
│       ├── advisor.py           # General advice agent
│       └── rag_agent.py         # Policy/guarantee agent (RAG placeholder)
├── data/
│   ├── laptops.json             # Product database (12 laptops)
│   └── policies.md              # Store policies (for RAG)
├── test-chat.py                 # TEST FILE: API connection test only
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment variable template
```

---

## Architecture

```
User Message
    │
    ▼
┌──────────────┐
│    RASA       │  Structured dialogue: intents, entities, forms
│  (NLU +       │
│  Dialogue)    │
└──────┬───────┘
       │
       │  If free/complex question detected:
       ▼
┌──────────────────────┐
│  Custom Action:       │
│  action_call_langgraph│ ──► LangGraph Agents
└──────────────────────┘
           │
           ├── router.py      → classifies the question
           ├── product_expert → answers product questions
           ├── comparator     → compares laptops
           ├── rag_agent      → answers policy questions
           └── advisor        → gives general advice
```

---

## Getting API Keys

### OpenRouter API Key
1. Visit [OpenRouter](https://openrouter.ai)
2. Sign up and create an account
3. Go to **Keys** section
4. Create a new API key
5. Copy it to `.env`

### LangSmith API Key (Optional)
1. Visit [LangSmith](https://smith.langchain.com)
2. Sign up and create an account
3. Go to **Settings** → **API Keys**
4. Create a new API key
5. Copy it to `.env`

---

## Testing API Connections

> **Note**: `test-chat.py` is a TEST FILE only. It verifies that OpenRouter API and LangSmith tracing work correctly. It does NOT represent the actual Buy-Bot implementation.

```bash
python test-chat.py
```

---

## Monitoring Traces

After running the chatbot:

1. Visit [LangSmith Dashboard](https://smith.langchain.com)
2. Select project **buy-bot**
3. View all conversation traces with inputs/outputs
4. Analyze latency, token usage, and performance

---

## Troubleshooting

### "OPENROUTER_API_KEY not found"
- Make sure `.env` file exists and contains the key
- Ensure `.env` is in the project root (not inside `rasa_bot/`)

### "rasa: command not found"
- Ensure your virtual environment is activated
- Run `pip install rasa==3.6.20`

### Action server not responding
- Make sure `rasa run actions` is running in a separate terminal
- Check that port 5055 is not blocked by a firewall

### "No traces appearing in LangSmith"
- Verify `LANGSMITH_API_KEY` is correct in `.env`
- Check `LANGSMITH_TRACING=true` is set

### Slow LLM responses
- The bot uses free OpenRouter models with rate limits
- Fallback models are tried automatically
- Reduce `max_tokens` in `langgraph_agents/agents/_llm.py` if needed
