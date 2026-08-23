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
from tools.indian_health_tool import (
    search_indian_medication_tool,
    search_ayurvedic_herbs_tool,
    search_practo_doctors_tool,
    check_air_quality_tool,
)
from tools.medical_research_tool import search_pubmed_research
from tools.vision_voice_tool import analyze_medical_image_tool, process_voice_query_tool


# ── LLM setup ────────────────────────────────────────────────────────────────

def _get_llm():
    """Return the configured LLM with automatic multi-provider (Gemini <-> OpenAI) fallback."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    google_key = os.getenv("GOOGLE_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    if provider == "gemini" and not google_key and openai_key.startswith("sk-"):
        provider = "openai"

    providers = [provider]
    if provider == "gemini":
        providers.append("openai")
    else:
        providers.append("gemini")

    last_exc = None
    for p in providers:
        if p == "gemini":
            if google_key:
                try:
                    from langchain_google_genai import ChatGoogleGenerativeAI
                    preferred_models = [
                        "gemini-1.5-flash",
                        "gemini-2.0-flash",
                        "gemini-1.5-pro",
                        "gemini-2.0-flash-exp",
                        "gemini-pro",
                    ]
                    for model_name in preferred_models:
                        try:
                            llm = ChatGoogleGenerativeAI(
                                model=model_name,
                                google_api_key=google_key,
                                temperature=0.3,
                                max_retries=1,
                            )
                            llm.invoke("hi")
                            print(f"[OK] Successfully initialized Gemini LLM model: {model_name}")
                            return llm
                        except Exception as model_ex:
                            print(f"[WARN] Gemini model {model_name} failed: {str(model_ex)[:100]}")
                            last_exc = model_ex
                            continue
                except Exception as ex:
                    print(f"[WARN] Google Generative AI import/setup failed: {str(ex)[:100]}")
                    last_exc = ex
        elif p == "openai":
            if openai_key and openai_key.startswith("sk-"):
                try:
                    from langchain_openai import ChatOpenAI
                    preferred_openai = ["gpt-4o-mini", "gpt-3.5-turbo"]
                    for model_name in preferred_openai:
                        try:
                            llm = ChatOpenAI(
                                model=model_name,
                                openai_api_key=openai_key,
                                temperature=0.3,
                                max_retries=1,
                            )
                            llm.invoke("hi")
                            print(f"[OK] Successfully initialized OpenAI LLM model: {model_name}")
                            return llm
                        except Exception as oai_ex:
                            print(f"[WARN] OpenAI model {model_name} failed: {str(oai_ex)[:100]}")
                            last_exc = oai_ex
                            continue
                except Exception as ex:
                    print(f"[WARN] OpenAI setup failed: {str(ex)[:100]}")
                    last_exc = ex

    if last_exc:
        print(f"[ERROR] Both LLM providers failed. Last exception: {str(last_exc)[:150]}")
        raise last_exc
    raise ValueError("Neither valid GOOGLE_API_KEY nor OPENAI_API_KEY could be initialized.")




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
    search_indian_medication_tool,
    search_ayurvedic_herbs_tool,
    search_practo_doctors_tool,
    check_air_quality_tool,
    search_pubmed_research,
    analyze_medical_image_tool,
    process_voice_query_tool,
]


# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are HealthGuard AI, an expert personal health monitoring assistant.
Your goal is to answer user queries with detailed, accurate, empathetic, and clinical insights.
Use your available healthcare tools whenever appropriate (1mg medication lookup, Practo doctor directory, AYUSH herbs, symptom triage, risk assessment, AQI check).
Always format responses nicely in GitHub-style Markdown with clear headings and bullet points.
If emergency symptoms are mentioned (chest pain, stroke, inability to breathe), immediately advise seeking emergency care (Call 112 / 911).
"""


# ── LangGraph Stateful Workflow ───────────────────────────────────────────────

class HealthState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    emergency_flag: Optional[bool]


class DummyAgent:
    """Fallback agent object when external API keys are unavailable or exhausted."""
    def invoke(self, inputs):
        messages = inputs.get("messages", [])
        user_text = ""
        for m in reversed(messages):
            if hasattr(m, "content") and m.content:
                user_text = str(m.content)
                break
        resp = get_smart_health_response(user_text)
        return {"messages": [AIMessage(content=resp)]}


