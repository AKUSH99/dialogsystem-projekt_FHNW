# agents/qa_agent.py
"""
QAAgent — always-on interceptor for off-script and off-topic messages.

Three responsibilities:
  1. classify_message() — classifies the user's latest message into one of:
       "on_script"  → normal answer to the current pipeline question
       "qa"         → off-script but laptop/shopping related (answer it)
       "off_topic"  → completely unrelated or inappropriate (refuse it)

  2. run()             — answers a "qa" question and hands back to the
                         interrupted stage

  3. handle_off_topic() — returns a hardcoded refusal for "off_topic" messages.
                          Hardcoded on purpose: we do not pass NSFW or unrelated
                          content into the LLM — the classifier saw it, the LLM
                          does not need to.

Why not change current_stage in run()?
  The graph routes back automatically using the existing current_stage value.
  If the QA agent changed it, the graph would not know where to return.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import Literal

from agents.prompts import BUYBOT_SYSTEM_PROMPT, QA_AGENT_ROLE
from agents.state import BuyBotState


# ---------------------------------------------------------------------------
# Classifier prompt
# ---------------------------------------------------------------------------

# Three-way classifier — kept here so it's easy to tune alongside the agent.
# The classifier receives the bot's last question AND the user's reply so it
# has enough context to classify short answers like "uni" or "yes" correctly.
_CLASSIFIER_PROMPT = """
You are a message classifier for a laptop purchasing advisor chatbot.

You will receive the bot's last question and the user's reply.
Classify the user's reply into exactly one of three categories:

ON_SCRIPT  — the reply answers the bot's question, even if it is short or informal.
             When in doubt, choose ON_SCRIPT.

QA         — the reply is a question or comment that does NOT answer the bot's question,
             but is still related to laptops, tech, or the buying process.

OFF_TOPIC  — the reply has nothing to do with buying a laptop, or contains
             harmful, inappropriate, or offensive content.

Examples — Bot: "What will you mainly use the laptop for?"
  User: "uni"              → ON_SCRIPT
  User: "gaming"           → ON_SCRIPT
  User: "mostly office"    → ON_SCRIPT
  User: "what does RAM mean?" → QA
  User: "what's the weather?" → OFF_TOPIC

Examples — Bot: "What's your budget in CHF?"
  User: "around 1500"      → ON_SCRIPT
  User: "1200 to 1500"     → ON_SCRIPT
  User: "why do you need that?" → QA
  User: "write me a poem"  → OFF_TOPIC

Examples — Bot: "Do you prefer Windows, macOS, or no preference?"
  User: "mac"              → ON_SCRIPT
  User: "windows"          → ON_SCRIPT
  User: "what's the difference?" → QA

Examples — Bot: "What are you studying?"
  User: "computer science" → ON_SCRIPT
  User: "architecture"     → ON_SCRIPT
  User: "does it matter?"  → QA

Reply with exactly one word: ON_SCRIPT, QA, or OFF_TOPIC.
""".strip()


# ---------------------------------------------------------------------------
# Hardcoded off-topic refusals (one per supported language)
# ---------------------------------------------------------------------------

# These are returned without an LLM call so that harmful content is never
# passed to the model as something to respond to.
_OFF_TOPIC_REFUSAL = {
    "english": (
        "I'm only able to help you find the right laptop. "
        "Let's get back to that — where were we?"
    ),
    "german": (
        "Ich kann nur beim Laptop-Kauf helfen. "
        "Lass uns weitermachen — wo waren wir?"
    ),
}

# Fallback if language is not set yet (should not happen in normal flow)
_OFF_TOPIC_REFUSAL_DEFAULT = _OFF_TOPIC_REFUSAL["english"]


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class QAAgent:
    """
    Handles off-script questions and off-topic/inappropriate messages.

    Usage as LangGraph nodes:
        agent = QAAgent(llm)
        graph.add_node("qa_agent", agent.run)
        graph.add_node("off_topic", agent.handle_off_topic)

    Usage as a conditional edge classifier:
        graph.add_conditional_edges(
            "intake",
            lambda state: QAAgent.classify_message(state, llm),
            {
                "on_script":  "intake",
                "qa":         "qa_agent",
                "off_topic":  "off_topic",
            }
        )
    """

    def __init__(self, llm):
        # Plain LLM — plain text responses, no structured output needed
        self.llm = llm

    def run(self, state: BuyBotState) -> dict:
        """
        Answers a laptop/shopping-related off-script question.

        Does NOT update current_stage — the graph uses the existing value
        to route back to the interrupted stage after this node completes.
        """
        system_message = SystemMessage(content=self._build_system_prompt(state))

        # Pass full conversation history so the LLM knows the context
        raw = self.llm.invoke([system_message] + state.messages)

        return {
            "messages": [AIMessage(content=raw.content)],
            # Intentionally no current_stage update — graph routes back using existing value
        }

    def handle_off_topic(self, state: BuyBotState) -> dict:
        """
        Returns a hardcoded refusal for off-topic or inappropriate messages.

        No LLM call — harmful or unrelated content is not forwarded to the model.
        The refusal is in the user's chosen language (falls back to English).
        """
        refusal = _OFF_TOPIC_REFUSAL.get(state.language, _OFF_TOPIC_REFUSAL_DEFAULT)

        return {
            "messages": [AIMessage(content=refusal)],
            # current_stage unchanged — conversation continues where it left off
        }

    @staticmethod
    def classify_message(state: BuyBotState, llm) -> Literal["on_script", "qa", "off_topic"]:
        """
        Classifies the user's latest message.

        Returns:
          "on_script"  → route to the current stage agent as normal
          "qa"         → route to qa_agent.run()
          "off_topic"  → route to qa_agent.handle_off_topic()

        Called by graph.py as the conditional edge function after each agent turn.
        Falls back to "on_script" if no human message is found, so the pipeline
        never gets stuck.
        """
        # Walk back through messages to find the last human reply and the
        # bot question that preceded it — both are needed for accurate classification.
        last_human = None
        last_bot   = None
        for msg in reversed(state.messages):
            if isinstance(msg, HumanMessage) and last_human is None:
                last_human = msg.content
            elif isinstance(msg, AIMessage) and last_human is not None and last_bot is None:
                last_bot = msg.content
                break  # we have both — stop scanning

        # Nothing to classify — let the current stage handle it
        if not last_human:
            return "on_script"

        # Format both turns so the classifier has full context.
        # Without the bot's question, short answers like "uni" or "yes" are ambiguous.
        if last_bot:
            context = f"Bot: {last_bot}\nUser: {last_human}"
        else:
            context = f"User: {last_human}"

        # Run the three-way classifier
        result = llm.invoke([
            SystemMessage(content=_CLASSIFIER_PROMPT),
            HumanMessage(content=context),
        ])

        label = result.content.strip().upper()

        if label == "QA":
            return "qa"
        if label == "OFF_TOPIC":
            return "off_topic"

        # ON_SCRIPT or anything unexpected → continue normally
        return "on_script"

    def _build_system_prompt(self, state: BuyBotState) -> str:
        """
        Builds the system prompt for the QA agent.

        Includes the interrupted stage and language so the answer is
        contextually grounded and in the right language.
        """
        return (
            f"{BUYBOT_SYSTEM_PROMPT}\n\n"
            f"{QA_AGENT_ROLE}\n\n"
            f"Interrupted stage: {state.current_stage}\n"
            f"Language: {state.language} — answer in this language."
        )
