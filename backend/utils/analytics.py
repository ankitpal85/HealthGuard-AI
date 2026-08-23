"""
Healthcare Analytics and Predictive Risk Models
Provides custom statistical models for cardiovascular risk, diabetes risk,
anomaly detection, and linear regression forecasting in pure Python.
"""

import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db


def calculate_cardiovascular_risk(user_id: int) -> Dict[str, Any]:
    """
    Calculate 10-year Cardiovascular Disease (CVD) risk based on a simplified
    Framingham risk score model using logged vitals and profile data.
    """
    user = db.get_user(user_id)
    if not user:
        return {"error": "User not found"}

    age = user.get("age") or 40
    gender = (user.get("gender") or "Male").lower()
    
    # Fetch latest vitals
    latest_bp = db.get_latest_metric(user_id, "blood_pressure_systolic")
    latest_bmi = db.get_latest_metric(user_id, "bmi")
    
    systolic_bp = latest_bp["value"] if latest_bp else 120.0
    bmi = latest_bmi["value"] if latest_bmi else 22.0
    
    # Check if user notes mention smoking
    is_smoker = False
    all_metrics = db.get_health_metrics(user_id, days=30)
    for m in all_metrics:
        if m.get("notes") and any(w in m["notes"].lower() for w in ["smoke", "smoking", "cigarette"]):
            is_smoker = True
            break

    # Simplified Framingham model scoring
    points = 0
    
    # 1. Age points
    if age < 35:
        points += 0
    elif age < 40:
        points += 1
    elif age < 45:
        points += 2
    elif age < 50:
        points += 4
    elif age < 55:
        points += 6
    elif age < 60:
        points += 8
    elif age < 65:
        points += 10
    else:
        points += 12

    # 2. Systolic Blood Pressure points
    if systolic_bp < 120:
        points += 0
    elif systolic_bp < 130:
        points += 1
    elif systolic_bp < 140:
        points += 2
    elif systolic_bp < 160:
        points += 4
    else:
        points += 6

    # 3. Smoking status points
    if is_smoker:
        points += 4

    # 4. Obesity / BMI points
    if bmi >= 30:
        points += 3
    elif bmi >= 25:
        points += 1

    # 5. Gender correction
    if gender == "female":
        points -= 1  # Females generally have lower risk at identical age/BP profiles before menopause

    # Translate points to 10-year risk percentage
    risk_pct = min(95.0, max(1.0, 1.0 + (points * 1.8)))

    if risk_pct < 10.0:
        category = "Low Risk"
        color = "#22c55e"
        advice = "Great! Continue maintaining a healthy diet and active lifestyle."
    elif risk_pct < 20.0:
        category = "Moderate Risk"
        color = "#f59e0b"
        advice = "Monitor your blood pressure and BMI. Include regular cardiovascular exercise (walking, running)."
    else:
        category = "High Risk"
        color = "#ef4444"
        advice = "Strongly advise consulting a physician. Focus on lowering blood pressure, sodium intake, and weight control."

    return {
        "user_id": user_id,
        "age": age,
        "gender": gender.capitalize(),
        "systolic_bp": systolic_bp,
        "bmi": bmi,
        "is_smoker": is_smoker,
        "risk_percentage": round(risk_pct, 1),
        "risk_category": category,
        "color": color,
        "advice": advice
    }


