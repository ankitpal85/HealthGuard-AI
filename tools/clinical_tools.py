"""
Clinical Tools for HealthGuard AI
Provides drug-drug interactions check, symptom triaging, and health analytics tools.
"""

from langchain.tools import tool
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db
from utils import analytics

# Predefined interaction database
DRUG_INTERACTIONS = {
    ("aspirin", "warfarin"): "🚨 **Severe Interaction**: High risk of serious bleeding. Both medications decrease blood clotting capacity. Concurrent use requires active medical monitoring and dosage adjustments.",
    ("aspirin", "ibuprofen"): "⚠️ **Moderate Interaction**: Ibuprofen can interfere with the anti-platelet effect of low-dose aspirin, reducing its cardioprotective benefits, and increases the risk of gastrointestinal ulcers.",
    ("ibuprofen", "naproxen"): "⚠️ **Moderate Interaction**: Combining multiple NSAIDs increases the risk of gastrointestinal bleeding, kidney strain, and stomach ulcers. Use only one NSAID at a time.",
    ("metformin", "alcohol"): "🚨 **Severe Interaction**: Metformin combined with alcohol increases the risk of Lactic Acidosis, a rare but life-threatening complication. Limit alcohol intake.",
    ("lisinopril", "spironolactone"): "⚠️ **Moderate Interaction**: Both medications increase blood potassium levels. Co-administration can lead to hyperkalemia (abnormally high potassium), which affects heart rhythm.",
    ("warfarin", "ibuprofen"): "🚨 **Severe Interaction**: Ibuprofen can cause gastrointestinal irritation and bleeding, and increases the anticoagulant effect of warfarin, dramatically increasing bleeding risk.",
    ("sildenafil", "nitroglycerin"): "🛑 **Contraindicated / Severe Danger**: Can cause a life-threatening, sudden drop in blood pressure. Avoid concurrent use completely. If chest pain occurs after taking sildenafil, do not use nitroglycerin; call emergency services immediately.",
}


@tool
def check_medication_interactions(medications: list) -> str:
    """
    Check if there are any known drug-drug interactions in a list of medications.

    Args:
        medications: List of medication names (e.g. ['Aspirin', 'Warfarin']).

    Returns:
        Interaction analysis report.
    """
    if not medications or len(medications) < 2:
        return "Please provide at least two medications to check for interactions."

    found_interactions = []
    meds_clean = [m.lower().strip() for m in medications]

    # Check all pairs
    for i in range(len(meds_clean)):
        for j in range(i + 1, len(meds_clean)):
            med1, med2 = meds_clean[i], meds_clean[j]
            pair1 = (med1, med2)
            pair2 = (med2, med1)

            interaction = DRUG_INTERACTIONS.get(pair1) or DRUG_INTERACTIONS.get(pair2)
            if interaction:
                found_interactions.append(f"- **{medications[i]}** + **{medications[j]}**:\n  {interaction}")

    # General MedlinePlus reference
    footer = "\n\n*Note: This check is based on a clinical ruleset of common drugs. For a complete check, consult a pharmacist or visit https://medlineplus.gov/druginformation.html*"

    if found_interactions:
        return "⚠️ **Medication Interactions Detected:**\n\n" + "\n\n".join(found_interactions) + footer
    else:
        return "✅ **No major interactions found** among the provided medications in our clinical ruleset.\n\n*Always verify with your doctor or pharmacist, as new interactions or personal health factors may apply.*" + footer


