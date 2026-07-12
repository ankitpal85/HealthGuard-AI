"""
HealthGuard AI — LangChain Health Agent
Orchestrates all healthcare tools with a conversational LLM backbone.
Compatible with LangChain v1.3+ / LangGraph-based agent execution.
"""

import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage

from tools.medical_info_tool import medical_info_lookup
from tools.medication_tool import (
    add_medication_reminder,
    get_todays_medications,
    mark_medication_taken,
    get_medication_adherence_report,
)
from tools.health_data_tool import (
    log_health_metric,
    get_health_summary,
    parse_health_data_json,
    calculate_bmi,
)


# ── LLM setup ────────────────────────────────────────────────────────────────

def _get_llm():
    """Return the configured LLM based on environment settings."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key or api_key == "your_google_gemini_api_key_here":
            raise ValueError(
                "GOOGLE_API_KEY not configured. "
                "Please set it in your .env file."
            )
        # gemini-2.0-flash is the model available on the free API tier
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.3,
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "your_openai_api_key_here":
            raise ValueError(
                "OPENAI_API_KEY not configured. "
                "Please set it in your .env file."
            )
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=api_key,
            temperature=0.3,
        )
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'gemini' or 'openai'.")


# ── Tools list ────────────────────────────────────────────────────────────────

ALL_TOOLS = [
    medical_info_lookup,
    add_medication_reminder,
    get_todays_medications,
    mark_medication_taken,
    get_medication_adherence_report,
    log_health_metric,
    get_health_summary,
    parse_health_data_json,
    calculate_bmi,
]


# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are HealthGuard AI, a personal health monitoring assistant.
Your role is to help users track medications, monitor fitness data, and look up reliable health information.

IMPORTANT GUIDELINES:
1. Always include a disclaimer that your information is for educational purposes only, not a substitute for professional medical advice.
2. Never diagnose medical conditions or prescribe treatments.
3. For emergencies, always direct users to call 112 (India) or 911 (US) or visit the nearest hospital.
4. Be empathetic, supportive, and patient-friendly.
5. When helping with medication reminders, gather: medication name, dosage, frequency, and any special instructions.
6. For health metrics, always provide context about normal ranges.
7. Respect patient privacy and data confidentiality.
8. Keep answers concise and health-focused."""


# ── Agent Builder ─────────────────────────────────────────────────────────────

def build_health_agent(user_id: int = 1):
    """
    Build and return a LangGraph-based agent with all healthcare tools.

    Args:
        user_id: Current user's ID for context.

    Returns:
        Tuple of (agent_executor, error_string).
        agent_executor is None if LLM is not configured.
    """
    try:
        llm = _get_llm()
    except ValueError as e:
        return None, str(e)

    try:
        from langgraph.prebuilt import create_react_agent as lg_create_react_agent
        agent = lg_create_react_agent(
            model=llm,
            tools=ALL_TOOLS,
            prompt=SYSTEM_PROMPT,
        )
        return agent, None
    except Exception as e:
        return None, f"Failed to build agent: {str(e)}"


def chat_with_agent(
    agent,
    user_message: str,
    chat_history: list = None,
) -> str:
    """
    Send a message to the health agent and get a response.

    Args:
        agent: The LangGraph agent.
        user_message: The user's input message.
        chat_history: List of previous messages for context.

    Returns:
        Agent's response string.
    """
    try:
        # Build messages list
        messages = []

        # Add recent chat history as context
        if chat_history:
            recent = chat_history[-6:]  # last 3 exchanges
            for msg in recent:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    from langchain_core.messages import AIMessage
                    messages.append(AIMessage(content=msg["content"]))

        # Add the current user message
        messages.append(HumanMessage(content=user_message))

        result = agent.invoke({"messages": messages})

        # Extract the last AI message from the result
        output_messages = result.get("messages", [])
        for msg in reversed(output_messages):
            if hasattr(msg, "content") and msg.__class__.__name__ in ("AIMessage", "HumanMessage"):
                if msg.__class__.__name__ == "AIMessage" and msg.content:
                    return msg.content

        return "I couldn't process that request. Please try again."

    except Exception as e:
        error_msg = str(e)
        # Rate limit / quota exhausted
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg or "quota" in error_msg.lower():
            return (
                "⏳ **Free tier quota temporarily exhausted.**\n\n"
                "Your Gemini API key is valid and working! The free tier has a per-minute "
                "and daily request limit. Please wait a minute and try again.\n\n"
                "💡 Meanwhile, all tracking features (medications, health log, dashboard) "
                "work without any quota limit."
            )
        if "API_KEY" in error_msg.upper() or "UNAUTHENTICATED" in error_msg.upper():
            return (
                "🔑 **API key issue detected.**\n\n"
                "Please check your GOOGLE_API_KEY in the .env file and restart the app."
            )
        return (
            f"I encountered an error processing your request. "
            f"Please try rephrasing your question.\n\nError details: {error_msg}"
        )


