"""
Health Insights
---------------
Generates a simple, non-diagnostic health summary for the dashboard.

This module uses existing database data such as:
- Vitals
- Medication adherence
- Nutrition logs
- Active medications

Important:
This is a wellness/tracking summary, NOT a medical diagnosis
or clinical risk assessment.
"""

from typing import Any, Dict, List, Optional

from database import db_manager as db


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def _safe_number(value: Any) -> Optional[float]:
    """Convert a value to float safely."""
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_text(value: Any, default: str = "") -> str:
    """Convert a value to clean text."""
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _metric_value(metric: Any) -> Any:
    """Get primary metric value from dict/object."""
    if isinstance(metric, dict):
        return metric.get("value")

    return getattr(metric, "value", None)


def _metric_value2(metric: Any) -> Any:
    """Get secondary metric value from dict/object."""
    if isinstance(metric, dict):
        return metric.get("value2")

    return getattr(metric, "value2", None)


def _metric_unit(metric: Any) -> str:
    """Get metric unit."""
    if isinstance(metric, dict):
        return _clean_text(metric.get("unit"))

    return _clean_text(getattr(metric, "unit", None))


# -------------------------------------------------------------------
# Latest vitals
# -------------------------------------------------------------------

def _get_latest_vitals(user_id: int) -> Dict[str, Any]:
    """
    Fetch latest available health metrics for the user.
    """

    metric_types = [
        "heart_rate",
        "blood_pressure",
        "steps",
        "sleep",
        "sleep_duration",
        "temperature",
        "body_temperature",
        "weight",
    ]

    latest: Dict[str, Any] = {}

    for metric_type in metric_types:
        try:
            metric = db.get_latest_metric(user_id, metric_type)

            if not metric:
                continue

            value = _metric_value(metric)

            if value is None:
                continue

            value2 = _metric_value2(metric)
            unit = _metric_unit(metric)

            if metric_type == "blood_pressure":
                systolic = _safe_number(value)
                diastolic = _safe_number(value2)

                if systolic is not None and diastolic is not None:
                    latest[metric_type] = {
                        "value": f"{int(systolic)}/{int(diastolic)}",
                        "systolic": systolic,
                        "diastolic": diastolic,
                        "unit": "mmHg",
                    }
                else:
                    latest[metric_type] = {
                        "value": value,
                        "unit": unit or "mmHg",
                    }

            else:
                number = _safe_number(value)

                latest[metric_type] = {
                    "value": (
                        int(number)
                        if number is not None and number.is_integer()
                        else number if number is not None else value
                    ),
                    "unit": unit,
                }

        except Exception:
            # One failed metric should not break the whole dashboard.
            continue

    return latest


# -------------------------------------------------------------------
# Format vitals for frontend
# -------------------------------------------------------------------

