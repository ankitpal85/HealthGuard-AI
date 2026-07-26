import sys, os
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, '.')


print("=== STARTING WEEK 3-4 MODULE TESTS ===")

# 1. Test database nutrition logs
print("\n--- 1. Testing Database Nutrition Logs ---")
from database import db_manager as db
db.init_db()

uid = 1 # Assume user ID 1 exists or create if needed
user = db.get_user(uid)
if not user:
    uid = db.create_user("Test User", age=45, gender="Male", weight_kg=85, height_cm=175)
    print(f"Created new test user (ID: {uid})")
else:
    print(f"Using existing test user: {user['name']} (ID: {uid})")

# Log meal
log_id = db.log_nutrition(uid, "lunch", 550, protein_g=30, carbs_g=60, fat_g=15, food_items="Chicken rice and salad")
print(f"Meal logged with ID: {log_id}")

# Fetch meals
meals = db.get_nutrition_logs(uid, days=1)
print(f"Fetched {len(meals)} meal logs for today. First entry: {meals[0]['food_items']} ({meals[0]['calories']} kcal)")


# 2. Test analytics module
print("\n--- 2. Testing Analytics & Predictive Models ---")
from utils import analytics

# Log BP and BMI for testing risk assessment
db.log_health_metric(uid, "blood_pressure_systolic", 145.0, "mmHg", notes="Feeling slightly stressed")
db.log_health_metric(uid, "bmi", 27.8, "kg/m²")
db.log_health_metric(uid, "blood_glucose", 115.0, "mg/dL", notes="Fasting reading")
db.log_health_metric(uid, "steps", 4500, "steps")
db.log_health_metric(uid, "steps", 5200, "steps")
db.log_health_metric(uid, "steps", 4800, "steps")
db.log_health_metric(uid, "steps", 5000, "steps")

cvd_risk = analytics.calculate_cardiovascular_risk(uid)
print(f"CVD Risk: {cvd_risk['risk_percentage']}% | Category: {cvd_risk['risk_category']}")
print(f"CVD Advice: {cvd_risk['advice']}")

diab_risk = analytics.calculate_diabetes_risk(uid)
print(f"Diabetes Risk Status: {diab_risk['risk_category']}")
print(f"Diabetes Advice: {diab_risk['advice']}")


# 3. Test Anomaly Detection & Forecasting
print("\n--- 3. Testing Anomaly Detection & Forecasting ---")
anoms = analytics.detect_anomalies(uid, days=7)
print(f"Anomalies detected: {len(anoms)}")
for a in anoms[:2]:
    print(f"  - [{a['severity']}] {a['display_name']}: {a['value']} {a['unit']} -> {a['reason']}")

forecast = analytics.forecast_metric_trends(uid, "steps", days_history=7)
if "error" in forecast:
    print(f"Steps Forecast Error: {forecast['error']}")
else:
    print(f"Steps Forecast Trend: {forecast['insight']}")
    print(f"Next 3 days predicted steps:")
    for f in forecast['forecast'][:3]:
        print(f"  - {f['date']}: {f['value']} steps")


# 4. Test Clinical Tools
print("\n--- 4. Testing Clinical Tools ---")
from tools.clinical_tools import check_medication_interactions, analyze_symptoms

# Test interaction check
result_interaction = check_medication_interactions.invoke({"medications": ["Aspirin", "Warfarin"]})
print("Interaction check (Aspirin + Warfarin) output:")
print(result_interaction)

result_no_interaction = check_medication_interactions.invoke({"medications": ["Metformin", "Aspirin"]})
print("\nInteraction check (Metformin + Aspirin) output:")
print(result_no_interaction)

# Test triage
triage_emergency = analyze_symptoms.invoke({"symptoms": "chest pain and shortness of breath"})
print("\nTriage emergency output:")
print(triage_emergency[:200] + "...")

triage_cough = analyze_symptoms.invoke({"symptoms": "fever and dry cough"})
print("\nTriage cough output:")
print(triage_cough[:200] + "...")


# 5. Test Stateful LangGraph Agent Builder
print("\n--- 5. Testing Stateful LangGraph Builder ---")
from agents.health_agent import build_health_agent, chat_with_agent

agent, err = build_health_agent(uid)
if err:
    print(f"Agent building error: {err}")
else:
    print("Stateful LangGraph Health Agent compiled successfully!")
    
    # Test triage node interception by checking emergency symptoms
    # (Since we are using local logic in triage_node, this doesn't hit Gemini/OpenAI API)
    emergency_response = chat_with_agent(agent, "My husband is experiencing severe chest pain and breathlessness.", chat_history=[])
    print("\nEmergency Triage Check Response:")
    print(emergency_response)

print("\n=== ALL TESTS COMPLETED SUCCESSFULLY ===")