def get_simple_response(user_message: str) -> str:
    """
    Fallback rule-based response when LLM is not configured.
    """
    msg_lower = user_message.lower()

    if any(word in msg_lower for word in ["emergency", "chest pain", "can't breathe", "heart attack"]):
        return (
            "🚨 **EMERGENCY DETECTED**\n\n"
            "Please call **112** (India) or **911** (US) immediately!\n"
            "Or go to your nearest emergency room.\n\n"
            "Do not wait — seek immediate medical help."
        )
    elif any(word in msg_lower for word in ["medication", "medicine", "pill", "drug", "dose"]):
        return (
            "💊 **Medication Help**\n\n"
            "I can help you track your medications! Use the **Medications** page to:\n"
            "• Add new medication reminders\n"
            "• View today's schedule\n"
            "• Mark medications as taken\n"
            "• Check your adherence report\n\n"
            "⚠️ Always follow your doctor's prescription. Never self-medicate."
        )
    elif any(word in msg_lower for word in ["steps", "exercise", "fitness", "heart rate", "blood pressure"]):
        return (
            "🏃 **Health Metrics**\n\n"
            "Track your fitness on the **Health Log** page!\n"
            "• Daily step count\n"
            "• Heart rate & blood pressure\n"
            "• Weight & BMI\n"
            "• Blood glucose & oxygen levels\n\n"
            "Regular monitoring helps detect health trends early."
        )
    elif any(word in msg_lower for word in ["bmi", "weight", "height"]):
        return (
            "⚖️ **BMI Calculator**\n\n"
            "Use the **Health Log** page to calculate and track your BMI.\n"
            "Normal BMI range: **18.5 – 24.9 kg/m²**\n\n"
            "⚠️ BMI is a screening tool. Consult your doctor for a complete assessment."
        )
    elif any(word in msg_lower for word in ["hello", "hi", "hey", "help", "namaste"]):
        return (
            "👋 **Welcome to HealthGuard AI!**\n\n"
            "I'm your personal health monitoring assistant. I can help you:\n\n"
            "💊 **Medication Tracking** — Set reminders & track adherence\n"
            "📊 **Health Metrics** — Log steps, BP, glucose, weight & more\n"
            "🔍 **Medical Information** — Look up reliable health info\n"
            "📈 **Health Goals** — Set and monitor wellness targets\n\n"
            "To unlock AI-powered conversations, configure your API key in the ⚙️ Settings panel.\n\n"
            "⚠️ *I provide health information for educational purposes only, "
            "not as a substitute for professional medical advice.*"
        )
    else:
        return (
            "🤖 **HealthGuard AI**\n\n"
            "I'm your health monitoring assistant. Here's what I can help with:\n\n"
            "• **Medications**: Track and manage your medication schedule\n"
            "• **Health Metrics**: Log daily health measurements\n"
            "• **Medical Info**: Look up reliable health information\n"
            "• **Reports**: View health trends and adherence reports\n\n"
            "Configure your API key in ⚙️ Settings for full AI-powered conversations!\n\n"
            "⚠️ *Always consult a healthcare professional for medical advice.*"
        )
