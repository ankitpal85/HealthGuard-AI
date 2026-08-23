"""
HealthGuard AI — FastAPI Backend Server
Exposes REST APIs and SSE Streaming for the React Frontend.
"""

import os
import sys
import json
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Query, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BACKEND_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


load_dotenv()

import io
from database import db_manager as db
import agents.health_agent as ha_module
from utils.firebase_auth import firebase_sign_up, firebase_sign_in
from utils.report_generator import generate_pdf_report_bytes
from tools.clinical_tools import analyze_symptoms, run_risk_assessment_tool, generate_automated_report
from tools.indian_health_tool import (
    search_indian_medication_tool,
    search_ayurvedic_herbs_tool,
    search_practo_doctors_tool,
    check_air_quality_tool
)
from tools.vision_voice_tool import analyze_medical_image_tool, process_voice_query_tool, parse_medical_report_file

# Initialize Database on Server Startup
db.init_db()

app = FastAPI(
    title="HealthGuard AI API",
    description="Backend services for HealthGuard AI Personal Health Assistant",
    version="2.0.0"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Request Models ───────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None
    age: Optional[int] = 25
    gender: Optional[str] = "Prefer not to say"
    weight_kg: Optional[float] = 70.0
    height_cm: Optional[float] = 170.0
    blood_group: Optional[str] = "Unknown"

class UserLogin(BaseModel):
    email_or_name: str
    password: Optional[str] = None

class AuthRegisterRequest(BaseModel):
    email: str
    password: str
    name: str = "User"
    age: Optional[int] = 30
    gender: Optional[str] = "Male"
    blood_group: Optional[str] = "O+"

class AuthLoginRequest(BaseModel):
    email: str
    password: str

class AllergyUpdateRequest(BaseModel):
    allergies: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None



class MedicationCreate(BaseModel):
    user_id: int
    name: str
    dosage: str
    frequency: str
    time_slots: List[str]
    start_date: str
    end_date: Optional[str] = None
    notes: Optional[str] = None

class MedicationLogRequest(BaseModel):
    medication_id: int
    user_id: int
    scheduled_at: str
    taken_at: Optional[str] = None
    status: str = "taken"
    notes: Optional[str] = None

class VitalLogRequest(BaseModel):
    user_id: int
    metric_type: str
    value: float
    value2: Optional[float] = None
    unit: str
    recorded_at: Optional[str] = None
    notes: Optional[str] = None

class NutritionLogRequest(BaseModel):
    user_id: int
    meal_type: str
    food_items: str
    calories: float
    protein_g: Optional[float] = 0.0
    carbs_g: Optional[float] = 0.0
    fats_g: Optional[float] = 0.0
    water_ml: Optional[float] = 0.0
    date_str: Optional[str] = None

class ChatRequest(BaseModel):
    user_id: int
    message: str

class SymptomAnalyzeRequest(BaseModel):
    user_id: int
    symptoms: List[str]

class RiskAssessmentRequest(BaseModel):
    user_id: int
    condition: str

class SettingsRequest(BaseModel):
    provider: str
    api_key: str

class FamilyMemberRequest(BaseModel):
    user_id: int
    name: str
    relationship: str
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    medical_notes: Optional[str] = None

class CaregiverRequest(BaseModel):
    user_id: int
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None
    notify_critical: bool = True
    notify_missed: bool = True

class VisionRequest(BaseModel):
    user_id: int
    image_url: str
    prompt: Optional[str] = "Analyze medical image"

class VoiceRequest(BaseModel):
    user_id: int
    voice_text: str



# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "HealthGuard AI Backend API", "version": "2.0.0"}


# ── User & Auth Endpoints ─────────────────────────────────────────────────────

@app.post("/api/auth/register")
def auth_register(req: AuthRegisterRequest):
    res = firebase_sign_up(
        email=req.email,
        password=req.password,
        name=req.name,
        age=req.age or 30,
        gender=req.gender or "Male",
        blood_group=req.blood_group or "O+"
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message", "Registration failed"))
    return res

@app.post("/api/auth/login")
def auth_login(req: AuthLoginRequest):
    res = firebase_sign_in(email=req.email, password=req.password)
    if not res.get("success"):
        raise HTTPException(status_code=401, detail=res.get("message", "Authentication failed"))
    return res

@app.get("/api/users/{user_id}/allergies")
def get_allergies(user_id: int):
    allergies = db.get_user_allergies(user_id)
    return {"user_id": user_id, "allergies": allergies}

@app.post("/api/users/{user_id}/allergies")
def update_allergies(user_id: int, req: AllergyUpdateRequest):
    db.update_user_allergies(user_id, req.allergies)
    return {"success": True, "allergies": req.allergies}

@app.get("/api/users")
def get_users():
    users = db.get_all_users()
    return {"users": users}


@app.get("/api/users/{user_id}")
def get_user_profile(user_id: int):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{user_id}")
def update_user_profile(user_id: int, req: UserProfileUpdate):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    if update_data:
        db.update_user(user_id, **update_data)
    
    updated_user = db.get_user(user_id)
    return {"success": True, "user": updated_user}


@app.post("/api/users")
def create_user(user_data: UserCreate):
    try:
        user_id = db.create_user(
            name=user_data.name.strip(),
            email=user_data.email.strip() if user_data.email else None,
            age=user_data.age,
            gender=user_data.gender if user_data.gender != "Prefer not to say" else None,
            weight_kg=user_data.weight_kg,
            height_cm=user_data.height_cm,
            blood_group=user_data.blood_group if user_data.blood_group != "Unknown" else None,
        )
        return {"success": True, "user_id": user_id, "name": user_data.name.strip()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Dashboard Summary Endpoint ────────────────────────────────────────────────

@app.get("/api/dashboard/summary")
def get_dashboard_summary(user_id: int = Query(...)):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    adherence = db.get_adherence_rate(user_id, days=7)
    medications = db.get_medications(user_id, active_only=True)
    vitals_summary = db.get_health_metrics(user_id, days=7)
    recent_alerts = db.get_active_health_alerts(user_id, limit=5)
    
    return {
        "user": user,
        "adherence_7day": adherence,
        "active_medications_count": len(medications),
        "vitals_summary": vitals_summary,
        "recent_alerts": recent_alerts,
    }


# ── Medications Endpoints ─────────────────────────────────────────────────────

@app.get("/api/medications")
def get_medications(user_id: int = Query(...)):
    meds = db.get_medications(user_id, active_only=False)
    return {"medications": meds}

@app.post("/api/medications")
def add_medication(med: MedicationCreate):
    time_slots_str = json.dumps(med.time_slots) if isinstance(med.time_slots, list) else str(med.time_slots)
    med_id = db.add_medication(
        user_id=med.user_id,
        name=med.name,
        dosage=med.dosage,
        frequency=med.frequency,
        time_slots=time_slots_str,
        start_date=med.start_date,
        end_date=med.end_date,
        notes=med.notes
    )
    return {"success": True, "medication_id": med_id}

@app.post("/api/medications/log")
def log_medication(log: MedicationLogRequest):
    db.log_medication(
        medication_id=log.medication_id,
        user_id=log.user_id,
        scheduled_at=log.scheduled_at,
        taken_at=log.taken_at,
        status=log.status,
        notes=log.notes
    )
    return {"success": True}

@app.get("/api/medications/adherence")
def get_medication_adherence(user_id: int = Query(...), days: int = Query(7)):
    rate = db.get_adherence_rate(user_id, days=days)
    return {"user_id": user_id, "days": days, "adherence_rate": rate}


# ── Health Vitals Log Endpoints ───────────────────────────────────────────────

@app.get("/api/vitals")
def get_vitals(user_id: int = Query(...), metric_type: Optional[str] = Query(None)):
    if metric_type:
        logs = db.get_health_metrics(user_id, metric_type=metric_type)
    else:
        logs = db.get_health_metrics(user_id)
    return {"vitals": logs}

@app.post("/api/vitals")
def log_vital(vital: VitalLogRequest):
    metric_id = db.log_health_metric(
        user_id=vital.user_id,
        metric_type=vital.metric_type,
        value=vital.value,
        value2=vital.value2,
        unit=vital.unit,
        recorded_at=vital.recorded_at,
        notes=vital.notes
    )
    return {"success": True, "metric_id": metric_id}


# ── Nutrition Endpoints ───────────────────────────────────────────────────────

@app.get("/api/nutrition")
def get_nutrition_logs(user_id: int = Query(...), days: int = Query(7)):
    logs = db.get_nutrition_logs(user_id, days=days)
    summary = db.get_daily_macro_summary(user_id, days=days)
    return {"logs": logs, "summary": summary}

@app.post("/api/nutrition")
def log_nutrition(nutr: NutritionLogRequest):
    log_id = db.log_nutrition(
        user_id=nutr.user_id,
        meal_type=nutr.meal_type,
        food_items=nutr.food_items,
        calories=nutr.calories,
        protein_g=nutr.protein_g,
        carbs_g=nutr.carbs_g,
        fat_g=nutr.fats_g,
    )
    return {"success": True, "log_id": log_id}


# ── AI Chatbot Endpoints ──────────────────────────────────────────────────────

@app.get("/api/chat/history")
def get_chat_history(user_id: int = Query(...), limit: int = Query(50)):
    history = db.get_chat_history(user_id, limit=limit)
    return {"history": history}

@app.delete("/api/chat/history")
def clear_chat_history(user_id: int = Query(...)):
    db.clear_chat_history(user_id)
    return {"success": True}

@app.post("/api/chat")
def chat_with_ai(req: ChatRequest):
    user_id = req.user_id
    prompt = req.message.strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Empty prompt")

    db.save_chat_message(user_id, "user", prompt)
    history = db.get_chat_history(user_id, limit=10)

    try:
        agent, _ = ha_module.build_health_agent(user_id)
        response_text = ha_module.chat_with_agent(agent, prompt, history[:-1])
    except Exception as e:
        response_text = ha_module.get_smart_health_response(prompt)

    db.save_chat_message(user_id, "assistant", response_text)
    return {"role": "assistant", "content": response_text}

from fastapi import BackgroundTasks

@app.post("/api/chat/stream")
async def chat_stream_ai(req: ChatRequest, background_tasks: BackgroundTasks):
    """Zero-latency Server-Sent Events (SSE) Endpoint for real-time streaming."""
    user_id = req.user_id
    prompt = req.message.strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Empty prompt")

    background_tasks.add_task(db.save_chat_message, user_id, "user", prompt)

    async def event_generator():
        history = db.get_chat_history(user_id, limit=4)
        try:
            agent, _ = ha_module.build_health_agent(user_id)
            response_text = ha_module.chat_with_agent(agent, prompt, history)
        except Exception:
            response_text = ha_module.get_smart_health_response(prompt)

        background_tasks.add_task(db.save_chat_message, user_id, "assistant", response_text)

        words = response_text.split(" ")
        for i in range(0, len(words), 2):
            chunk = " ".join(words[i:i+2]) + " "
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.005)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")




# ── Risk & Clinical Analytics Endpoints ────────────────────────────────────────

@app.post("/api/symptoms/analyze")
def api_analyze_symptoms(req: SymptomAnalyzeRequest):
    symptom_str = ", ".join(req.symptoms)
    res = analyze_symptoms.invoke({"symptoms": symptom_str})
    return {"analysis": res}

@app.post("/api/risk-assessment")
def api_risk_assessment(req: RiskAssessmentRequest):
    user = db.get_user(req.user_id)
    vitals = db.get_health_metrics(req.user_id)
    res = run_risk_assessment_tool.invoke({"condition": req.condition, "patient_summary": str(vitals)})
    return {"risk_report": res}

@app.get("/api/reports/generate")
def api_generate_report(user_id: int = Query(...)):
    user = db.get_user(user_id)
    vitals = db.get_health_metrics(user_id)
    report = generate_automated_report.invoke({"patient_id": user_id, "patient_data": str(vitals)})
    return {"patient": user, "report": report}

@app.get("/api/reports/download-pdf")
def download_pdf_report(user_id: int = Query(...)):
    pdf_bytes = generate_pdf_report_bytes(user_id)
    user = db.get_user(user_id)
    patient_name = (user.get("name") if user else "Patient").replace(" ", "_")
    filename = f"HealthGuard_Clinical_Summary_{patient_name}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )



# ── Indian Health & AYUSH Endpoints ───────────────────────────────────────────

@app.get("/api/indian-health/medications")
def search_indian_meds(query: str = Query(...)):
    res = search_indian_medication_tool.invoke({"query": query})
    return {"result": res}

@app.get("/api/indian-health/ayurveda")
def search_ayurveda(query: str = Query(...)):
    res = search_ayurvedic_herbs_tool.invoke({"query": query})
    return {"result": res}

@app.get("/api/indian-health/doctors")
def search_practo(specialty: str = Query("General Physician"), city: str = Query("Mumbai")):
    res = search_practo_doctors_tool.invoke({"specialty": specialty, "city": city})
    return {"result": res}

@app.get("/api/indian-health/aqi")
def get_aqi(city: str = Query("Delhi")):
    res = check_air_quality_tool.invoke({"city": city})
    return {"result": res}


# ── Family & Caregivers Endpoints ─────────────────────────────────────────────

@app.get("/api/family")
def get_family_members(user_id: int = Query(...)):
    members = db.get_family_members(user_id)
    return {"family_members": members}

@app.post("/api/family")
def add_family_member(req: FamilyMemberRequest):
    mem_id = db.add_family_member(
        user_id=req.user_id,
        name=req.name,
        relationship=req.relationship,
        age=req.age,
        gender=req.gender,
        blood_group=req.blood_group,
        medical_notes=req.medical_notes or ""
    )
    return {"success": True, "family_member_id": mem_id}

@app.get("/api/caregivers")
def get_caregivers(user_id: int = Query(...)):
    contacts = db.get_caregiver_contacts(user_id)
    return {"caregivers": contacts}

@app.post("/api/caregivers")
def add_caregiver(req: CaregiverRequest):
    cg_id = db.add_caregiver_contact(
        user_id=req.user_id,
        name=req.name,
        relationship=req.relationship,
        phone=req.phone,
        email=req.email or "",
        notify_critical=1 if req.notify_critical else 0,
        notify_missed=1 if req.notify_missed else 0
    )
    return {"success": True, "caregiver_id": cg_id}



# ── Vision & Voice AI Endpoints ───────────────────────────────────────────────

@app.post("/api/vision/upload-report")
async def upload_medical_report(user_id: int = Query(1), file: UploadFile = File(...)):
    file_bytes = await file.read()
    result = parse_medical_report_file(file_bytes, file.filename or "medical_report.pdf", user_id=user_id)
    return result

@app.post("/api/vision/analyze")
async def analyze_vision_image(req: VisionRequest):
    res = analyze_medical_image_tool.invoke({"image_path": req.image_url, "prompt": req.prompt or "Analyze medical image"})
    return {"analysis": res}

@app.post("/api/voice/process")
def process_voice(req: VoiceRequest):
    res = process_voice_query_tool.invoke({"voice_text": req.voice_text})
    return {"result": res}




# ── Settings Endpoint ─────────────────────────────────────────────────────────

@app.post("/api/settings")
def update_settings(req: SettingsRequest):
    os.environ["LLM_PROVIDER"] = req.provider
    if req.provider == "gemini":
        os.environ["GOOGLE_API_KEY"] = req.api_key.strip()
    else:
        os.environ["OPENAI_API_KEY"] = req.api_key.strip()
    return {"success": True, "provider": req.provider}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