def calculate_diabetes_risk(user_id: int) -> Dict[str, Any]:
    """
    Calculate Type-2 Diabetes risk using a simplified FINDRISC score.
    """
    user = db.get_user(user_id)
    if not user:
        return {"error": "User not found"}

    age = user.get("age") or 40
    
    # Fetch latest metrics
    latest_bmi = db.get_latest_metric(user_id, "bmi")
    latest_glucose = db.get_latest_metric(user_id, "blood_glucose")
    latest_bp = db.get_latest_metric(user_id, "blood_pressure_systolic")
    latest_steps = db.get_latest_metric(user_id, "steps")

    bmi = latest_bmi["value"] if latest_bmi else 22.0
    glucose = latest_glucose["value"] if latest_glucose else 95.0
    systolic_bp = latest_bp["value"] if latest_bp else 120.0
    avg_steps = 8000.0
    
    # Calculate step average if history exists
    step_history = db.get_health_metrics(user_id, "steps", days=7)
    if step_history:
        avg_steps = sum(s["value"] for s in step_history) / len(step_history)

    points = 0

    # 1. Age points
    if age < 45:
        points += 0
    elif age < 55:
        points += 2
    elif age < 65:
        points += 3
    else:
        points += 4

    # 2. BMI points
    if bmi < 25:
        points += 0
    elif bmi < 30:
        points += 1
    else:
        points += 3

    # 3. High Blood Pressure points
    if systolic_bp >= 130:
        points += 2

    # 4. High Glucose points
    if glucose >= 100:  # Pre-diabetic / Diabetic fasting levels
        points += 5

    # 5. Activity points
    if avg_steps < 7000:
        points += 2

    # Map FINDRISC score to 10-year risk probability
    if points < 7:
        risk_pct = 1.0
        category = "Low Risk (1%)"
        color = "#22c55e"
        advice = "Low likelihood of developing diabetes. Keep up the good work!"
    elif points < 12:
        risk_pct = 4.0
        category = "Slightly Elevated (4%)"
        color = "#22c55e"
        advice = "Maintain physical activity and monitor weight."
    elif points < 15:
        risk_pct = 17.0
        category = "Moderate Risk (17%)"
        color = "#f59e0b"
        advice = "Consider reducing carbohydrate intake and aim for at least 150 minutes of weekly exercise."
    elif points < 20:
        risk_pct = 33.0
        category = "High Risk (33%)"
        color = "#ef4444"
        advice = "We recommend visiting a doctor to get an HbA1c test."
    else:
        risk_pct = 50.0
        category = "Very High Risk (50%)"
        color = "#ef4444"
        advice = "Immediate medical checkup recommended for complete blood profiling and lifestyle modification plan."

    return {
        "user_id": user_id,
        "score": points,
        "bmi": bmi,
        "glucose": glucose,
        "systolic_bp": systolic_bp,
        "avg_steps": int(avg_steps),
        "risk_percentage": risk_pct,
        "risk_category": category,
        "color": color,
        "advice": advice
    }


def detect_anomalies(user_id: int, days: int = 14) -> List[Dict[str, Any]]:
    """
    Scan recent health metrics for statistical and clinical anomalies.
    Returns a list of flagged anomalous readings.
    """
    metrics = db.get_health_metrics(user_id, days=days)
    if not metrics:
        return []

    df = pd.DataFrame(metrics)
    anomalies = []

    # Thresholds for absolute clinical alerts
    CRITICAL_THRESHOLDS = {
        "heart_rate": {"low": 50.0, "high": 120.0, "name": "Heart Rate"},
        "blood_pressure_systolic": {"low": 85.0, "high": 150.0, "name": "Systolic Blood Pressure"},
        "blood_pressure_diastolic": {"low": 50.0, "high": 95.0, "name": "Diastolic Blood Pressure"},
        "oxygen_saturation": {"low": 93.0, "high": 101.0, "name": "Oxygen Saturation"},
        "blood_glucose": {"low": 60.0, "high": 180.0, "name": "Blood Glucose"},
        "sleep_hours": {"low": 4.0, "high": 12.0, "name": "Sleep"},
    }

    # Group by metric type to calculate statistical Z-score
    for mtype in df["metric_type"].unique():
        sub_df = df[df["metric_type"] == mtype].copy()
        
        # 1. Clinical Threshold Check
        thresholds = CRITICAL_THRESHOLDS.get(mtype)
        for _, row in sub_df.iterrows():
            val = row["value"]
            is_anomaly = False
            reason = ""
            severity = "Warning"

            # Check absolute levels
            if thresholds:
                if val < thresholds["low"]:
                    is_anomaly = True
                    reason = f"Clinical Alert: {thresholds['name']} is abnormally low ({val} {row['unit']})"
                    severity = "Critical" if mtype in ["oxygen_saturation", "blood_pressure_systolic"] else "Warning"
                elif val > thresholds["high"]:
                    is_anomaly = True
                    reason = f"Clinical Alert: {thresholds['name']} is abnormally high ({val} {row['unit']})"
                    severity = "Critical" if mtype in ["blood_glucose", "blood_pressure_systolic", "heart_rate"] else "Warning"

            # 2. Statistical Z-Score Check (if at least 5 readings exist)
            if len(sub_df) >= 5 and not is_anomaly:
                mean = sub_df["value"].mean()
                std = sub_df["value"].std()
                if std > 0:
                    z_score = (val - mean) / std
                    if abs(z_score) > 2.0:
                        is_anomaly = True
                        direction = "sudden spike" if z_score > 0 else "sudden drop"
                        reason = f"Statistical Anomaly: A {direction} of {val} {row['unit']} compared to your 14-day average of {mean:.1f}"
                        severity = "Warning"

            if is_anomaly:
                anomalies.append({
                    "id": row["id"],
                    "metric_type": mtype,
                    "display_name": mtype.replace("_", " ").title(),
                    "value": val,
                    "unit": row["unit"],
                    "recorded_at": row["recorded_at"],
                    "reason": reason,
                    "severity": severity
                })

    return sorted(anomalies, key=lambda x: x["recorded_at"], reverse=True)