def _format_latest_vitals(latest: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert latest vitals dictionary into frontend-friendly list."""

    display_names = {
        "heart_rate": "Heart Rate",
        "blood_pressure": "Blood Pressure",
        "steps": "Steps",
        "sleep": "Sleep",
        "sleep_duration": "Sleep Duration",
        "temperature": "Temperature",
        "body_temperature": "Body Temperature",
        "weight": "Weight",
    }

    icons = {
        "heart_rate": "heart",
        "blood_pressure": "activity",
        "steps": "footprints",
        "sleep": "moon",
        "sleep_duration": "moon",
        "temperature": "activity",
        "body_temperature": "activity",
        "weight": "activity",
    }

    result: List[Dict[str, Any]] = []

    for key, data in latest.items():
        if not isinstance(data, dict):
            data = {
                "value": data,
                "unit": "",
            }

        result.append(
            {
                "type": key,
                "name": display_names.get(key, key.replace("_", " ").title()),
                "value": data.get("value"),
                "unit": data.get("unit", ""),
                "icon": icons.get(key, "activity"),
            }
        )

    return result


# -------------------------------------------------------------------
# Insights
# -------------------------------------------------------------------

def _generate_insights(
    adherence: Optional[float],
    vitals_count: int,
    nutrition_count: int,
    active_medications: int,
    latest: Dict[str, Any],
) -> List[Dict[str, str]]:
    """
    Generate simple rule-based wellness insights.

    These are informational summaries and should not be treated
    as medical diagnoses.
    """

    insights: List[Dict[str, str]] = []

    # Medication adherence
    if adherence is not None:
        if adherence >= 90:
            insights.append(
                {
                    "type": "positive",
                    "title": "Excellent medication adherence",
                    "message": (
                        f"Your 7-day medication adherence is "
                        f"{round(adherence)}%."
                    ),
                }
            )
        elif adherence >= 75:
            insights.append(
                {
                    "type": "info",
                    "title": "Medication adherence is good",
                    "message": (
                        f"Your 7-day medication adherence is "
                        f"{round(adherence)}%. Try to stay consistent."
                    ),
                }
            )
        else:
            insights.append(
                {
                    "type": "warning",
                    "title": "Medication adherence needs attention",
                    "message": (
                        f"Your 7-day adherence is "
                        f"{round(adherence)}%. Consider using reminders "
                        f"to avoid missed doses."
                    ),
                }
            )

    # Vital tracking
    if vitals_count >= 5:
        insights.append(
            {
                "type": "positive",
                "title": "Good health tracking",
                "message": (
                    f"You recorded {vitals_count} vital measurements "
                    "during the last 7 days."
                ),
            }
        )
    elif vitals_count > 0:
        insights.append(
            {
                "type": "info",
                "title": "Keep tracking your vitals",
                "message": (
                    "Regularly recording your health metrics can make "
                    "your personal health history more useful."
                ),
            }
        )
    else:
        insights.append(
            {
                "type": "info",
                "title": "Start tracking your vitals",
                "message": (
                    "No recent vital measurements were found. "
                    "Add your health metrics to build your dashboard history."
                ),
            }
        )

    # Nutrition
    if nutrition_count >= 5:
        insights.append(
            {
                "type": "positive",
                "title": "Nutrition tracking is active",
                "message": (
                    f"You recorded {nutrition_count} nutrition entries "
                    "in the last 7 days."
                ),
            }
        )
    elif nutrition_count > 0:
        insights.append(
            {
                "type": "info",
                "title": "Continue nutrition tracking",
                "message": (
                    "You have started tracking nutrition. "
                    "More consistent entries can provide better insights."
                ),
            }
        )
    else:
        insights.append(
            {
                "type": "info",
                "title": "Nutrition tracking is empty",
                "message": (
                    "Add meals and nutrition information to improve "
                    "your personal health summary."
                ),
            }
        )

    # Active medications
    if active_medications > 0:
        insights.append(
            {
                "type": "info",
                "title": "Medication plan is active",
                "message": (
                    f"You currently have {active_medications} active "
                    "medication(s) in your profile."
                ),
            }
        )

    # Heart rate informational check
    heart_rate_data = latest.get("heart_rate")

    if isinstance(heart_rate_data, dict):
        heart_rate = _safe_number(heart_rate_data.get("value"))

        if heart_rate is not None:
            if heart_rate < 50:
                insights.append(
                    {
                        "type": "warning",
                        "title": "Heart-rate reading is low",
                        "message": (
                            "A recent heart-rate reading is below 50 BPM. "
                            "Individual readings can vary; if this is unusual "
                            "for you or you feel unwell, consider seeking "
                            "professional medical advice."
                        ),
                    }
                )
            elif heart_rate > 100:
                insights.append(
                    {
                        "type": "warning",
                        "title": "Heart-rate reading is elevated",
                        "message": (
                            "A recent heart-rate reading is above 100 BPM. "
                            "Context matters, including activity and stress. "
                            "If it remains elevated or you feel unwell, "
                            "consider professional medical advice."
                        ),
                    }
                )

    # Blood pressure informational check
    bp_data = latest.get("blood_pressure")

    if isinstance(bp_data, dict):
        systolic = _safe_number(bp_data.get("systolic"))
        diastolic = _safe_number(bp_data.get("diastolic"))

        if systolic is not None and diastolic is not None:
            if systolic >= 140 or diastolic >= 90:
                insights.append(
                    {
                        "type": "warning",
                        "title": "Blood pressure reading is elevated",
                        "message": (
                            f"Recent reading: {int(systolic)}/{int(diastolic)} "
                            "mmHg. A single reading does not establish a "
                            "diagnosis; consider rechecking and discussing "
                            "persistent elevated readings with a healthcare "
                            "professional."
                        ),
                    }
                )

    return insights


# -------------------------------------------------------------------
# Recommendations
# -------------------------------------------------------------------

def _generate_recommendations(
    adherence: Optional[float],
    vitals_count: int,
    nutrition_count: int,
    active_medications: int,
) -> List[str]:
    """Generate simple tracking-focused recommendations."""

    recommendations: List[str] = []

    if adherence is not None and adherence < 90:
        recommendations.append(
            "Use medication reminders and try to maintain a consistent schedule."
        )

    if vitals_count < 5:
        recommendations.append(
            "Keep recording relevant health metrics regularly."
        )

    if nutrition_count < 5:
        recommendations.append(
            "Log meals consistently to build a better nutrition history."
        )

    if active_medications == 0:
        recommendations.append(
            "If you take regular medications, make sure your medication "
            "list is up to date."
        )

    if not recommendations:
        recommendations.append(
            "Keep your health records updated and continue your current "
            "tracking routine."
        )

    return recommendations[:5]


# -------------------------------------------------------------------
# Wellness score
# -------------------------------------------------------------------

def _calculate_wellness_score(
    adherence: Optional[float],
    vitals_count: int,
    nutrition_count: int,
    active_medications: int,
) -> int:
    """
    Calculate a simple dashboard wellness/tracking score.

    IMPORTANT:
    This is NOT a clinical health or disease-risk score.
    """

    score = 0.0

    # Medication adherence: 40 points
    if adherence is not None:
        score += min(max(adherence, 0), 100) * 0.40

    # Vital tracking: 25 points
    vital_score = min(vitals_count / 7, 1.0)
    score += vital_score * 25

    # Nutrition tracking: 20 points
    nutrition_score = min(nutrition_count / 7, 1.0)
    score += nutrition_score * 20

    # Medication/profile activity: 15 points
    if active_medications > 0:
        score += 15

    return max(0, min(100, round(score)))


def _score_level(score: int) -> str:
    """Convert numeric wellness score to a simple level."""

    if score >= 85:
        return "Excellent"

    if score >= 70:
        return "Good"

    if score >= 50:
        return "Fair"

    return "Needs Attention"


# -------------------------------------------------------------------
# Main health insights function
# -------------------------------------------------------------------

def generate_health_insights(user_id: int) -> Dict[str, Any]:
    """
    Generate the complete health insights response.
    """

    user = db.get_user(user_id)

    if not user:
        return {
            "success": False,
            "user_id": user_id,
            "message": "User not found.",
        }

    # ---------------------------------------------------------------
    # User name
    # ---------------------------------------------------------------

    if isinstance(user, dict):
        user_name = (
            user.get("name")
            or user.get("full_name")
            or user.get("username")
            or "User"
        )
    else:
        user_name = (
            getattr(user, "name", None)
            or getattr(user, "full_name", None)
            or getattr(user, "username", None)
            or "User"
        )

    # ---------------------------------------------------------------
    # Vitals
    # ---------------------------------------------------------------

    try:
        vitals = db.get_health_metrics(
            user_id,
            days=7,
        )
    except Exception:
        vitals = []

    if vitals is None:
        vitals = []

    # ---------------------------------------------------------------
    # Medications
    # ---------------------------------------------------------------

    try:
        medications = db.get_medications(
            user_id,
            active_only=True,
        )
    except Exception:
        medications = []

    if medications is None:
        medications = []

    active_medications = len(medications)

    # ---------------------------------------------------------------
    # Medication logs
    # ---------------------------------------------------------------

    try:
        medication_logs = db.get_medication_logs(
            user_id,
            days=7,
        )
    except Exception:
        medication_logs = []

    if medication_logs is None:
        medication_logs = []

    # ---------------------------------------------------------------
    # Adherence
    # ---------------------------------------------------------------

    try:
        adherence_raw = db.get_adherence_rate(
            user_id,
            days=7,
        )
    except Exception:
        adherence_raw = None

    adherence = _safe_number(adherence_raw)

    if adherence is not None:
        adherence = max(0, min(100, adherence))

    # ---------------------------------------------------------------
    # Nutrition
    # ---------------------------------------------------------------

    try:
        nutrition_logs = db.get_nutrition_logs(
            user_id,
            days=7,
        )
    except Exception:
        nutrition_logs = []

    if nutrition_logs is None:
        nutrition_logs = []

    # ---------------------------------------------------------------
    # Latest vitals
    # ---------------------------------------------------------------

    latest = _get_latest_vitals(user_id)

    formatted_latest = _format_latest_vitals(latest)

    # ---------------------------------------------------------------
    # Score
    # ---------------------------------------------------------------

    wellness_score = _calculate_wellness_score(
        adherence=adherence,
        vitals_count=len(vitals),
        nutrition_count=len(nutrition_logs),
        active_medications=active_medications,
    )

    level = _score_level(wellness_score)

    # ---------------------------------------------------------------
    # Insights
    # ---------------------------------------------------------------

    insights = _generate_insights(
        adherence=adherence,
        vitals_count=len(vitals),
        nutrition_count=len(nutrition_logs),
        active_medications=active_medications,
        latest=latest,
    )

    # ---------------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------------

    recommendations = _generate_recommendations(
        adherence=adherence,
        vitals_count=len(vitals),
        nutrition_count=len(nutrition_logs),
        active_medications=active_medications,
    )

    # ---------------------------------------------------------------
    # Final response
    # ---------------------------------------------------------------

    return {
        "success": True,
        "user_id": user_id,
        "user_name": _clean_text(user_name, "User"),

        "wellness_score": wellness_score,
        "level": level,

        "data_points": {
            "vitals_7day": len(vitals),
            "active_medications": active_medications,
            "nutrition_logs_7day": len(nutrition_logs),
            "adherence_7day": (
                round(adherence, 1)
                if adherence is not None
                else None
            ),
        },

        "latest": formatted_latest,

        "insights": insights,

        "recommendations": recommendations,

        "medication_logs_7day": len(medication_logs),

        "disclaimer": (
            "This dashboard provides informational wellness and "
            "tracking insights only. It is not a medical diagnosis "
            "or a replacement for professional medical advice or "
            "emergency care."
        ),
    }


# -------------------------------------------------------------------
# Safe public wrapper
# -------------------------------------------------------------------

def get_health_insights(user_id: int) -> Dict[str, Any]:
    """
    Safe wrapper used by FastAPI.

    Prevents unexpected database errors from crashing the endpoint.
    """

    try:
        return generate_health_insights(user_id)

    except Exception as exc:
        return {
            "success": False,
            "user_id": user_id,
            "message": "Health insights are temporarily unavailable.",
            "error": str(exc),
            "wellness_score": 0,
            "level": "Unavailable",
            "data_points": {
                "vitals_7day": 0,
                "active_medications": 0,
                "nutrition_logs_7day": 0,
                "adherence_7day": None,
            },
            "latest": [],
            "insights": [],
            "recommendations": [],
            "medication_logs_7day": 0,
            "disclaimer": (
                "This dashboard provides informational wellness and "
                "tracking insights only. It is not a medical diagnosis "
                "or a replacement for professional medical advice "
                "or emergency care."
            ),
        }


# -------------------------------------------------------------------
# Compatibility alias
# -------------------------------------------------------------------

def build_health_insights(user_id: int) -> Dict[str, Any]:
    """
    Backward-compatible function name.

    This allows main.py to use either:

        get_health_insights(user_id)

    or:

        build_health_insights(user_id)
    """

    return get_health_insights(user_id)