@tool
def analyze_symptoms(symptoms: str) -> str:
    """
    Analyze user-reported symptoms and provide triage recommendations (clinical triage).

    Args:
        symptoms: Description of the symptoms (e.g. 'chest pain', 'fever and headache').

    Returns:
        Structured guidance (emergency, see doctor, self-care).
    """
    sym_lower = symptoms.lower()

    # 1. Critical Symptoms Check
    emergency_keywords = ["chest pain", "shortness of breath", "difficulty breathing", "severe chest pressure",
                          "numbness in arm", "slurred speech", "face drooping", "loss of consciousness", "severe allergic reaction"]
    
    for kw in emergency_keywords:
        if kw in sym_lower:
            return (
                "🚨 **EMERGENCY WARNING DETECTED** 🚨\n\n"
                "Your reported symptom (**" + kw + "**) indicates a potentially life-threatening condition.\n\n"
                "⚠️ **What to do:**\n"
                "1. **Call 112 (India) or 911 (US) immediately.**\n"
                "2. Go to the nearest emergency department.\n"
                "3. Do not drive yourself; call an ambulance.\n\n"
                "*Disclaimer: HealthGuard AI does not provide emergency medical diagnosis. Seek professional medical help immediately.*"
            )

    # 2. General Triage Heuristics
    guidance = "🔍 **Symptom Assessment & Guidance**\n\n"
    
    if "fever" in sym_lower:
        guidance += "🤒 **Fever detected:**\n"
        guidance += "- Ensure plenty of rest and hydration.\n"
        guidance += "- Monitor temperature. If fever exceeds 103°F (39.4°C) or lasts more than 3 days, see a doctor.\n"
        guidance += "- Seek immediate help if accompanied by a stiff neck, confusion, or breathing difficulty.\n\n"
    
    if "headache" in sym_lower:
        guidance += "🤕 **Headache detected:**\n"
        guidance += "- Rest in a quiet, dark room. Stay hydrated.\n"
        guidance += "- Seek emergency care if it is a sudden, severe headache ('thunderclap' headache) or accompanied by fever, neck stiffness, or confusion.\n\n"
        
    if "cough" in sym_lower or "sore throat" in sym_lower:
        guidance += "🗣️ **Respiratory symptoms (Cough/Sore Throat):**\n"
        guidance += "- Drink warm liquids (tea, honey). Use a humidifier.\n"
        guidance += "- Consult a doctor if you experience wheezing, blood in sputum, or if symptoms persist beyond 10 days.\n\n"

    if "stomach" in sym_lower or "abdominal" in sym_lower or "nausea" in sym_lower:
        guidance += "🤢 **Gastrointestinal symptoms:**\n"
        guidance += "- Drink clear fluids in small sips. Stick to bland foods (BRAT diet).\n"
        guidance += "- Seek immediate medical attention for severe, sudden abdominal pain, high fever, or blood in vomit/stool.\n\n"

    if len(guidance) < 50:  # No match
        guidance += (
            "We have recorded your symptoms: '" + symptoms + "'.\n\n"
            "**General Self-Care Tips:**\n"
            "- Get adequate rest and drink plenty of fluids.\n"
            "- Keep track of when symptoms started and if they are worsening.\n\n"
            "⚠️ **When to see a doctor:**\n"
            "- If symptoms do not improve after 3-5 days.\n"
            "- If pain or discomfort is severe.\n"
            "- If you have underlying conditions (diabetes, heart disease).\n"
        )

    guidance += (
        "\n\n---\n"
        "⚠️ *Disclaimer: This analysis is for educational and tracking purposes only. "
        "It is not a diagnosis. Always consult a medical professional for advice.*"
    )
    return guidance


@tool
def log_nutrition_log(
    user_id: int,
    meal_type: str,
    calories: float,
    protein_g: float = None,
    carbs_g: float = None,
    fat_g: float = None,
    food_items: str = None,
    recorded_at: str = None
) -> str:
    """
    Log a meal or nutritional intake record for a user.

    Args:
        user_id: The user's ID.
        meal_type: breakfast, lunch, dinner, or snack.
        calories: Caloric value in kcal.
        protein_g: Optional protein content in grams.
        carbs_g: Optional carbohydrates in grams.
        fat_g: Optional fat content in grams.
        food_items: Optional description of foods eaten (e.g. 'Oatmeal with banana').
        recorded_at: Optional datetime string (YYYY-MM-DD HH:MM).

    Returns:
        Confirmation status.
    """
    try:
        meal_type_clean = meal_type.lower().strip()
        if meal_type_clean not in ["breakfast", "lunch", "dinner", "snack"]:
            meal_type_clean = "snack"

        log_id = db.log_nutrition(
            user_id=user_id,
            meal_type=meal_type_clean,
            calories=calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            food_items=food_items,
            recorded_at=recorded_at
        )

        res = f"🍎 **Nutrition Logged!** (Log ID: {log_id})\n\n"
        res += f"🍴 Meal: {meal_type_clean.capitalize()}\n"
        res += f"🔥 Calories: {calories} kcal\n"
        if protein_g or carbs_g or fat_g:
            res += f"💪 Macros: Protein: {protein_g or 0}g | Carbs: {carbs_g or 0}g | Fat: {fat_g or 0}g\n"
        if food_items:
            res += f"📝 Food: {food_items}\n"

        return res
    except Exception as e:
        return f"❌ Error logging nutrition: {str(e)}"


@tool
def run_risk_assessment_tool(user_id: int) -> str:
    """
    Run the predictive risk assessment models for Cardiovascular and Diabetes risks
    and list active warnings/anomalies.

    Args:
        user_id: The user's ID.

    Returns:
        Structured clinical summary report of health risks.
    """
    try:
        cvd = analytics.calculate_cardiovascular_risk(user_id)
        diab = analytics.calculate_diabetes_risk(user_id)
        anoms = analytics.detect_anomalies(user_id, days=14)

        report = "📋 **Predictive Health Risk Assessment**\n\n"
        
        # CVD Risk
        if "error" not in cvd:
            report += "🫀 **10-Year Cardiovascular Disease Risk:**\n"
            report += f"  - Status: **{cvd['risk_category']}** ({cvd['risk_percentage']}%)\n"
            report += f"  - Guidance: {cvd['advice']}\n\n"
        
        # Diabetes Risk
        if "error" not in diab:
            report += "🍬 **Type-2 Diabetes Risk Profile (FINDRISC):**\n"
            report += f"  - Status: **{diab['risk_category']}**\n"
            report += f"  - Guidance: {diab['advice']}\n\n"

        # Anomalies
        report += "⚠️ **Recent Vital Alerts / Anomalies (Last 14 days):**\n"
        if anoms:
            for an in anoms[:5]:
                severity_icon = "🚨" if an["severity"] == "Critical" else "⚠️"
                report += f"  - {severity_icon} **{an['display_name']}** ({an['recorded_at']}): {an['reason']}\n"
        else:
            report += "  - ✅ No anomalies detected in recent vitals.\n"

        report += (
            "\n\n---\n"
            "⚠️ *Disclaimer: Risk scores are based on statistical population indicators and are not "
            "definitive clinical diagnoses. Always consult a physician.*"
        )
        return report
    except Exception as e:
        return f"❌ Error running risk assessment: {str(e)}"