def forecast_metric_trends(user_id: int, metric_type: str, days_history: int = 21) -> Dict[str, Any]:
    """
    Perform a simple linear regression trend prediction for the next 7 days
    based on the last N days of data.
    """
    metrics = db.get_health_metrics(user_id, metric_type=metric_type, days=days_history)
    if not metrics or len(metrics) < 4:
        return {"error": "Insufficient history (minimum 4 readings required)"}

    # Prepare historical data
    df = pd.DataFrame(metrics)
    df["date"] = pd.to_datetime(df["recorded_at"])
    df = df.sort_values("date")

    # Group by date to get daily average if multiple logs exist per day
    df["day_diff"] = (df["date"] - df["date"].min()).dt.days
    
    X = df["day_diff"].values
    y = df["value"].values
    n = len(X)

    # Calculate Linear Regression: y = mx + c
    sum_x = np.sum(X)
    sum_y = np.sum(y)
    sum_xx = np.sum(X ** 2)
    sum_xy = np.sum(X * y)

    denominator = n * sum_xx - (sum_x ** 2)
    if denominator == 0:
        return {"error": "Insufficient date variation in history"}

    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / denominator

    # Generate 7-day forecast
    last_day = df["day_diff"].max()
    last_date = df["date"].max()
    
    forecast = []
    for step in range(1, 8):
        future_day = last_day + step
        future_date = last_date + timedelta(days=step)
        pred_val = slope * future_day + intercept
        # Keep steps and sleep values non-negative
        if metric_type in ["steps", "sleep_hours", "water_intake"]:
            pred_val = max(0.0, pred_val)
        
        forecast.append({
            "date": future_date.strftime("%Y-%m-%d"),
            "value": round(pred_val, 1)
        })

    # Describe the trend
    unit = df["unit"].iloc[0]
    change_direction = "increasing" if slope > 0.01 else "decreasing" if slope < -0.01 else "stable"
    rate_desc = f"{abs(slope):.1f} {unit} per day" if metric_type != "water_intake" else f"{abs(slope):.2f} {unit} per day"
    
    insight = f"Your {metric_type.replace('_',' ')} is currently **{change_direction}** at a rate of **{rate_desc}**."
    if metric_type == "steps" and slope < 0:
        insight += " ⚠️ Trend shows activity decline. Try scheduling regular walks."
    elif metric_type == "weight" and slope > 0:
        insight += " ⚠️ Trend shows weight gain. Consider monitoring calorie logs."

    return {
        "metric_type": metric_type,
        "slope": slope,
        "intercept": intercept,
        "forecast": forecast,
        "insight": insight,
        "historical_avg": round(df["value"].mean(), 1),
        "unit": unit
    }
