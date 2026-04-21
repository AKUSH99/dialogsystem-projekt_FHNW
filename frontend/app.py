# frontend/app.py
"""
Buy-Bot — Streamlit chat frontend.

Run from the project root:
    streamlit run frontend/app.py

Each browser tab is an independent conversation with its own session_id.
The LangGraph graph is built once and shared across all sessions (stateless);
per-session state lives in MemorySaver (keyed by thread_id) and st.session_state.
"""

import os
import sys

# Add the project root to sys.path so 'agents.*' imports work regardless
# of which directory Streamlit is launched from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from langchain_core.messages import HumanMessage

from agents.graph import build_graph
from agents.llm_builder import build_llms
from agents.state import create_initial_state

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Buy-Bot — Laptop Advisor",
    page_icon="💻",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Shared resources — built once per server process, shared across all sessions
# ---------------------------------------------------------------------------

@st.cache_resource
def get_graph():
    """
    Builds the LangGraph pipeline once and caches it for the lifetime of the
    server process. All sessions share the same compiled graph — this is safe
    because all conversation state is stored in MemorySaver keyed by thread_id,
    so sessions never interfere with each other.

    Two models are used:
      llm_fast   → intake, expert agents, classifier
      llm_strong → QA answers, search ranking, suggestion

    To switch models, edit model_config.py — no need to touch this file.
    """
    llm_fast, llm_strong = build_llms()

    # Use absolute path for the database so the app works regardless of
    # which directory Streamlit is launched from.
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "laptops.db",
    )

    return build_graph(llm_fast, llm_strong, db_path=db_path)


# ---------------------------------------------------------------------------
# Session initialisation
# ---------------------------------------------------------------------------

def init_session():
    """
    Sets up a fresh conversation session in st.session_state.
    Called once when the tab is first opened, and again when the user
    clicks "New conversation".

    st.session_state keys:
        session_id  — LangGraph thread_id, unique per conversation
        messages    — list of {"role": "user"|"assistant", "content": str}
                      used to render the chat history
        done        — True when the pipeline has finished (stage == "done")
    """
    state = create_initial_state()
    st.session_state.session_id = state.session_id
    st.session_state.messages   = []
    st.session_state.done       = False

    # First graph invocation — no user message yet.
    # Dispatch sees empty messages and routes to intake, which generates
    # the opening language-choice greeting.
    graph  = get_graph()
    config = {"configurable": {"thread_id": st.session_state.session_id}}
    result = graph.invoke({"session_id": state.session_id}, config)

    greeting = result["messages"][-1].content
    st.session_state.messages.append({"role": "assistant", "content": greeting})


# Initialise on first load only
if "session_id" not in st.session_state:
    init_session()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Buy-Bot")
    st.caption("Laptop purchasing advisor")
    st.divider()
    st.markdown(
        "I'll ask you a few questions and recommend the best laptop "
        "from our catalogue for your needs and budget."
    )
    st.markdown("**Tips:**")
    st.markdown("- Ask 'what does OLED mean?' at any point")
    st.markdown("- Prices are in CHF")
    st.divider()

    if st.button("New conversation", use_container_width=True):
        init_session()
        st.rerun()

# ---------------------------------------------------------------------------
# Chat header
# ---------------------------------------------------------------------------

st.title("Buy-Bot — Laptop Advisor")

# ---------------------------------------------------------------------------
# Render conversation history
# ---------------------------------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

if st.session_state.done:
    # Pipeline finished — disable input and show a restart prompt
    st.success("Recommendation complete. Start a new conversation from the sidebar.")

else:
    if prompt := st.chat_input("Type your message..."):
        # 1. Show the user's message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Invoke the graph and wait for the bot's reply
        with st.chat_message("assistant"):
            with st.spinner(""):
                graph  = get_graph()
                config = {"configurable": {"thread_id": st.session_state.session_id}}

                result = graph.invoke(
                    {"messages": [HumanMessage(content=prompt)]},
                    config,
                )

            reply = result["messages"][-1].content
            st.markdown(reply)

        # 3. Persist the reply and check if the pipeline is done
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.done = result.get("current_stage") == "done"

        # 4. Rerun so the input box resets cleanly
        st.rerun()
