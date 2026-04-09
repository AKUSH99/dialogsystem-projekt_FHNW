# Buy-Bot Setup Guide

## Prerequisites

- Python 3.10+
- Virtual environment (venv)

## Installation

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

### 3. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env .env
```

Then edit `.env` with your API keys:

```
OPENROUTER_API_KEY=sk-or-v1-xxxxx
LANGSMITH_API_KEY=ls_xxxxx
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=buy-bot
```

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

## Testing API Connections

> **Note**: `test-chat.py` is a TEST FILE only. It verifies that OpenRouter API and LangSmith tracing work correctly. It does NOT represent the actual Buy-Bot implementation.

```bash
python test-chat.py
```

### What test-chat.py Tests
- ✅ OpenRouter API connectivity
- ✅ LangSmith tracing integration
- ✅ LangGraph state management
- ✅ Basic safeguard filters
- ✅ Message history handling

**The actual Buy-Bot implementation will be created separately.**

## Architecture

```
User Input
    ↓
[Safeguard Filter] → Blocks unsafe content
    ↓
[LangGraph State] → Manages conversation history
    ↓
[Chat Node] → Calls OpenRouter LLM with system prompt
    ↓
[LangSmith Trace] → Logs all interactions for debugging
    ↓
Bot Response
```

## Monitoring Traces

After running the chatbot:

1. Visit [LangSmith Dashboard](https://smith.langchain.com)
2. Select project **buy-bot**
3. View all conversation traces with inputs/outputs
4. Analyze latency, token usage, and performance

## Available OpenRouter Models

Replace the model in `test-chat.py` with any OpenRouter model:

```python
# Examples:
"openrouter/meta-llama/llama-2-70b-chat"  # Llama 2 (free)
"openrouter/openai/gpt-3.5-turbo"         # GPT-3.5 Turbo
"openrouter/mistralai/mistral-7b-instruct" # Mistral 7B
```

## Customization (For Testing Only)

Since `test-chat.py` is a test file, these customizations are just for testing purposes:

### Modify Test System Prompt
Edit `SYSTEM_PROMPT` in `test-chat.py` to test different prompts.

### Add More Test Safeguards
Extend `safeguard_input()` function to test new filtering rules.

### Change Test LLM Parameters
Adjust `temperature`, `max_tokens`, or model in `test-chat.py` to test different configurations.

## Troubleshooting

### "OPENROUTER_API_KEY not found"
- Make sure `.env` file exists and contains the key
- Load env variables: `from dotenv import load_dotenv; load_dotenv()`

### "No traces appearing in LangSmith"
- Verify `LANGSMITH_API_KEY` is correct in `.env`
- Check `LANGSMITH_TRACING=true` is set
- Ensure the project name matches what's in LangSmith

### Slow responses
- Check your internet connection
- Try a faster model (e.g., `mistral-7b-instruct` instead of `llama-2-70b`)
- Reduce `max_tokens` if appropriate
