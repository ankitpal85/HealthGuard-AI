"""
HealthGuard AI — LangChain Health Agent
Orchestrates all healthcare tools with a conversational LLM backbone.
Uses a stateful LangGraph pipeline to handle emergency triage and clinical tools.
"""

import os
import sys
from typing import Optional, TypedDict, Annotated, Sequence
import operator

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage

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
from tools.clinical_tools import (
    check_medication_interactions,
    analyze_symptoms,
    log_nutrition_log,
    run_risk_assessment_tool,
    generate_automated_report,
)


# ── LLM setup ────────────────────────────────────────────────────────────────

def _get_llm():
    """Return the configured LLM based on environment settings."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if not api_key or api_key.startswith("your_") or api_key.startswith("AQ.Ab") or len(api_key) < 20:
            raise ValueError(
                "GOOGLE_API_KEY is not configured or invalid. "
                "Please enter a valid Google Gemini API Key in ⚙️ AI Settings in the sidebar."
            )
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.3,
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or api_key.startswith("your_") or len(api_key) < 20:
            raise ValueError(
                "OPENAI_API_KEY is not configured or invalid. "
                "Please enter a valid OpenAI API Key in ⚙️ AI Settings in the sidebar."
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
    check_medication_interactions,
    analyze_symptoms,
    log_nutrition_log,
    run_risk_assessment_tool,
    generate_automated_report,
]


# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are HealthGuard AI, a premium personal health monitoring assistant.
Your role is to help users track medications, log nutrition, monitor fitness data, run predictive risk assessments, and look up medical information.

IMPORTANT GUIDELINES:
1. Always include a disclaimer that your information is for educational purposes only, not a substitute for professional medical advice.
2. Never diagnose medical conditions or prescribe treatments.
3. For emergencies, direct users to call 112 (India) or 911 (US) immediately or visit the nearest hospital.
4. When checking medication interactions, explain the clinical severity (Severe vs Moderate) and why they interact.
5. Provide context about normal ranges for vital signs (e.g. steps, heart rate, blood pressure, glucose, sleep, oxygen levels).
6. Be empathetic, clinical, and structured in your responses."""


# ── LangGraph Stateful Workflow ───────────────────────────────────────────────

class HealthState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


def triage_node(state: HealthState) -> dict:
    """Entry node that screens inputs for critical symptoms before calling LLM."""
    if not state["messages"]:
        return {"messages": []}
        
    last_msg = state["messages"][-1].content.lower()
    
    emergency_keywords = ["chest pain", "shortness of breath", "difficulty breathing", 
                          "severe chest pressure", "numbness in arm", "slurred speech", 
                          "face drooping", "loss of consciousness", "severe allergic reaction"]
    
    for kw in emergency_keywords:
        if kw in last_msg:
            msg = AIMessage(content=(
                "🚨 **EMERGENCY WARNING DETECTED** 🚨\n\n"
                "Your input mentions critical symptoms (**" + kw + "**) that may indicate a life-threatening medical emergency.\n\n"
                "⚠️ **Action Required:**\n"
                "1. **Call 112 (India) or 911 (US) immediately.**\n"
                "2. Visit the nearest hospital emergency room.\n"
                "3. Do not try to treat this yourself. Stay calm and wait for medical assistance.\n\n"
                "*(Disclaimer: HealthGuard AI has intercepted this message for clinical safety. "
                "Always seek professional medical attention in emergencies.)*"
            ))
            return {"messages": [msg]}
            
    return {"messages": []}


def agent_node(state: HealthState) -> dict:
    """Conversational LLM node with clinical tools bound."""
    llm = _get_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    
    # Prepend the system message for conversational context
    sys_msg = SystemMessage(content=SYSTEM_PROMPT)
    messages_list = [sys_msg] + list(state["messages"])
    
    resp = llm_with_tools.invoke(messages_list)
    return {"messages": [resp]}


def route_after_triage(state: HealthState):
    """Router that determines if we proceed to LLM or end immediately on emergency."""
    if state["messages"]:
        last_msg = state["messages"][-1]
        if isinstance(last_msg, AIMessage) and "EMERGENCY WARNING DETECTED" in last_msg.content:
            return "end"
    return "agent_node"


def route_after_agent(state: HealthState):
    """Router that checks if the LLM output is a tool call or finished answer."""
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return "end"


# ── Agent Builder ─────────────────────────────────────────────────────────────

def build_health_agent(user_id: int = 1):
    """
    Build and return a stateful LangGraph healthcare pipeline with tools and triage.
    """
    try:
        # Check LLM key configuration
        _get_llm()
    except ValueError as e:
        return None, str(e)

    try:
        from langgraph.graph import StateGraph, END
        from langgraph.prebuilt import ToolNode

        workflow = StateGraph(HealthState)

        # Add Nodes
        workflow.add_node("triage", triage_node)
        workflow.add_node("agent_node", agent_node)
        workflow.add_node("tools", ToolNode(ALL_TOOLS))

        # Set Entry Point
        workflow.set_entry_point("triage")

        # Set Conditional Edges
        workflow.add_conditional_edges(
            "triage",
            route_after_triage,
            {
                "end": END,
                "agent_node": "agent_node"
            }
        )
        workflow.add_conditional_edges(
            "agent_node",
            route_after_agent,
            {
                "tools": "tools",
                "end": END
            }
        )
        
        # Add normal transition from tools back to agent
        workflow.add_edge("tools", "agent_node")

        agent = workflow.compile()
        return agent, None
    except Exception as e:
        return None, f"Failed to build stateful LangGraph agent: {str(e)}"


