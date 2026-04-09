# Buy-Bot Architecture – Rasa + LangGraph Agents

Technical design for Buy-Bot using Rasa NLU and LangGraph specialized agents.

> 👉 **See [README.md](README.md) for user personas and example conversations**

---

## 🎯 Design Philosophy

Buy-Bot uses a **two-stage conversation approach**:

1. **Intent Extraction** (Rasa) – Understand user needs
2. **Specialized Agents** (LangGraph) – Deliver targeted conversation per use case

Benefits:
- Each agent asks the right questions for its use case
- Conversation stays focused and efficient
- Recommendations are highly tailored
- User experience optimized per persona

---

## 🏗 System Architecture

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Rasa NLU - Intent Extraction  │
│  Extracts: budget, use_case,    │
│  mobility, performance, etc.    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  LangGraph Agent Router         │
│  Selects appropriate agent      │
└────────────┬────────────────────┘
             │
     ┌───────┼───────┐
     ▼       ▼       ▼
   ┌──────┬──────┬──────┐
   │ Uni  │Gaming│Work  │
   │Agent │Agent │Agent │
   └──────┴──────┴──────┘
     │       │       │
     └───────┼───────┘
             ▼
┌─────────────────────────────────┐
│  Recommendation Engine          │
│  Product matching & filtering   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Output: 2-4 Recommendations    │
│  with explanations              │
└─────────────────────────────────┘
```

---

## 🧠 Rasa NLU Component

### Extracted Intents

| Intent | Triggers | Agent |
|--------|----------|-------|
| `university` | "student", "uni", "study", "school" | Uni Agent |
| `gaming` | "game", "esports", "fps", "gaming" | Gaming Agent |
| `work` | "work", "professional", "office", "business" | Work Agent |
| `entertainment` | "movie", "streaming", "video editing" | General Agent |
| `mixed` | Multiple use cases | Multi-purpose Agent |

### Extracted Entities

| Entity | Type | Example |
|--------|------|---------|
| `budget` | float | `800.0`, `1500.0` (not translated) |
| `use_case` | string | "university", "gaming", "work" |
| `mobility` | string | "high", "medium", "low" |
| `performance` | string | "high", "medium", "low" |
| `screen_size` | string | "small", "medium", "large" |

### Rasa Training Data Structure

```yaml
version: "3.1"
nlu:
- intent: university
  examples: |
    - I'm a student
    - I need a laptop for uni
    - Budget [800](budget) CHF for studying
    
- intent: gaming
  examples: |
    - I want to play games
    - Gaming laptop needed
    - [1500](budget) CHF for gaming
```

---

## 🤖 LangGraph Agent System

### Agent Base Class

```python
class SpecializedAgent:
    def __init__(self, intent: dict):
        self.intent = intent
        self.llm = ChatOpenAI(model="...")
        self.product_db = ProductDatabase()
    
    def ask_questions(self) -> dict:
        """Ask use-case-specific questions"""
        pass
    
    def recommend_products(self, user_profile: dict) -> List[Laptop]:
        """Return 2-4 tailored recommendations"""
        pass
```

### Three Agent Types

**Uni Agent:**
- Target: Students
- Focus: Lightweight, battery life, reliability

**Gaming Agent:**
- Target: Gamers
- Focus: GPU/CPU performance, refresh rate

**Work Agent:**
- Target: Professionals
- Focus: Reliability, productivity, security

---

## 🗄 Product Database

### Laptop Schema

```python
@dataclass
class Laptop:
    id: str
    name: str
    brand: str
    price: float
    
    # Hardware
    cpu: str  # "Intel Core i5-13420H"
    gpu: str  # "RTX 4060" or "Integrated"
    ram_min: int  # GB
    storage: int  # GB
    
    # Display
    screen_size: float  # inches
    refresh_rate: int  # Hz
    resolution: str  # "1920x1200"
    
    # Physical
    weight: float  # kg
    battery_life: float  # hours
    color: str
    
    # Classification
    use_case: List[str]  # ["university", "gaming", "work"]
    tier: str  # "budget", "mid", "premium"
    
    # Details
    description: str
    pros: List[str]
    cons: List[str]
    best_for: str
```

### Product Matching Algorithm

```python
def match_products(user_profile: dict) -> List[Laptop]:
    # Budget is float extracted by Rasa (e.g., 800.0)
    budget = user_profile.get("budget", 1000.0)
    
    # Filter with 20% margin (± 20% from budget)
    price_min = budget * 0.8
    price_max = budget * 1.2
    
    candidates = laptop_db.filter(
        price_min=price_min,
        price_max=price_max,
        use_case=user_profile["primary_use_case"]
    )
    
    # Score by relevance to user profile
    scored = []
    for laptop in candidates:
        score = calculate_score(laptop, user_profile)
        scored.append((laptop, score))
    
    # Return top 4 matches
    return sorted(scored, key=lambda x: x[1], reverse=True)[:4]
```

---

## 🧠 Conversation State

### LangSmith Tracing

Every conversation is logged automatically:
- Input (user message)
- Rasa NLU extraction (intent, entities)
- Selected agent
- Agent questions & responses
- Final recommendations
- Latency & token usage

### Agent State

```python
agent_state = {
    "intent": {...},
    "user_profile": {
        "budget": 800.0,
        "use_case": "university",
        "mobility": "high",
        ...
    },
    "questions_asked": [...],
    "conversation_history": [...],
    "recommendations": [...],
    "timestamp": "2026-04-09T10:30:00Z"
}
```

---

## 🔄 Implementation Roadmap

### Phase 1: Infrastructure Testing ✅
- [x] test-chat.py - OpenRouter API verification
- [x] LangSmith tracing setup
- [x] Documentation

### Phase 2: Rasa NLU Setup 🔵
- [ ] Install Rasa
- [ ] Create training data (nlu.yml)
- [ ] Train NLU model
- [ ] Test intent extraction
- [ ] Integrate with Python backend

### Phase 3: Agent Development 🔵
- [ ] Create Agent base class
- [ ] Implement UniAgent
- [ ] Implement GamingAgent
- [ ] Implement WorkAgent
- [ ] Create agent router

### Phase 4: Product System 🔵
- [ ] Design product database schema
- [ ] Load product data
- [ ] Implement matching algorithm
- [ ] Create product descriptions

### Phase 5: Integration 🔵
- [ ] Connect Rasa → Agent Router → LangGraph
- [ ] Test full conversation flow
- [ ] Performance optimization
- [ ] LangSmith monitoring

### Phase 6: Frontend Interfaces 🔵
- [ ] Streamlit app (simple web interface)
- [ ] Telegram bot integration

---

## 🚀 Deployment

### Infrastructure
- Rasa model serving (separate server or integrated)
- LangGraph agent execution (async support)
- Product database (SQL or NoSQL)
- Message queue for conversation logging (Redis/RabbitMQ)

### Monitoring
- LangSmith dashboard for conversations
- Error tracking (Sentry/DataDog)
- Performance metrics (response time, tokens)

---

**Version:** 1.0  
**Status:** Planning Phase  
**Next Step:** Implement Rasa NLU component