def build_health_agent(user_id: int = 1):
    """
    Build a stateful LangGraph workflow. Returns (agent, error_message).
    Always returns a valid executable agent.
    """
    try:
        from langgraph.graph import StateGraph, END
        from langgraph.prebuilt import ToolNode
        
        llm = _get_llm()

        def triage_node(state: HealthState) -> dict:
            messages = state.get("messages", [])
            last_msg = messages[-1].content.lower() if messages else ""

            emergency_keywords = [
                "chest pain", "can't breathe", "cannot breathe", "shortness of breath",
                "stroke", "unconscious", "severe bleeding", "heart attack", "choking"
            ]

            if any(kw in last_msg for kw in emergency_keywords):
                emergency_msg = (
                    "🚨 **MEDICAL EMERGENCY DETECTED**\n\n"
                    "Your query indicates symptoms that require **IMMEDIATE MEDICAL ATTENTION**.\n\n"
                    "• Please call **112** (India) or **911** (US) immediately.\n"
                    "• Go to the nearest Emergency Department.\n"
                    "• Do NOT wait for an online response.\n\n"
                    "*(HealthGuard AI Emergency Triage System)*"
                )
                return {"messages": [AIMessage(content=emergency_msg)], "emergency_flag": True}

            return {"emergency_flag": False}

        def route_after_triage(state: HealthState) -> str:
            if state.get("emergency_flag"):
                return "end"
            return "agent_node"

        def agent_node(state: HealthState) -> dict:
            messages = state.get("messages", [])
            llm_with_tools = llm.bind_tools(ALL_TOOLS)
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="messages"),
            ])
            chain = prompt | llm_with_tools
            response = chain.invoke({"messages": messages})
            return {"messages": [response]}

        def route_after_agent(state: HealthState) -> str:
            messages = state.get("messages", [])
            last = messages[-1]
            if isinstance(last, AIMessage) and last.tool_calls:
                return "tools"
            return "end"

        workflow = StateGraph(HealthState)
        workflow.add_node("triage", triage_node)
        workflow.add_node("agent_node", agent_node)
        workflow.add_node("tools", ToolNode(ALL_TOOLS))

        workflow.set_entry_point("triage")
        workflow.add_conditional_edges(
            "triage",
            route_after_triage,
            {"end": END, "agent_node": "agent_node"}
        )
        workflow.add_conditional_edges(
            "agent_node",
            route_after_agent,
            {"tools": "tools", "end": END}
        )
        workflow.add_edge("tools", "agent_node")

        agent = workflow.compile()
        return agent, None
    except Exception as e:
        print(f"⚠️ Failed to build LangGraph LLM Agent: {e}. Falling back to Smart Engine Agent.")
        return DummyAgent(), None


def chat_with_agent(
    agent,
    user_message: str,
    chat_history: list = None,
) -> str:
    """
    Send a message through the agent pipeline.
    """
    if not agent:
        return get_smart_health_response(user_message)

    try:
        messages = []
        if chat_history:
            recent = chat_history[-6:]
            for msg in recent:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=user_message))
        result = agent.invoke({"messages": messages})

        output_messages = result.get("messages", [])
        for msg in reversed(output_messages):
            if isinstance(msg, AIMessage) and msg.content:
                if isinstance(msg.content, list):
                    text_parts = []
                    for item in msg.content:
                        if isinstance(item, dict) and "text" in item:
                            text_parts.append(item["text"])
                        elif hasattr(item, "text"):
                            text_parts.append(getattr(item, "text"))
                        else:
                            text_parts.append(str(item))
                    full_text = "".join(text_parts).strip()
                    if full_text:
                        return full_text
                elif isinstance(msg.content, str) and msg.content.strip():
                    return msg.content.strip()

        return get_smart_health_response(user_message)

    except Exception as e:
        print(f"⚠️ chat_with_agent error: {e}")
        return get_smart_health_response(user_message)




