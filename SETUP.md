# Buy-Bot Setup Guide

## Prerequisites

- Python 3.10 (required for Rasa)
- Virtual environment (venv or conda)

---

## 1. Activate Virtual Environment

```bash
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```
OPENROUTER_API_KEY=sk-or-v1-xxxxx
LANGSMITH_API_KEY=ls_xxxxx
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=buy-bot
```

---

## 4. Build the Product Database

```bash
python data/init_db.py
```

This generates `data/laptops.db` from `data/laptops.sql`. Run this any time you update the SQL file.

---

## 5. Test API Connections

```bash
python test-chat.py
```

> `test-chat.py` only verifies OpenRouter and LangSmith connectivity. It is not the actual bot.

---

## Project Structure

```
dialogsystem-projekt_FHNW/
├── rasa_bot/                    # Rasa intake layer (to be built)
│   ├── domain.yml
│   ├── config.yml
│   ├── data/
│   │   ├── nlu.yml
│   │   ├── stories.yml
│   │   └── rules.yml
│   └── actions/
│       └── actions.py           # Webhook: triggers LangGraph pipeline
├── agents/                      # LangGraph pipeline (to be built)
│   ├── graph.py
│   ├── router.py
│   ├── uni_agent.py
│   ├── gaming_agent.py
│   ├── professional_agent.py
│   ├── office_agent.py
│   ├── search_agent.py
│   ├── suggestion_agent.py
│   └── qa_agent.py
├── data/
│   ├── laptops.sql              # Source schema + data (28 laptops)
│   ├── laptops.db               # Compiled SQLite database
│   ├── init_db.py               # Rebuilds laptops.db
│   └── policies.md              # Store policies for RAG
├── frontend/                    # (to be built)
│   ├── streamlit_app.py
│   └── telegram_bot.py
├── test-chat.py
├── requirements.txt
└── .env.example
```

---

## Getting API Keys

### OpenRouter
1. Visit [openrouter.ai](https://openrouter.ai)
2. Sign up → Keys → Create new key
3. Copy to `.env`

### LangSmith (optional, for tracing)
1. Visit [smith.langchain.com](https://smith.langchain.com)
2. Settings → API Keys → Create new key
3. Copy to `.env`

---

## Monitoring

After running the bot, view all conversation traces at [smith.langchain.com](https://smith.langchain.com) under project **buy-bot**.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `OPENROUTER_API_KEY not found` | Check `.env` exists in project root |
| `rasa: command not found` | Activate venv, run `pip install rasa==3.6.21` |
| Action server not responding | Run `rasa run actions` in a separate terminal (port 5055) |
| No LangSmith traces | Verify `LANGSMITH_API_KEY` and `LANGSMITH_TRACING=true` in `.env` |
