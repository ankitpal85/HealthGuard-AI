"""
HealthGuard AI — Health Chatbot Page
AI-powered health assistant with medical information lookup.
"""

import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db
from agents.health_agent import build_health_agent, chat_with_agent, get_simple_response


SUGGESTED_QUESTIONS = [
    "What are today's medications?",
    "What is normal blood pressure?",
    "Explain the symptoms of diabetes",
    "How much water should I drink daily?",
    "What are the benefits of walking 10,000 steps?",
    "Tell me about heart rate zones for exercise",
    "What is the normal blood glucose range?",
    "How does sleep affect health?",
]


def show_chatbot():
    user_id = st.session_state.get("user_id", 1)

    st.markdown("""
    <div style="margin-bottom:20px">
        <h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;margin:0">
            🤖 HealthGuard AI Chat
        </h1>
        <p style="color:#94a3b8;margin:4px 0 0 0">Ask me anything about your health, medications, or wellness</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Initialize agent ───────────────────────────────────────────────────
    if "health_agent" not in st.session_state:
        with st.spinner("Initializing AI agent..."):
            agent, err = build_health_agent(user_id)
            st.session_state.health_agent = agent
            st.session_state.agent_error = err

    if st.session_state.agent_error:
        banner_html = (
            '<div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);'
            'border-radius:12px;padding:14px 18px;margin-bottom:16px;">'
            '<span style="color:#f59e0b;font-weight:600">⚙️ Rule-Based Assistant Active</span>'
            f'<div style="color:#94a3b8;font-size:0.85rem;margin-top:4px">'
            f'{st.session_state.agent_error}<br>'
            '💡 <em>Running in Rule-Based fallback mode. Enter a valid Google Gemini API Key in ⚙️ AI Settings (sidebar) to activate full AI reasoning.</em>'
            '</div></div>'
        )
        st.markdown(banner_html, unsafe_allow_html=True)


    # ── Suggested questions ────────────────────────────────────────────────
    st.markdown("<p style='color:#94a3b8;font-size:0.85rem;margin-bottom:8px'>💡 Suggested questions:</p>",
                unsafe_allow_html=True)
    cols = st.columns(4)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 4]:
            if st.button(q, key=f"suggest_{i}", use_container_width=True):
                st.session_state.pending_message = q

    st.markdown("<hr style='border-color:rgba(148,163,184,0.1);margin:16px 0'>", unsafe_allow_html=True)

    # ── Chat history display ───────────────────────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

        # Load from DB
        history = db.get_chat_history(user_id, limit=20)
        if history:
            st.session_state.chat_messages = history
        else:
            # Welcome message
            welcome = (
                "👋 **Hello! I'm HealthGuard AI**, your personal health monitoring assistant.\n\n"
                "I can help you with:\n"
                "• 💊 Medication reminders and tracking\n"
                "• 📊 Health metrics and wellness data\n"
                "• 🔍 Medical information from trusted sources\n"
                "• 📈 Health insights and goal tracking\n\n"
                "**⚠️ Disclaimer**: I provide health information for educational purposes only. "
                "Always consult a qualified healthcare professional for medical advice.\n\n"
                "How can I help you today?"
            )
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": welcome,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

    # Display messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])
                ts = msg.get("created_at", "")
                if ts:
                    st.caption(ts)

    # ── Handle pending messages from suggestion buttons ────────────────────
    if "pending_message" in st.session_state:
        pending = st.session_state.pop("pending_message")
        _process_message(pending, user_id)
        st.rerun()

    # ── Chat input ─────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask me about your health, medications, or wellness..."):
        _process_message(prompt, user_id)
        st.rerun()

    # ── Clear chat button ─────────────────────────────────────────────────
    col_clr, col_export = st.columns([1, 1])
    with col_clr:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    with col_export:
        if st.session_state.chat_messages:
            chat_export = "\n\n".join(
                [f"**{m['role'].title()}** ({m.get('created_at','')})\n{m['content']}"
                 for m in st.session_state.chat_messages]
            )
            st.download_button(
                "📥 Export Chat", chat_export,
                f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                "text/plain", use_container_width=True
            )

    # ── Emergency info ────────────────────────────────────────────────────
    emerg_html = (
        '<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);'
        'border-radius:12px;padding:12px 16px;margin-top:16px;text-align:center">'
        '<span style="color:#ef4444;font-weight:600">🚨 Medical Emergency?</span>'
        '<span style="color:#94a3b8;font-size:0.85rem;margin-left:8px">'
        'Call <strong style="color:#ef4444">112</strong> (India) immediately. '
        'Do not rely on AI for emergency medical situations.</span></div>'
    )
    st.markdown(emerg_html, unsafe_allow_html=True)



def _process_message(prompt: str, user_id: int):
    """Process a user message and generate a response."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Add user message
    user_msg = {"role": "user", "content": prompt, "created_at": timestamp}
    st.session_state.chat_messages.append(user_msg)
    db.save_chat_message(user_id, "user", prompt)

    # Generate response
    agent = st.session_state.get("health_agent")
    if agent:
        history = st.session_state.chat_messages[:-1]  # exclude the just-added message
        with st.spinner("HealthGuard AI is thinking..."):
            response = chat_with_agent(agent, prompt, history)
    else:
        response = get_simple_response(prompt)

    # Add assistant message
    assistant_msg = {"role": "assistant", "content": response, "created_at": timestamp}
    st.session_state.chat_messages.append(assistant_msg)
    db.save_chat_message(user_id, "assistant", response)