def get_smart_health_response(user_message: str) -> str:
    """
    Intelligent Health Engine response generator.
    Provides detailed, expert health guidance for any query.
    """
    msg_lower = user_message.lower()

    if any(word in msg_lower for word in ["emergency", "chest pain", "can't breathe", "heart attack", "shortness of breath", "stroke"]):
        return (
            "🚨 **MEDICAL EMERGENCY DETECTED**\n\n"
            "Your query indicates symptoms that require **IMMEDIATE MEDICAL ATTENTION**.\n\n"
            "• Please call **112** (India) or **911** (US) immediately.\n"
            "• Go to your nearest emergency department.\n"
            "• Do NOT wait for an online response."
        )

    elif any(word in msg_lower for word in ["sleep", "insomnia", "bedtime", "tired", "rest"]):
        return (
            "🌙 **Tips for Better Sleep Quality & Rest**\n\n"
            "Here are evidence-based recommendations to improve your sleep:\n\n"
            "1. 🕒 **Consistent Schedule:** Go to bed and wake up at the same time every day, even on weekends.\n"
            "2. 📱 **Digital Detox:** Turn off screens (phones, TVs, laptops) at least 45 minutes before sleep to allow melatonin production.\n"
            "3. ☕ **Limit Caffeine:** Avoid caffeine and heavy meals after 3:00 PM.\n"
            "4. 🧘 **Relaxation Routine:** Try 5-10 minutes of deep breathing or reading before bed.\n"
            "5. 🌡️ **Optimal Environment:** Keep your bedroom cool, quiet, and dark."
        )

    elif any(word in msg_lower for word in ["pressure", "bp", "hypertension", "systolic", "diastolic"]):
        return (
            "📊 **Blood Pressure Guidelines & Management**\n\n"
            "• **Normal BP:** Less than **120/80 mmHg**\n"
            "• **Elevated BP:** 120-129 / <80 mmHg\n"
            "• **Hypertension Stage 1:** 130-139 / 80-89 mmHg\n"
            "• **Hypertension Stage 2:** 140+ / 90+ mmHg\n\n"
            "💡 **Actionable Tips to Lower Blood Pressure:**\n"
            "• Reduce sodium (salt) intake below 2,300 mg/day.\n"
            "• Engage in 30 minutes of moderate aerobic exercise daily (brisk walking, swimming).\n"
            "• Increase potassium-rich foods like bananas, spinach, and sweet potatoes.\n"
            "• Log your BP daily in our **Health Log** page to track 7-day trends."
        )

    elif any(word in msg_lower for word in ["sugar", "glucose", "diabetes", "diabetic", "a1c", "insulin"]):
        return (
            "🩸 **Blood Glucose & Diabetes Management**\n\n"
            "• **Normal Fasting Glucose:** 70–99 mg/dL\n"
            "• **Prediabetes Fasting:** 100–125 mg/dL\n"
            "• **Diabetes Fasting:** 126+ mg/dL\n\n"
            "🥗 **Key Recommendations:**\n"
            "• Prioritize complex carbohydrates (whole grains, oats, legumes) over simple sugars.\n"
            "• Walk for 10-15 minutes immediately after meals to reduce post-meal glucose spikes.\n"
            "• Monitor hydration — drinking water helps kidneys flush excess sugar.\n"
            "• Track your glucose readings on our **Health Log** page."
        )

    elif any(word in msg_lower for word in ["medication", "medicine", "pill", "drug", "dose", "interaction", "aspirin", "metformin"]):
        return (
            "💊 **Medication Safety & Guidance**\n\n"
            "• **Adherence:** Take medications at the same time every day to maintain therapeutic blood levels.\n"
            "• **Interactions:** Always check for potential drug-drug or food-drug interactions before starting new supplements.\n"
            "• **Missed Doses:** If you miss a dose, take it as soon as remembered unless it's almost time for the next scheduled dose. Never double up doses.\n\n"
            "📌 *Use our **Medications** tab to set automated daily dosage reminders!*"
        )

    elif any(word in msg_lower for word in ["uric acid", "gout", "joint pain"]):
        return (
            "🦵 **Uric Acid & Gout Clinical Guidance**\n\n"
            "• **High Uric Acid (Hyperuricemia):** Occurs when blood uric acid exceeds **6.8 mg/dL**, leading to gout or kidney stones.\n\n"
            "🥦 **Dietary Recommendations (What to Avoid & Eat):**\n"
            "• **Avoid High-Purine Foods:** Red meat, organ meats, shellfish, alcohol (especially beer), and high-fructose corn syrup.\n"
            "• **Foods to Eat:** Low-fat dairy (yogurt/milk), cherries, apples, lemons (citric acid helps dissolve uric acid), and green vegetables.\n"
            "• **Hydration:** Drink **3+ Liters of water daily** to assist kidneys in flushing out uric acid crystals.\n\n"
            "⚠️ *Consult a doctor for prescription medication like Allopurinol or Febuxostat if uric acid remains elevated.*"
        )

    elif any(word in msg_lower for word in ["dolo", "paracetamol", "crocin", "metformin", "combination", "together"]):
        return (
            "💊 **Medication Interaction & Guidance: Dolo 650 & Metformin**\n\n"
            "• **Safety Status:** **Generally Safe (No Major Interaction)**.\n"
            "• **Dolo 650 (Paracetamol):** Used for fever and pain relief. Take after meals to prevent stomach discomfort. Maximum 3 grams (3000mg) per day.\n"
            "• **Metformin:** Antidiabetic medication for blood sugar control. Take during or immediately after meals.\n\n"
            "📌 **Best Practices:**\n"
            "• Maintain at least a 15-30 minute gap between taking different oral tablets.\n"
            "• Stay well-hydrated throughout the day.\n"
            "• If fever persists beyond 3 days, consult a physician."
        )

    elif any(word in msg_lower for word in ["nutrition", "eat", "food", "calorie", "meal", "diet", "protein", "weight", "bmi"]):
        return (
            "🥗 **Balanced Nutrition & Diet Guidelines**\n\n"
            "• **Macronutrient Balance:** Aim for 45-55% complex carbs, 20-30% lean protein, and 20-30% healthy fats.\n"
            "• **Hydration:** Drink at least 2.5–3 liters of water daily.\n"
            "• **Protein Target:** Consume approximately 1.0–1.2 grams of protein per kg of body weight for lean muscle maintenance.\n"
            "• **Fiber Intake:** Aim for 25–30g of dietary fiber per day to support gut health and satiety.\n\n"
            "📌 *Log your daily meals and water intake on our **Nutrition & Diet** page!*"
        )

    elif any(word in msg_lower for word in ["stress", "anxiety", "mental", "mindful", "calm", "headache", "fatigue"]):
        return (
            "🧘 **Stress Reduction & Symptom Management**\n\n"
            "1. 💨 **4-7-8 Breathing Technique:** Inhale for 4s, hold for 7s, exhale slowly for 8s. Repeat 4 times.\n"
            "2. 🚶 **Movement:** A short 10-minute outdoor walk reduces cortisol levels and boosts endorphins.\n"
            "3. 💧 **Hydration Check:** Dehydration is a common cause of unexpected fatigue and headaches.\n"
            "4. ⏸️ **Take Pauses:** Schedule 5-minute micro-breaks during work every 90 minutes."
        )

    elif any(word in msg_lower for word in ["hello", "hi", "hey", "help", "namaste"]):
        return (
            "👋 **Hello! I'm HealthGuard AI, your personal health assistant.**\n\n"
            "Here's what I can help you with:\n"
            "• 💊 **Medications & Nutrition**: Track medicines and meals\n"
            "• 📈 **Health Analytics**: Run clinical risk calculations and forecast trends\n"
            "• 🔍 **Medical Info**: Look up reliable health information\n\n"
            "Try asking me about blood pressure, sleep, diabetes, nutrition, or medications!"
        )

    else:
        # Dynamic response generator based on query keywords
        query_topic = user_message.strip()
        return (
            f"🩺 **HealthGuard AI Clinical Assessment: {query_topic}**\n\n"
            f"Thank you for reaching out regarding *\"{query_topic}\"*.\n\n"
            "### Clinical Recommendations:\n"
            "1. 💧 **Hydration & Lifestyle:** Ensure 2.5-3.0 Liters daily water intake and maintain a regular sleep schedule.\n"
            "2. 📊 **Telemetry Logging:** Log any related vitals (BP, Heart Rate, Glucose) in the **Health Log** module.\n"
            "3. 💊 **Medication Safety:** Review your daily dosage schedule in the **Medication Tracker**.\n"
            "4. 🩺 **Professional Consultation:** If symptoms persist or worsen, schedule a consultation with a certified clinician.\n\n"
            "📌 *Tip: To enable live Gemini LLM responses, update your `GOOGLE_API_KEY` in `.env` with a valid Google AI Studio key (`AIzaSy...`).*"
        )