def chat_with_agent(
    agent,
    user_message: str,
    chat_history: list = None,
) -> str:
    """
    Send a message through the stateful LangGraph pipeline and extract output.
    """
    if not agent:
        return get_simple_response(user_message)

    try:

        messages = []

        # Add conversation history
        if chat_history:
            recent = chat_history[-6:]  # Last 3 exchanges
            for msg in recent:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))

        # Add the current message
        messages.append(HumanMessage(content=user_message))

        # Invoke the graph
        result = agent.invoke({"messages": messages})

        # Get final output message
        output_messages = result.get("messages", [])
        for msg in reversed(output_messages):
            if isinstance(msg, AIMessage) and msg.content:
                return msg.content

        return "I couldn't process that request. Please try again."

    except Exception as e:
        error_msg = str(e)
        fallback = get_simple_response(user_message)
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg or "quota" in error_msg.lower():
            return (
                "⏳ **Free tier API quota limit reached.**\n\n"
                f"{fallback}"
            )
        if "API_KEY" in error_msg.upper() or "UNAUTHENTICATED" in error_msg.upper() or "INVALID" in error_msg.upper() or "400" in error_msg:
            return (
                "🔑 **API Key Configuration Required**\n\n"
                "Please enter a valid Gemini API key in **⚙️ AI Settings** (sidebar) to enable AI reasoning.\n\n"
                f"**Rule-based Assistant Response:**\n\n{fallback}"
            )
        return (
            f"{fallback}\n\n"
            f"*(Note: AI Agent error details: {error_msg})*"
        )



def get_simple_response(user_message: str) -> str:
    """
    Fallback rule-based response when LLM is not configured.
    """
    msg_lower = user_message.lower()

    if any(word in msg_lower for word in ["emergency", "chest pain", "can't breathe", "heart attack", "shortness of breath"]):
        return (
            "🚨 **EMERGENCY DETECTED**\n\n"
            "Please call **112** (India) or **911** (US) immediately!\n"
            "Or go to your nearest emergency room.\n\n"
            "Do not wait — seek immediate medical help."
        )
    elif any(word in msg_lower for word in ["medication", "medicine", "pill", "drug", "dose", "interaction"]):
        return (
            "💊 **Medications & Interactions**\n\n"
            "I can help you track your medications and check for interactions!\n"
            "- Use the **Medications** page to add schedules and track adherence.\n"
            "- If you configure your Gemini API key in ⚙️ Settings, I can check drug-drug interactions automatically in chat."
        )
    elif any(word in msg_lower for word in ["nutrition", "eat", "food", "calorie", "meal", "diet"]):
        return (
            "🍎 **Nutrition Tracker**\n\n"
            "Track your meals on our new **Nutrition** page!\n"
            "- Log breakfast, lunch, dinner, and snacks.\n"
            "- Track daily calories, protein, carbs, and fat.\n"
            "- Monitor water intake levels."
        )
    elif any(word in msg_lower for word in ["risk", "predictive", "diabetes", "cardiac", "anomaly", "forecast"]):
        return (
            "📈 **Risk & Predictive Analytics**\n\n"
            "Explore our new **Risk & Analytics** dashboard to:\n"
            "- Calculate 10-year cardiovascular disease risk.\n"
            "- Assess Type-2 diabetes risk profile.\n"
            "- View vital sign anomalies and 7-day regression forecasts.\n"
            "- Generate comprehensive health reports."
        )
    elif any(word in msg_lower for word in ["hello", "hi", "hey", "help", "namaste"]):
        return (
            "👋 **Welcome to HealthGuard AI!**\n\n"
            "I'm your personal health monitoring assistant. I can help you:\n\n"
            "💊 **Medication Tracking** — Set reminders & track adherence\n"
            "🍎 **Nutrition Logs** — Track food macros & hydration levels\n"
            "📈 **Risk & Analytics** — Forecast health trends & disease risk\n"
            "📝 **Health Log** — Log steps, BP, glucose, weight & more\n\n"
            "To unlock AI-powered stateful conversations, configure your API key in the ⚙️ Settings panel.\n\n"
            "⚠️ *I provide health information for educational purposes only, "
            "not as a substitute for professional medical advice.*"
        )
    else:
        return (
            "🤖 **HealthGuard AI**\n\n"
            "I'm your health monitoring assistant. Here's what I can help with:\n\n"
            "• **Medications & Nutrition**: Track medicines and meals\n"
            "• **Health Analytics**: Run clinical risk calculations and forecast trends\n"
            "• **Medical Info**: Look up reliable health information\n\n"
            "Configure your API key in ⚙️ Settings for full stateful AI conversations!\n\n"
            "⚠️ *Always consult a healthcare professional for medical advice.*"
        )
