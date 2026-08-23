"""
Medication Management Tool
Handles medication reminders, scheduling, and adherence tracking via LangChain tools.
"""

import json
from datetime import datetime, timedelta
from langchain.tools import tool
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db


FREQUENCY_MAP = {
    "once daily": ["08:00"],
    "twice daily": ["08:00", "20:00"],
    "three times daily": ["08:00", "14:00", "20:00"],
    "four times daily": ["07:00", "12:00", "17:00", "21:00"],
    "every morning": ["08:00"],
    "every night": ["21:00"],
    "weekly": ["08:00"],  # Monday default
}


@tool
def add_medication_reminder(
    user_id: int,
    medication_name: str,
    dosage: str,
    frequency: str,
    start_date: str = None,
    end_date: str = None,
    notes: str = None
) -> str:
    """
    Add a new medication reminder for a user.

    Args:
        user_id: The user's ID in the database.
        medication_name: Name of the medication (e.g., 'Metformin', 'Aspirin').
        dosage: Dosage information (e.g., '500mg', '1 tablet').
        frequency: How often to take it (e.g., 'twice daily', 'once daily').
        start_date: Start date in YYYY-MM-DD format (defaults to today).
        end_date: Optional end date in YYYY-MM-DD format.
        notes: Optional notes (e.g., 'take with food').

    Returns:
        Confirmation message with scheduled times.
    """
    try:
        start_date = start_date or datetime.now().strftime("%Y-%m-%d")
        freq_lower = frequency.lower().strip()
        time_slots = FREQUENCY_MAP.get(freq_lower, ["08:00"])
        time_slots_json = json.dumps(time_slots)

        med_id = db.add_medication(
            user_id=user_id,
            name=medication_name,
            dosage=dosage,
            frequency=frequency,
            time_slots=time_slots_json,
            start_date=start_date,
            end_date=end_date,
            notes=notes
        )

        times_str = ", ".join(time_slots)
        result = (
            f"✅ Medication reminder added successfully!\n\n"
            f"**{medication_name}** ({dosage})\n"
            f"📅 Frequency: {frequency}\n"
            f"⏰ Scheduled times: {times_str}\n"
            f"📆 Start date: {start_date}\n"
        )
        if end_date:
            result += f"📆 End date: {end_date}\n"
        if notes:
            result += f"📝 Notes: {notes}\n"
        result += f"\nMedication ID: {med_id}"
        return result

    except Exception as e:
        return f"❌ Error adding medication reminder: {str(e)}"


@tool
def get_todays_medications(user_id: int) -> str:
    """
    Get all medications scheduled for today for a user.

    Args:
        user_id: The user's ID in the database.

    Returns:
        List of today's medications with their scheduled times.
    """
    try:
        medications = db.get_medications(user_id, active_only=True)
        if not medications:
            return "No active medications found. Add medications using the medication tracker."

        today = datetime.now().strftime("%Y-%m-%d")
        result = f"💊 **Today's Medications** ({today})\n\n"

        for med in medications:
            # Check if medication is still in range
            if med.get("end_date") and med["end_date"] < today:
                continue
            if med["start_date"] > today:
                continue

            try:
                times = json.loads(med["time_slots"])
            except (json.JSONDecodeError, TypeError):
                times = ["08:00"]

            result += f"• **{med['name']}** - {med['dosage']}\n"
            result += f"  ⏰ Times: {', '.join(times)}\n"
            result += f"  📋 Frequency: {med['frequency']}\n"
            if med.get("notes"):
                result += f"  📝 {med['notes']}\n"
            result += "\n"

        adherence = db.get_adherence_rate(user_id, days=7)
        result += f"---\n📊 **7-Day Adherence Rate**: {adherence}%"
        return result

    except Exception as e:
        return f"❌ Error fetching medications: {str(e)}"


@tool
def mark_medication_taken(
    medication_id: int,
    user_id: int,
    scheduled_time: str = None,
    notes: str = None
) -> str:
    """
    Mark a medication as taken for today.

    Args:
        medication_id: ID of the medication.
        user_id: The user's ID.
        scheduled_time: The scheduled time (HH:MM) for this dose.
        notes: Optional notes about this dose.

    Returns:
        Confirmation message.
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        scheduled_at = f"{today} {scheduled_time}" if scheduled_time else f"{today} 08:00"
        log_id = db.log_medication(
            medication_id=medication_id,
            user_id=user_id,
            scheduled_at=scheduled_at,
            status="taken",
            notes=notes
        )
        adherence = db.get_adherence_rate(user_id, days=7)
        return (
            f"✅ Medication marked as taken! (Log ID: {log_id})\n"
            f"📊 Your 7-day adherence rate is now: **{adherence}%**\n\n"
            f"Keep up the great work! Consistent medication adherence is crucial for your health."
        )
    except Exception as e:
        return f"❌ Error logging medication: {str(e)}"


@tool
def get_medication_adherence_report(user_id: int, days: int = 7) -> str:
    """
    Generate a medication adherence report for the past N days.

    Args:
        user_id: The user's ID.
        days: Number of days to include in report (default: 7).

    Returns:
        Detailed adherence report.
    """
    try:
        logs = db.get_medication_logs(user_id, days=days)
        adherence = db.get_adherence_rate(user_id, days=days)

        if not logs:
            return (
                f"No medication logs found for the past {days} days.\n"
                "Start tracking your medications to see adherence reports."
            )

        taken = sum(1 for l in logs if l["status"] == "taken")
        missed = sum(1 for l in logs if l["status"] == "missed")
        pending = sum(1 for l in logs if l["status"] == "pending")

        report = f"📊 **Medication Adherence Report (Last {days} Days)**\n\n"
        report += f"✅ Taken: {taken}\n"
        report += f"❌ Missed: {missed}\n"
        report += f"⏳ Pending: {pending}\n"
        report += f"📈 Adherence Rate: **{adherence}%**\n\n"

        if adherence >= 90:
            report += "🌟 Excellent adherence! You're doing a fantastic job."
        elif adherence >= 70:
            report += "👍 Good adherence. Try to be more consistent for better health outcomes."
        else:
            report += "⚠️ Low adherence detected. Please consult your doctor about medication management."

        return report
    except Exception as e:
        return f"❌ Error generating report: {str(e)}"
