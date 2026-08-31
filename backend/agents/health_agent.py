"""
HealthGuard AI — LangChain Health Agent
Orchestrates all healthcare tools with a conversational LLM backbone.
Uses a stateful LangGraph pipeline to handle emergency triage and clinical tools.
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()
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

def _is_valid_key(key: str, provider: str) -> bool:
    if not key or not isinstance(key, str):
        return False
    k = key.strip()
    if k.startswith("your_") or "your_key" in k or k == "your_google_api_key_here" or k == "your_openai_api_key_here":
        return False
    if provider == "openai":
        return k.startswith("sk-")
    return len(k) >= 8

def _get_llm():
    """Return the configured LLM with automatic multi-provider (Gemini <-> OpenAI) fallback."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    google_key = os.getenv("GOOGLE_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    valid_google = _is_valid_key(google_key, "gemini")
    valid_openai = _is_valid_key(openai_key, "openai")

    if provider == "gemini" and not valid_google and valid_openai:
        provider = "openai"

    providers = [provider]
    if provider == "gemini" and valid_openai:
        providers.append("openai")
    elif provider == "openai" and valid_google:
        providers.append("gemini")

    last_exc = None
    for p in providers:
        if p == "gemini" and valid_google:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                preferred_models = [
                    "models/gemini-3.6-flash",
                    "models/gemini-3.5-flash",
                    "models/gemini-flash-latest",
                    "models/gemini-pro-latest",
                    "gemini-2.5-flash",
                    "gemini-1.5-flash",
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
                        print(f"[OK] Initialized Gemini LLM model: {model_name}")
                        return llm
                    except Exception as model_ex:
                        print(f"[WARN] Gemini model {model_name} failed: {str(model_ex)[:100]}")
                        last_exc = model_ex
                        continue
            except Exception as ex:
                print(f"[WARN] Google Generative AI import/setup failed: {str(ex)[:100]}")
                last_exc = ex
        elif p == "openai" and valid_openai:
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
                        print(f"[OK] Initialized OpenAI LLM model: {model_name}")
                        return llm
                    except Exception as oai_ex:
                        print(f"[WARN] OpenAI model {model_name} failed: {str(oai_ex)[:100]}")
                        last_exc = oai_ex
                        continue
            except Exception as ex:
                print(f"[WARN] OpenAI setup failed: {str(ex)[:100]}")
                last_exc = ex

    if last_exc:
        print(f"[WARN] Both LLM providers failed. Falling back to Smart Engine. Reason: {str(last_exc)[:150]}")
        raise last_exc
    raise ValueError("Neither valid GOOGLE_API_KEY nor OPENAI_API_KEY is configured.")




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

SYSTEM_PROMPT = """You are HealthGuard AI, a concise and accurate medical health assistant.

DOMAIN RULE (NON-NEGOTIABLE):
- Answer ONLY medical/health topics: symptoms, diseases, medications, nutrition, fitness, mental health, wellness.
- For ANY non-medical question, respond EXACTLY: "⚠️ **Domain Restriction** — I only answer medical and health questions. Please ask a health-related question!"
- Do NOT connect non-medical topics to health just to answer them.

ANSWER FORMAT RULES (STRICTLY FOLLOW):
1. NEVER repeat, restate, echo, or acknowledge the user's question. Do NOT write "Thank you for asking", "You asked about", "Regarding your query", or any similar phrase.
2. Start your response DIRECTLY with the answer — no preamble, no intro.
3. Be CONCISE and to-the-point. Give only what is clinically necessary. Avoid padding or filler text.
4. Use simple Markdown (short bullet points or numbered steps) for readability. Avoid excessive headings.
5. For emergencies (chest pain, stroke, can't breathe), immediately say: call 112 (India) / 911 (US) — go to hospital now.
6. Use healthcare tools (medication lookup, symptom analysis, risk assessment) when relevant.
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
        print(f"[WARN] Failed to build LangGraph LLM Agent: {e}. Falling back to Smart Engine Agent.")
        return DummyAgent(), None


# ── Hardcoded domain-restriction reply ───────────────────────────────────────
DOMAIN_RESTRICTION_MSG = (
    "⚠️ **Domain Restriction Notice**\n\n"
    "I am specialized strictly as a **Medical & Healthcare Assistant** (HealthGuard AI).\n\n"
    "I can only assist with questions related to:\n"
    "• Medical conditions, symptoms & diseases\n"
    "• Medications, supplements & dosages\n"
    "• Nutrition, diet & physical vitals\n"
    "• Healthcare & doctor guidance\n\n"
    "Please ask a health or medical-related question!"
)


def chat_with_agent(
    agent,
    user_message: str,
    chat_history: list = None,
) -> str:
    """
    Send a message through the agent pipeline.
    Non-medical queries are rejected BEFORE reaching the LLM.
    """
    # ── Gate: block all non-medical queries immediately ───────────────────────
    if not is_health_query(user_message):
        return DOMAIN_RESTRICTION_MSG

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




def is_health_query(user_message: str) -> bool:
    """Check if the user message contains any medical, health, wellness, or clinical keywords."""
    msg_lower = user_message.lower()
    health_keywords = [
        # Medical & Vitals
        "health", "medical", "doctor", "medicine", "medication", "pill", "drug", "dose", "dosage",
        "symptom", "disease", "illness", "infection", "pain", "fever", "cough", "cold", "flu",
        "virus", "headache", "stomach", "skin", "blood", "pressure", "bp", "sugar", "glucose",
        "diabetes", "diabetic", "heart", "kidney", "liver", "lung", "brain", "sleep", "insomnia",
        "tired", "fatigue", "stress", "anxiety", "mental", "depression", "diet", "nutrition",
        "food", "calorie", "protein", "carbs", "fat", "weight", "bmi", "exercise", "workout",
        "fitness", "water", "hydration", "uric acid", "gout", "thyroid", "cholesterol", "pulse",
        "vitals", "hospital", "clinic", "treatment", "cure", "remedy", "ayurved", "herb",
        "pharmacy", "prescription", "lab", "test", "scan", "mri", "xray", "ecg", "ultrasound",
        "cancer", "tumor", "allergy", "injury", "wound", "fracture", "surgery", "patient",
        "physician", "nurse", "dermatolog", "cardiolog", "neurolog", "pediatric", "orthoped",
        "gastro", "ophtalm", "ent", "psychiat", "teeth", "dental", "eye", "ear", "throat",
        "belly", "chest", "leg", "arm", "back", "neck", "joint", "muscle", "bone", "hair",
        "body", "healthguard", "dolo", "paracetamol", "crocin", "metformin", "aspirin",
        "ibuprofen", "antibiotic", "vitamin", "supplement", "vaccine", "vaccination",
        "pregnancy", "period", "cramp", "nausea", "vomiting", "diarrhea", "constipation",
        "acne", "rash", "itch", "swelling", "spo2", "oxygen", "pulse",
        # Hindi / Hinglish medical words
        "bukhar", "dard", "sar", "pet", "bimari", "elaj", "dawai", "dava", "sehat", "sir", "gala",
        "khana", "motapa", "vazan", "kamar", "nind", "tavcha", "aankh", "kaan", "paani", "upchar",
        "sujan", "khansi", "zukam",
        # Greetings & Assistant Info
        "hello", "hi", "hey", "help", "namaste", "good morning", "good evening", "who are you",
        "what can you do", "capabilities"
    ]
    return any(kw in msg_lower for kw in health_keywords)


def get_smart_health_response(user_message: str) -> str:
    """
    Intelligent Health Engine response generator.
    Provides detailed, expert health guidance for medical queries,
    and strictly refuses non-medical queries.
    """
    if not is_health_query(user_message):
        return (
            "⚠️ **Domain Restriction Notice**\n\n"
            "I am specialized strictly as a **Medical & Healthcare Assistant** (HealthGuard AI).\n\n"
            "I can only assist with questions related to:\n"
            "• Medical conditions, symptoms & diseases\n"
            "• Medications, supplements & dosages\n"
            "• Nutrition, diet & physical vitals\n"
            "• Healthcare & doctor guidance\n\n"
            "Please ask a health or medical-related question!"
        )

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
            "🌙 **Better Sleep Tips**\n"
            "1. 🕒 Fixed sleep/wake time daily — even weekends.\n"
            "2. 📱 No screens 45 min before bed (blocks melatonin).\n"
            "3. ☕ No caffeine or heavy meals after 3 PM.\n"
            "4. 🧘 5–10 min deep breathing or reading before bed.\n"
            "5. 🌡️ Keep room cool, dark, and quiet."
        )

    elif any(word in msg_lower for word in ["pressure", "bp", "hypertension", "systolic", "diastolic"]):
        return (
            "📊 **Blood Pressure Reference**\n"
            "• Normal: < 120/80 mmHg\n"
            "• Elevated: 120–129 / <80\n"
            "• Hypertension Stage 1: 130–139 / 80–89\n"
            "• Hypertension Stage 2: ≥ 140/90 (consult doctor)\n\n"
            "**To lower BP:** Reduce salt (<2,300 mg/day), 30 min brisk walk daily, eat potassium-rich foods (banana, spinach)."
        )

    elif any(word in msg_lower for word in ["sugar", "glucose", "diabetes", "diabetic", "a1c", "insulin"]):
        return (
            "🩸 **Blood Glucose Reference**\n"
            "• Normal fasting: 70–99 mg/dL\n"
            "• Prediabetes: 100–125 mg/dL\n"
            "• Diabetes: ≥ 126 mg/dL\n\n"
            "**Tips:** Prefer whole grains/oats over sugar; walk 10–15 min after meals; stay well-hydrated."
        )

    elif any(word in msg_lower for word in ["medication", "medicine", "pill", "drug", "dose", "interaction", "aspirin", "metformin"]):
        return (
            "💊 **Medication Safety**\n"
            "• Take medicines at the same time daily for consistent blood levels.\n"
            "• Check for drug-drug or food-drug interactions before adding supplements.\n"
            "• Missed dose: take it as soon as you remember — never double up."
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
            "🥗 **Nutrition Basics**\n"
            "• Macros: 45–55% complex carbs, 20–30% protein, 20–30% healthy fats.\n"
            "• Water: 2.5–3 liters/day.\n"
            "• Protein: ~1.0–1.2 g per kg body weight daily.\n"
            "• Fiber: 25–30 g/day for gut health."
        )

    elif any(word in msg_lower for word in ["stress", "anxiety", "mental", "mindful", "calm", "headache", "fatigue"]):
        return (
            "🧘 **Stress & Fatigue Relief**\n"
            "1. 💨 4-7-8 breathing: inhale 4s → hold 7s → exhale 8s. Repeat 4×.\n"
            "2. 🚶 10-min outdoor walk lowers cortisol and boosts mood.\n"
            "3. 💧 Check hydration — dehydration causes headaches and fatigue.\n"
            "4. ⏸️ Take 5-min breaks every 90 min during work."
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

    # ── Fever / Bukhar ────────────────────────────────────────────────────────
    elif any(word in msg_lower for word in ["fever", "bukhar", "temperature", "tapman", "high temp", "body heat", "103", "104", "101", "38°", "39°", "40°"]):
        return (
            "🌡️ **Fever — Clinical Guidance**\n\n"
            "**Normal body temperature:** 36.1°C – 37.2°C (97°F – 99°F)\n\n"
            "### 🔢 Fever Severity Scale:\n"
            "| Temperature | Level |\n"
            "|---|---|\n"
            "| 37.5°C – 38.4°C (99.5°F – 101°F) | Low-grade fever |\n"
            "| 38.5°C – 39.4°C (101.3°F – 102.9°F) | Moderate fever |\n"
            "| 39.5°C+ (103°F+) | High fever — seek medical attention |\n"
            "| 40°C+ (104°F+) | 🚨 **Emergency** — go to hospital immediately |\n\n"
            "### ✅ Immediate Steps:\n"
            "1. 💊 **Paracetamol (Dolo 650 / Crocin):** 500–650 mg every 4–6 hours (max 4g/day). Take after meals.\n"
            "2. 💧 **Hydration:** Drink **3+ liters of water/ORS/coconut water** — fever causes rapid fluid loss.\n"
            "3. 🧊 **Cool Compress:** Apply a damp cloth on forehead, armpits, and neck to reduce temperature.\n"
            "4. 👕 **Light Clothing:** Wear lightweight, breathable cotton clothes. Avoid heavy blankets.\n"
            "5. 🌡️ **Monitor:** Check temperature every 4 hours and log in the **Health Log** module.\n\n"
            "### ⚠️ Consult a Doctor Immediately If:\n"
            "• Fever is above **39.5°C (103°F)** and not reducing with medication\n"
            "• Fever lasts more than **3 days**\n"
            "• Accompanied by **severe headache, neck stiffness, rash, or difficulty breathing**\n"
            "• Fever in **infants under 3 months** (any fever = emergency)\n\n"
            "📌 *Log your temperature readings in the **Health Log** to track trends over 24–48 hours.*"
        )

    # ── Cough / Cold / Flu / Zukam ────────────────────────────────────────────
    elif any(word in msg_lower for word in ["cough", "cold", "flu", "runny nose", "sore throat", "khansi", "zukam", "gala", "naak", "congestion", "sneezing"]):
        return (
            "🤧 **Cough, Cold & Flu — Clinical Guidance**\n\n"
            "### Common Causes:\n"
            "• **Viral cold** — most colds are caused by rhinovirus (resolves in 7–10 days)\n"
            "• **Influenza (Flu)** — more severe with body ache, high fever\n"
            "• **Allergic rhinitis** — sneezing + runny nose triggered by dust/pollen\n\n"
            "### ✅ Recommended Treatment:\n"
            "1. 💊 **For Fever + Body Ache:** Paracetamol (Dolo 650) 500–650 mg every 6 hours\n"
            "2. 🫁 **For Congestion:** Steam inhalation 2–3 times daily (add tulsi/eucalyptus leaves)\n"
            "3. 🍯 **For Sore Throat:** Warm salt water gargles 3x/day + honey + ginger tea\n"
            "4. 💊 **For Runny Nose:** Cetirizine (10 mg, once at night) for allergic symptoms\n"
            "5. 💧 **Hydration:** Warm soups, herbal teas, and 3+ liters of warm water daily\n"
            "6. 😴 **Rest:** Minimum 8 hours of sleep to allow immune system recovery\n\n"
            "### ⚠️ See a Doctor If:\n"
            "• Symptoms last more than **10 days** or worsen after day 3\n"
            "• High fever (above 39°C) with cold symptoms\n"
            "• Yellow/green mucus with facial pain (may indicate sinusitis)\n"
            "• Difficulty breathing or chest tightness\n\n"
            "🌿 *Ayurvedic Tip: Kadha (Tulsi + Ginger + Black pepper + Clove) is effective for early cold relief.*"
        )

    # ── Vomiting / Nausea / Diarrhea ─────────────────────────────────────────
    elif any(word in msg_lower for word in ["vomit", "nausea", "diarrhea", "loose motion", "ulti", "dast", "stomach ache", "pet dard", "indigestion", "acidity", "gastric"]):
        return (
            "🤢 **Vomiting, Nausea & Stomach Issues — Clinical Guidance**\n\n"
            "### ✅ Immediate Steps:\n"
            "1. 💧 **ORS (Oral Rehydration Solution):** Mix 1 sachet in 1L water. Sip every 15 minutes to prevent dehydration.\n"
            "2. 🍚 **BRAT Diet:** Banana, Rice, Applesauce, Toast — gentle on an irritated stomach.\n"
            "3. 💊 **For Nausea:** Domperidone (10 mg) or Ondansetron — take 30 minutes before meals.\n"
            "4. 💊 **For Loose Motions:** ORS + Zinc supplement (20 mg/day) accelerates gut recovery.\n"
            "5. 🚫 **Avoid:** Spicy food, dairy, alcohol, and caffeine until fully recovered.\n"
            "6. 🌱 **Natural Remedy:** Ginger tea or ½ tsp ajwain (carom seeds) with warm water for cramps.\n\n"
            "### ⚠️ Seek Emergency Care If:\n"
            "• Blood in vomit or stool\n"
            "• Severe dehydration (no urine for 8+ hours, sunken eyes, extreme dizziness)\n"
            "• High fever **with** vomiting — could indicate food poisoning or appendicitis\n"
            "• Vomiting in **pregnant women** (hyperemesis) — immediate medical attention needed\n\n"
            "📌 *If symptoms persist beyond 48 hours, consult a doctor for stool culture or endoscopy.*"
        )

    # ── Allergy / Rash / Skin ─────────────────────────────────────────────────
    elif any(word in msg_lower for word in ["allergy", "rash", "itch", "skin", "hives", "acne", "eczema", "urticaria", "khujli", "daane", "tavcha"]):
        return (
            "🩹 **Skin Allergy & Rash — Clinical Guidance**\n\n"
            "### Common Causes:\n"
            "• **Food allergy** — nuts, shellfish, dairy, eggs\n"
            "• **Contact dermatitis** — soaps, detergents, metals (nickel), latex\n"
            "• **Drug reaction** — new medications\n"
            "• **Insect bites** — mosquitoes, bedbugs\n"
            "• **Heat rash / Prickly heat** — blocked sweat glands\n\n"
            "### ✅ Immediate Steps:\n"
            "1. 💊 **Antihistamine:** Cetirizine 10 mg or Loratadine 10 mg once daily for itching/hives\n"
            "2. 🧴 **Topical:** Calamine lotion or 1% Hydrocortisone cream for localized itching\n"
            "3. 🚿 **Wash Area:** Rinse with cool water and mild soap to remove allergen\n"
            "4. 🧊 **Cool Compress:** Apply for 10–15 minutes to soothe inflammation\n"
            "5. 🚫 **Avoid Scratching:** Prevents secondary bacterial infection\n\n"
            "### ⚠️ Emergency (Anaphylaxis) Signs — Call 112 Immediately:\n"
            "• Swelling of lips, tongue, or throat\n"
            "• Difficulty breathing after allergen exposure\n"
            "• Sudden drop in BP with dizziness\n\n"
            "📌 *See a dermatologist if rash persists > 7 days or spreads rapidly.*"
        )

    # ── Body Pain / Muscle Pain / Backache ────────────────────────────────────
    elif any(word in msg_lower for word in ["body pain", "muscle pain", "backache", "back pain", "body ache", "badan dard", "kamar dard", "joint", "arthritis"]):
        return (
            "💪 **Body Pain & Muscle Ache — Clinical Guidance**\n\n"
            "### Common Causes:\n"
            "• Viral infection (fever-related body ache)\n"
            "• Muscle overuse or poor posture\n"
            "• Vitamin D / Magnesium deficiency\n"
            "• Arthritis or inflammatory conditions\n\n"
            "### ✅ Treatment Steps:\n"
            "1. 💊 **Pain Relief:** Ibuprofen 400 mg (after meals) or Paracetamol 650 mg every 6 hours\n"
            "2. 🔥 **Hot Compress:** Apply warm pad on affected area for 15–20 minutes, 3x daily\n"
            "3. 🧘 **Gentle Stretching:** Light stretches and yoga improve blood flow and reduce stiffness\n"
            "4. 💊 **For Deficiency-Related Pain:** Vitamin D3 (60,000 IU weekly) + Magnesium (300 mg/day)\n"
            "5. 💧 **Hydration:** Dehydration worsens muscle cramps — drink 3+ liters daily\n"
            "6. 😴 **Rest:** Allow muscles to recover with adequate sleep\n\n"
            "### ⚠️ Consult a Doctor If:\n"
            "• Pain is severe, localized, and worsening\n"
            "• Accompanied by swelling, redness, or loss of movement\n"
            "• Chest or left-arm pain (rule out cardiac cause)\n\n"
            "📌 *Log pain levels in **Health Log** and track patterns over 7 days.*"
        )

    # ── Cholesterol ───────────────────────────────────────────────────────────
    elif any(word in msg_lower for word in ["cholesterol", "ldl", "hdl", "triglyceride", "lipid", "fatty liver"]):
        return (
            "🫀 **Cholesterol & Lipid Profile — Clinical Guidance**\n\n"
            "### 📊 Target Levels (Indian Guidelines):\n"
            "| Marker | Optimal | Borderline High | High Risk |\n"
            "|---|---|---|---|\n"
            "| Total Cholesterol | < 200 mg/dL | 200–239 | ≥ 240 |\n"
            "| LDL (Bad) | < 100 mg/dL | 130–159 | ≥ 160 |\n"
            "| HDL (Good) | > 60 mg/dL | 40–59 | < 40 |\n"
            "| Triglycerides | < 150 mg/dL | 150–199 | ≥ 200 |\n\n"
            "### ✅ Key Recommendations:\n"
            "1. 🥗 **Diet:** Reduce saturated fats (fried food, red meat, full-fat dairy). Increase oats, nuts, flaxseeds, olive oil.\n"
            "2. 🚶 **Exercise:** 30 minutes brisk walk 5x/week raises HDL and lowers LDL.\n"
            "3. 🚭 **Quit Smoking:** Smoking reduces HDL and damages arterial walls.\n"
            "4. 🐟 **Omega-3:** Fish oil (1–2g/day) or flaxseed significantly reduces triglycerides.\n"
            "5. 💊 **Statins:** If LDL > 160 with risk factors, doctor may prescribe Atorvastatin/Rosuvastatin.\n\n"
            "📌 *Get a full lipid panel test every 6 months and log results in **Health Log**.*"
        )

    else:
        return (
            "🩺 Please describe your symptoms or health concern in more detail so I can give you accurate guidance.\n\n"
            "If symptoms are severe or persistent, consult a doctor promptly."
        )


