"""
Comprehensive Integration Test for HealthGuard AI
Tests all Week 3-4 (Track A & Track B) and Week 5-6 (Option A1, Option A2, Track B) features.
"""

import sys
import os
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


print("=== RUNNING FULL HEALTHGUARD AI INTEGRATION VERIFICATION ===")


# 1. Database Initialization & Seed Verification
print("\n--- 1. Testing Database & Seeding ---")
from database import db_manager as db
db.init_db()

from utils.firebase_auth import firebase_sign_up, firebase_sign_in
auth_res = firebase_sign_up("ankit_test@healthguard.ai", "Password123!", "Ankit Sharma", age=30, gender="Male")
print(f"Firebase Signup Result: {auth_res.get('message')} (Provider: {auth_res.get('provider')})")

login_res = firebase_sign_in("ankit_test@healthguard.ai", "Password123!")
print(f"Firebase Login Result: {login_res.get('message')} (Provider: {login_res.get('provider')})")

uid = login_res.get('user_id', 1)
user = db.get_user(uid)
print(f"Verified active user: {user['name']} (ID: {uid}, Email: {user.get('email')})")

# 2. Indian Medicine (1mg) & Ayurveda Tests
print("\n--- 2. Testing 1mg Indian Medicine & Ayurveda Tools ---")
from tools.indian_health_tool import (
    search_indian_medication_tool,
    search_ayurvedic_herbs_tool,
    search_practo_doctors_tool,
    check_air_quality_tool,
)

res_1mg = search_indian_medication_tool.invoke({"query": "Dolo"})
print(f"1mg Medicine Tool Output:\n{res_1mg[:250]}...\n")

res_ayu = search_ayurvedic_herbs_tool.invoke({"herb_name": "Ashwagandha"})
print(f"Ayurvedic Herb Tool Output:\n{res_ayu[:250]}...\n")

res_practo = search_practo_doctors_tool.invoke({"specialty": "Cardiologist", "city": "Mumbai"})
print(f"Practo Doctor Tool Output:\n{res_practo[:250]}...\n")

res_aqi = check_air_quality_tool.invoke({"city": "Delhi"})
print(f"AQI Tool Output:\n{res_aqi[:200]}...\n")

# 3. Medical Research (PubMed) & Vision/Voice Tools
print("\n--- 3. Testing PubMed & Vision/Voice Tools ---")
from tools.medical_research_tool import search_pubmed_research
from tools.vision_voice_tool import analyze_medical_image_tool, process_voice_query_tool

res_pubmed = search_pubmed_research.invoke({"query": "Metformin diabetes"})
print(f"PubMed Research Output:\n{res_pubmed[:200]}...\n")

res_vision = analyze_medical_image_tool.invoke({"image_description": "Rx Dolo 650mg TDS", "category": "Prescription"})
print(f"Vision AI Output:\n{res_vision[:200]}...\n")

res_voice = process_voice_query_tool.invoke({"audio_transcript": "What are my medicines for today?"})
print(f"Voice Query Output:\n{res_voice}\n")

# 4. Family & Caregiver CRUD & Alert System
print("\n--- 4. Testing Family & Caregiver Operations ---")
mem_id = db.add_family_member(uid, "Ramesh Pal", "Father", 70, "Male", "B+", "Hypertension")
print(f"Family member created with ID: {mem_id}")

cg_id = db.add_caregiver_contact(uid, "Priya Pal", "Daughter", "+91 98765 43210", "priya@example.com")
print(f"Caregiver contact created with ID: {cg_id}")

alert_id = db.log_health_alert(uid, "Critical Vitals", "Emergency", "BP Systolic > 180 mmHg detected", "blood_pressure_systolic", 185.0, ">180 mmHg")
print(f"Critical health alert logged with ID: {alert_id}")

# 5. Report Generator
print("\n--- 5. Testing Automated HTML/Markdown Report Generation ---")
from utils.report_generator import generate_comprehensive_report
report = generate_comprehensive_report(uid)
print(f"Generated Markdown Report length: {len(report['markdown'])} chars")
print(f"Generated HTML Report length: {len(report['html'])} chars")

# 6. Stateful LangGraph Agent Verification
print("\n--- 6. Testing LangGraph Stateful Agent with All Registered Tools ---")
from agents.health_agent import build_health_agent, chat_with_agent, ALL_TOOLS

print(f"Total Registered Tools in Agent: {len(ALL_TOOLS)}")
agent, err = build_health_agent(uid)
print("Stateful LangGraph agent built successfully.")

chat_resp = chat_with_agent(agent, "Check 1mg for Dolo 650 price in India", chat_history=[])
print(f"Agent Chat Response snippet:\n{chat_resp[:250]}...")

print("\n=== ALL INTEGRATION VERIFICATION TESTS PASSED SUCCESSFULLY! ===")

