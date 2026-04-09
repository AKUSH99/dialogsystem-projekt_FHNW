# 🛒 Buy-Bot – FHNW Dialogsysteme Projekt

> Ein intelligenter Laptop-Kaufberater-Chatbot, der Kunden ohne technisches Vorwissen durch den Kaufprozess führt.

**Modul:** Dialogsysteme – FHNW School of Business  
**Projekttyp:** Team-based Assessment

> **Important**: See `LLM.md`, `SETUP.md`, and `CHANGELOG.md` for technical documentation. The file `test-chat.py` is a **TEST FILE ONLY** for verifying API connections — it does NOT represent the actual Buy-Bot implementation.

---

## 📋 Inhaltsverzeichnis

- [Problemstellung](#-problemstellung)
- [Lösung](#-lösung)
- [Bot-Persona: Buy-Bot](#-bot-persona-buy-bot)
- [User Personas](#-user-personas)
- [Beispieldialoge](#-beispieldialoge)
- [Architektur](#-architektur)
- [Setup & Installation](#-setup--installation)
- [Projektartefakte](#-projektartefakte)
- [Bewertungskriterien](#-bewertungskriterien)
- [Team](#-team)

---

## ❗ Problemstellung

- **Hohe Abbruchraten** im Kaufprozess, weil Kunden unsicher sind, ob ein Gerät zu ihren Bedürfnissen passt.
- **Erhöhte Retouren-Quoten** durch Fehlkäufe, da herkömmliche Filter (Preis, Marke) den eigentlichen Use Case nicht abdecken.
- Kunden fühlen sich von technischen Spezifikationen (RAM, CPU, GPU, DDR5, Taktrate) **überfordert**.
- **Fehlende personalisierte Beratung** im E-Commerce-Bereich.

## 💡 Lösung

**Buy-Bot** ist ein Chatbot, der:
- Nutzer freundlich begrüsst und gezielte Fragen stellt (Budget, Zweck, Präferenzen)
- **2-4 passende Laptop-Optionen** mit kurzer Begründung liefert
- In **einfacher Sprache** berät - Lifestyle-Fokus statt Spec-Fokus
- Transparenz priorisiert (Preis, Vorteile, mögliche Nachteile)
- Fragen zu Garantie, Rückgabe und Versand via **RAG (Knowledge Base)** beantwortet

---

## 🤖 Bot-Persona: Buy-Bot

| Eigenschaft | Beschreibung |
|---|---|
| **Name** | Buy-Bot |
| **Persönlichkeit** | Optimistisch, verkaufsorientiert, freundlich, proaktiv |
| **Tonalität** | Professionell aber mit leichtem Werbe-Charme |
| **Mission** | Kaufen soll sich nicht wie Ausgeben anfühlen, sondern wie Investieren in Glück |
| **Verhalten** | Stellt gezielte Fragen, liefert passende Optionen mit Begründung, formuliert motivierend |
| **Hintergrund** | Entstand aus einem Innovationsprogramm für effizientere Einkaufserlebnisse |

---

## 👥 User Personas

### Persona 1: Laura Müller
| Eigenschaft | Beschreibung |
|---|---|
| **Alter** | 23 Jahre |
| **Beruf** | BWL-Studentin, 40% Marketingbüro |
| **Ziel** | Laptop für Uni und Alltag (Netflix, leichtes Arbeiten) |
| **Budget** | ca. 800 CHF |
| **Challenges** | Überfordert von technischen Filtern, Angst vor Fehlkauf oder überteuerten Modellen |
| **Desires** | Verständliche Beratung in Menschensprache, sichere Kaufentscheidung |

### Persona 2: Maca Damian
| Eigenschaft | Beschreibung |
|---|---|
| **Alter** | 18 Jahre |
| **Beruf** | Student |
| **Ziel** | Laptop für Uni und Gaming (CS:GO, League of Legends) |
| **Budget** | ca. 900 CHF |
| **Challenges** | Limitiertes Budget, wenig Zeit, junge Sprache |
| **Desires** | Zielgruppen-angepasste Sprache, interaktive Entscheidungsfindung |

---

## 💬 Beispieldialoge

### Dialog 1: Laura Müller - Studentin sucht Alltags-Laptop

| BOT | USER | BOT (Alternative) |
|---|---|---|
| Hello, I am Buy-Bot. | | Hi, I can help you find a laptop. |
| What is your budget? | 800 CHF | How much do you want to spend? |
| What do you need the laptop for? | University, browsing, and Netflix. | Is it mainly for study or entertainment? |
| Do you carry it with you every day? | Yes. | Do you use it on the go? |
| Is low weight important for you? | Yes. | Do you want something light for commuting? |
| Do you need it for gaming too? | No. | Will you also play games on it? |
| I recommend a light everyday laptop. | | A simple student laptop fits your needs. |
| It is good for study, streaming, and daily use. | | It should work well for classes and Netflix. |
| Do you want to see a cheaper option too? | Yes. | I can also show you a lower-cost option. |
| Great. I will show you two options. | | Okay, here are two matching laptops. |

### Dialog 2: Maca Damian - Student sucht Gaming-Laptop

| BOT | USER | BOT (Alternative) |
|---|---|---|
| Hello, I am Buy-Bot. | | Hi, I can help you find a laptop. |
| What is your budget? | 900 CHF | How much do you want to spend? |
| What do you need the laptop for? | University and gaming. | Is it for study, gaming, or both? |
| Which games do you play? | Counter-Strike and League of Legends. | What games are important for you? |
| Do you carry it to class every day? | Yes. | Will you use it on the go? |
| What matters more: FPS or portability? | FPS. | Do you want more gaming power or lower weight? |
| I recommend a budget gaming laptop. | | A mid-range gaming laptop fits your needs. |
| It is good for study and esports games. | | It should work well for university and daily gaming. |
| Do you want to see a cheaper option too? | Yes. | I can also show you a lower-cost option. |
| Great. I will show you two options. | | Okay, here are two matching laptops. |

---

## 🏗 Architektur

Das System verwendet **Rasa als primären Dialog-Manager** (für strukturierte Konversationen via Intents, Entities, Slots und Forms) und **LangGraph als "Expertenteam"** für freie oder komplexe Fragen via spezialisierter LLM-Agenten.

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
           ├── router       → classifies the question
           ├── product_expert → answers product questions
           ├── comparator   → compares laptops side by side
           ├── rag_agent    → answers policy/guarantee questions
           └── advisor      → gives general lifestyle advice
```

### Projektstruktur

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
└── requirements.txt             # Python dependencies
```

### Kanäle
| Kanal | Beschreibung |
|---|---|
| **Primär** | Web-Chat auf der E-Commerce-Website (REST / SocketIO) |
| **Optional** | Telegram |

---

## 🚀 Setup und Installation

Vollständige Anweisungen findest du in [`SETUP.md`](SETUP.md).

**Kurzanleitung:**

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. Umgebungsvariablen konfigurieren
cp .env.example .env  # API-Keys eintragen

# 3. Rasa-Modell trainieren
cd rasa_bot && rasa train

# 4. Action-Server starten (neues Terminal)
cd rasa_bot && rasa run actions

# 5. Rasa-Server starten
cd rasa_bot && rasa run --cors "*"
# oder direkt im Terminal chatten:
cd rasa_bot && rasa shell
```

---

## 📎 Projektartefakte

| Artefakt | Link |
|---|---|
| **Conversational AI Canvas (Miro)** | https://miro.com/app/board/uXjVG2xTs8c=/ |
| **Präsentationsfolien** | Link folgt |
| **Voiceflow-Projekt** | Link folgt |
| **GitHub Repository** | [AKUSH99/dialogsystem-projekt_FHNW](https://github.com/AKUSH99/dialogsystem-projekt_FHNW) |

---

## 📊 Bewertungskriterien

| Kriterium | Gewicht | Fokus |
|---|---|---|
| Define, UX und Personas | 10% | Kontext, Domäne, User Experience, realistische Use Cases |
| Conversational Design | 25% | Realistische Dialoge, klarer Gesprächsfluss |
| Architecture und Information Need | 10% | Systemarchitektur, API-Integrationen |
| Build, Release und Operate | 20% | NLU/LLM-Nutzung, funktionierendes System, Fehlerbehandlung |
| Overall und Artefakte | 20% | Vollständiges AI Canvas, nachvollziehbare Umsetzung |
| Presentation und Demonstration | 15% | Klare Präsentation, überzeugende Demo |

---

## 👥 Team

| Name | Rolle |
|---|---|
| Almidin Bangoji | Student / Collaborator |
| Vaagisan Vadivel | Student / Collaborator |
| Damian Martin | Student / Collaborator |

---

## 📄 Lizenz

Dieses Projekt wurde im Rahmen des Moduls Dialogsysteme an der FHNW erstellt.
