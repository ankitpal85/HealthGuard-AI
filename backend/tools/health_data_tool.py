"""
Health Data Tool
Handles health metrics logging, retrieval, parsing and basic analysis.
"""

import json
import pandas as pd
from datetime import datetime
from langchain.tools import tool
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db


METRIC_CONFIG = {
    "steps": {"unit": "steps", "normal_min": 0, "normal_max": 15000, "goal": 10000},
    "heart_rate": {"unit": "bpm", "normal_min": 60, "normal_max": 100, "goal": 75},
    "blood_pressure_systolic": {"unit": "mmHg", "normal_min": 90, "normal_max": 120, "goal": 115},
    "blood_pressure_diastolic": {"unit": "mmHg", "normal_min": 60, "normal_max": 80, "goal": 75},
    "weight": {"unit": "kg", "normal_min": 0, "normal_max": 300, "goal": None},
    "blood_glucose": {"unit": "mg/dL", "normal_min": 70, "normal_max": 140, "goal": 100},
    "oxygen_saturation": {"unit": "%", "normal_min": 95, "normal_max": 100, "goal": 98},
    "sleep_hours": {"unit": "hours", "normal_min": 6, "normal_max": 9, "goal": 8},
    "calories_burned": {"unit": "kcal", "normal_min": 0, "normal_max": 5000, "goal": 2000},
    "water_intake": {"unit": "liters", "normal_min": 0, "normal_max": 10, "goal": 2.5},
    "bmi": {"unit": "kg/m²", "normal_min": 18.5, "normal_max": 24.9, "goal": 22},
}


def _assess_metric(metric_type: str, value: float) -> str:
    config = METRIC_CONFIG.get(metric_type)
    if not config:
        return "✅ Recorded"
    if value < config["normal_min"]:
        return "⚠️ Below normal range"
    elif value > config["normal_max"]:
        return "⚠️ Above normal range"
    return "✅ Normal range"


@tool
def log_health_metric(
    user_id: int,
    metric_type: str,
    value: float,
    recorded_at: str = None,
    value2: float = None,
    notes: str = None
) -> str:
    """
    Log a health metric reading for a user.

    Args:
        user_id: The user's ID.
        metric_type: Type of metric. Options: steps, heart_rate, blood_pressure_systolic,
                     blood_pressure_diastolic, weight, blood_glucose, oxygen_saturation,
                     sleep_hours, calories_burned, water_intake, bmi.
        value: The metric value.
        recorded_at: Optional datetime string (YYYY-MM-DD HH:MM). Defaults to now.
        value2: Second value for blood pressure (diastolic when systolic is value).
        notes: Optional notes.

    Returns:
        Confirmation with health assessment.
    """
    try:
        config = METRIC_CONFIG.get(metric_type, {"unit": "units"})
        unit = config.get("unit", "units")
        recorded_at = recorded_at or datetime.now().strftime("%Y-%m-%d %H:%M")

        metric_id = db.log_health_metric(
            user_id=user_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            recorded_at=recorded_at,
            value2=value2,
            notes=notes
        )

        assessment = _assess_metric(metric_type, value)
        display_name = metric_type.replace("_", " ").title()

        result = f"✅ **{display_name}** recorded!\n\n"
        result += f"📊 Value: **{value} {unit}**\n"
        if value2 is not None:
            result += f"   Secondary: {value2} {unit}\n"
        result += f"🕒 Recorded at: {recorded_at}\n"
        result += f"🔍 Status: {assessment}\n"
        if notes:
            result += f"📝 Notes: {notes}\n"
        result += f"\nMetric ID: {metric_id}"

        return result
    except Exception as e:
        return f"❌ Error logging health metric: {str(e)}"