@tool
def generate_automated_report(user_id: int, days: int = 7) -> str:
    """
    Generate an automated comprehensive health report containing medication adherence,
    vitals summary, anomalies, and nutrition summaries.

    Args:
        user_id: The user's ID.
        days: Report duration in days.

    Returns:
        Comprehensive health report formatted in Markdown.
    """
    try:
        user = db.get_user(user_id)
        if not user:
            return "User profile not found."

        adherence = db.get_adherence_rate(user_id, days=days)
        metrics = db.get_health_metrics(user_id, days=days)
        nutr = db.get_nutrition_logs(user_id, days=days)
        anoms = analytics.detect_anomalies(user_id, days=days)

        report = f"# 🏥 HEALTHGUARD AI COMPREHENSIVE REPORT\n"
        report += f"**Patient Name:** {user['name']} | **Date Generated:** {datetime.now().strftime('%Y-%m-%d')}\n"
        report += f"**Report Period:** Last {days} Days\n"
        report += f"==========================================\n\n"

        # 1. Medication Adherence
        report += f"## 💊 Medication Adherence Summary\n"
        report += f"- **Adherence Rate:** **{adherence}%**\n"
        if adherence >= 90:
            report += f"- *Status:* Excellent medication adherence.\n"
        elif adherence >= 70:
            report += f"- *Status:* Good, but can be improved. Try to set routine reminders.\n"
        else:
            report += f"- *Status:* ⚠️ Warning: Low adherence rate. Please consult your physician.\n"
        report += "\n"

        # 2. Vitals & Health Metrics Summary
        report += f"## 📊 Vitals & Health Metrics\n"
        if metrics:
            import pandas as pd
            df = pd.DataFrame(metrics)
            for mtype in df["metric_type"].unique():
                sub = df[df["metric_type"] == mtype]
                avg = sub["value"].mean()
                unit = sub["unit"].iloc[0]
                report += f"- **{mtype.replace('_',' ').title()}:** Average: {avg:.1f} {unit} (Min: {sub['value'].min():.1f} | Max: {sub['value'].max():.1f}) over {len(sub)} readings.\n"
        else:
            report += f"- No health metrics logged during this period.\n"
        report += "\n"

        # 3. Nutrition Log Summary
        report += f"## 🍎 Nutrition & Caloric Log\n"
        if nutr:
            ndf = pd.DataFrame(nutr)
            total_cals = ndf["calories"].sum()
            avg_daily = total_cals / days
            report += f"- **Total Calories Logged:** {total_cals:.0f} kcal\n"
            report += f"- **Average Daily Caloric Intake:** {avg_daily:.0f} kcal/day\n"
            avg_prot = ndf["protein_g"].mean() if "protein_g" in ndf.columns else 0
            avg_carb = ndf["carbs_g"].mean() if "carbs_g" in ndf.columns else 0
            avg_fat = ndf["fat_g"].mean() if "fat_g" in ndf.columns else 0
            report += f"- **Average Macronutrients:** Protein: {avg_prot or 0:.1f}g | Carbs: {avg_carb or 0:.1f}g | Fat: {avg_fat or 0:.1f}g\n"
        else:
            report += f"- No nutrition data logged during this period.\n"
        report += "\n"

        # 4. Critical Warnings & Anomalies
        report += f"## 🚨 Vital Alerts & Anomalies\n"
        if anoms:
            for an in anoms:
                report += f"- **{an['display_name']}** ({an['recorded_at']}): {an['reason']}\n"
        else:
            report += f"- ✅ No critical vital anomalies or health alerts during this period.\n"
        report += "\n"

        # 5. AI Recommendations
        cvd = analytics.calculate_cardiovascular_risk(user_id)
        report += f"## 💡 AI-Generated Wellness Guidance\n"
        if "error" not in cvd:
            report += f"- **CVD Prevention:** {cvd['advice']}\n"
        report += f"- Ensure to stay hydrated, aim for at least 7-8 hours of sleep daily, and maintain a log of physical steps.\n\n"

        report += (
            "Disclaimer: This report is compiled based on patient-logged inputs and is for general health "
            "tracking. It does not replace clinical evaluation or diagnostic blood profiling. In case of emergency, "
            "seek professional medical support immediately."
        )
        return report
    except Exception as e:
        return f"❌ Error generating report: {str(e)}"