@tool
def get_health_summary(user_id: int, days: int = 7) -> str:
    """
    Get a comprehensive health summary for the past N days.

    Args:
        user_id: The user's ID.
        days: Number of days to include (default: 7).

    Returns:
        Health summary with averages and assessments for all tracked metrics.
    """
    try:
        all_metrics = db.get_health_metrics(user_id, days=days)

        if not all_metrics:
            return (
                f"No health data found for the past {days} days.\n"
                "Start logging your health metrics to see your summary."
            )

        df = pd.DataFrame(all_metrics)
        summary = f"📋 **Health Summary (Last {days} Days)**\n\n"

        for metric_type in df["metric_type"].unique():
            sub = df[df["metric_type"] == metric_type]
            avg_val = sub["value"].mean()
            min_val = sub["value"].min()
            max_val = sub["value"].max()
            config = METRIC_CONFIG.get(metric_type, {"unit": "units"})
            unit = config.get("unit", "units")
            display_name = metric_type.replace("_", " ").title()
            assessment = _assess_metric(metric_type, avg_val)

            summary += f"**{display_name}** {assessment}\n"
            summary += f"  Avg: {avg_val:.1f} {unit} | Min: {min_val:.1f} | Max: {max_val:.1f}\n"
            summary += f"  Readings: {len(sub)}\n\n"

        return summary
    except Exception as e:
        return f"❌ Error generating health summary: {str(e)}"


@tool
def parse_health_data_json(json_data: str, user_id: int) -> str:
    """
    Parse and import health data from a JSON string.
    Supports batch import of multiple health metrics at once.

    Args:
        json_data: JSON string with health metrics. Format:
                   [{"metric_type": "steps", "value": 8500, "recorded_at": "2024-01-15 08:00"},...]
        user_id: The user's ID.

    Returns:
        Import summary with count of records processed.
    """
    try:
        data = json.loads(json_data)
        if isinstance(data, dict):
            data = [data]

        imported = 0
        errors = []

        for record in data:
            try:
                metric_type = record.get("metric_type", "")
                value = float(record.get("value", 0))
                recorded_at = record.get("recorded_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
                unit = METRIC_CONFIG.get(metric_type, {}).get("unit", "units")
                notes = record.get("notes")
                value2 = record.get("value2")

                db.log_health_metric(
                    user_id=user_id,
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    recorded_at=recorded_at,
                    value2=value2,
                    notes=notes
                )
                imported += 1
            except Exception as e:
                errors.append(str(e))

        result = f"✅ **Health Data Import Complete**\n\n"
        result += f"📊 Records imported: {imported}/{len(data)}\n"
        if errors:
            result += f"⚠️ Errors: {len(errors)}\n"
            for err in errors[:3]:
                result += f"  - {err}\n"
        return result
    except json.JSONDecodeError:
        return "❌ Invalid JSON format. Please provide valid JSON data."
    except Exception as e:
        return f"❌ Error parsing health data: {str(e)}"


@tool
def calculate_bmi(weight_kg: float, height_cm: float, user_id: int = None) -> str:
    """
    Calculate BMI and log it if user_id is provided.

    Args:
        weight_kg: Weight in kilograms.
        height_cm: Height in centimeters.
        user_id: Optional user ID to save the BMI reading.

    Returns:
        BMI value, category, and health guidance.
    """
    try:
        height_m = height_cm / 100
        bmi = round(weight_kg / (height_m ** 2), 1)

        if bmi < 18.5:
            category = "Underweight"
            advice = "Consider consulting a nutritionist to reach a healthy weight."
        elif bmi < 25:
            category = "Normal weight"
            advice = "Great! Maintain your healthy lifestyle."
        elif bmi < 30:
            category = "Overweight"
            advice = "Consider moderate exercise and balanced diet. Consult your doctor."
        elif bmi < 35:
            category = "Obese (Class I)"
            advice = "Please consult a healthcare provider for a weight management plan."
        else:
            category = "Obese (Class II/III)"
            advice = "Seek immediate medical guidance for weight management."

        result = f"📊 **BMI Calculation**\n\n"
        result += f"Weight: {weight_kg} kg | Height: {height_cm} cm\n"
        result += f"**BMI: {bmi} kg/m²** — {category}\n\n"
        result += f"💡 {advice}\n\n"
        result += "⚠️ BMI is a screening tool, not a diagnostic measure. Consult your doctor for complete health assessment."

        if user_id:
            db.log_health_metric(user_id=user_id, metric_type="bmi",
                                 value=bmi, unit="kg/m²")
            result += f"\n✅ BMI logged to your health records."

        return result
    except Exception as e:
        return f"❌ Error calculating BMI: {str(e)}"
