"""
HealthGuard AI — Medications Page
Full medication CRUD, scheduling, and adherence tracking.
"""

import streamlit as st
import json
from datetime import datetime, date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db
from utils.visualizations import chart_medication_adherence


FREQUENCY_OPTIONS = [
    "Once daily",
    "Twice daily",
    "Three times daily",
    "Four times daily",
    "Every morning",
    "Every night",
    "Weekly",
    "As needed",
]

FREQUENCY_TIMES = {
    "Once daily": ["08:00"],
    "Twice daily": ["08:00", "20:00"],
    "Three times daily": ["08:00", "14:00", "20:00"],
    "Four times daily": ["07:00", "12:00", "17:00", "21:00"],
    "Every morning": ["08:00"],
    "Every night": ["21:00"],
    "Weekly": ["08:00"],
    "As needed": ["As needed"],
}


def show_medications():
    user_id = st.session_state.get("user_id", 1)

    st.markdown("""
    <div style="margin-bottom:24px">
        <h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;margin:0">
            💊 Medication Tracker
        </h1>
        <p style="color:#94a3b8;margin:4px 0 0 0">Manage your medications and track adherence</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Today's Schedule", "➕ Add Medication", "📊 Adherence Report"])

    # ── Tab 1: Today's Schedule ─────────────────────────────────────────────
    with tab1:
        medications = db.get_medications(user_id, active_only=True)
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_display = datetime.now().strftime("%A, %B %d, %Y")

        st.markdown(f"<p style='color:#94a3b8;margin-bottom:16px'>📅 {today_display}</p>", unsafe_allow_html=True)

        if not medications:
            st.info("No active medications found. Add your first medication in the '➕ Add Medication' tab.")
        else:
            for med in medications:
                # Skip expired or not-yet-started medications
                if med.get("end_date") and med["end_date"] < today_str:
                    continue
                if med["start_date"] > today_str:
                    continue

                try:
                    times = json.loads(med["time_slots"])
                except (json.JSONDecodeError, TypeError):
                    times = ["08:00"]

                with st.container():
                    st.markdown(f"""
                    <div style="
                        background:linear-gradient(135deg,rgba(30,41,59,0.9),rgba(15,23,42,0.9));
                        border:1px solid rgba(79,142,247,0.15);
                        border-radius:14px;padding:18px 22px;margin-bottom:14px;
                    ">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start">
                            <div>
                                <h3 style="color:#e2e8f0;margin:0 0 4px 0;font-size:1.1rem">{med['name']}</h3>
                                <div style="display:flex;gap:16px;flex-wrap:wrap">
                                    <span style="color:#94a3b8;font-size:0.85rem">💊 {med['dosage']}</span>
                                    <span style="color:#94a3b8;font-size:0.85rem">🔄 {med['frequency']}</span>
                                    <span style="color:#94a3b8;font-size:0.85rem">⏰ {', '.join(times)}</span>
                                </div>
                                {f'<p style="color:#f59e0b;font-size:0.8rem;margin:6px 0 0 0">📝 {med["notes"]}</p>' if med.get("notes") else ""}
                            </div>
                            <span style="background:rgba(34,197,94,0.1);color:#22c55e;padding:4px 10px;border-radius:99px;font-size:0.75rem;border:1px solid rgba(34,197,94,0.2)">Active</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    col_btn, col_miss, col_del = st.columns([2, 2, 1])
                    with col_btn:
                        if st.button(f"✅ Mark as Taken", key=f"taken_{med['id']}"):
                            scheduled_at = f"{today_str} {times[0]}"
                            db.log_medication(
                                medication_id=med["id"],
                                user_id=user_id,
                                scheduled_at=scheduled_at,
                                status="taken"
                            )
                            st.success(f"✅ {med['name']} marked as taken!")
                            st.rerun()
                    with col_miss:
                        if st.button(f"❌ Mark as Missed", key=f"missed_{med['id']}"):
                            scheduled_at = f"{today_str} {times[0]}"
                            db.log_medication(
                                medication_id=med["id"],
                                user_id=user_id,
                                scheduled_at=scheduled_at,
                                status="missed"
                            )
                            st.warning(f"❌ {med['name']} marked as missed.")
                            st.rerun()
                    with col_del:
                        if st.button("🗑️", key=f"del_{med['id']}", help="Deactivate medication"):
                            db.deactivate_medication(med["id"])
                            st.info(f"Deactivated {med['name']}.")
                            st.rerun()

        # Adherence summary
        st.markdown("<hr style='border-color:rgba(148,163,184,0.1);margin:20px 0'>", unsafe_allow_html=True)
        adherence = db.get_adherence_rate(user_id, days=7)
        color = "#22c55e" if adherence >= 80 else "#f59e0b" if adherence >= 60 else "#ef4444"
        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg,rgba(30,41,59,0.9),rgba(15,23,42,0.9));
            border:1px solid rgba(148,163,184,0.1);border-radius:14px;
            padding:20px;text-align:center;
        ">
            <div style="font-size:3rem;font-weight:700;color:{color}">{adherence}%</div>
            <div style="color:#94a3b8">7-Day Medication Adherence Rate</div>
            <div style="color:#94a3b8;font-size:0.8rem;margin-top:4px">
                {"🌟 Excellent! Keep it up!" if adherence >= 90 else
                 "👍 Good progress!" if adherence >= 70 else
                 "⚠️ Try to improve consistency" if adherence >= 50 else
                 "🚨 Low adherence – please consult your doctor"}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Tab 2: Add Medication ───────────────────────────────────────────────
    with tab2:
        st.markdown("<h3 style='color:#e2e8f0;margin-bottom:16px'>Add New Medication</h3>", unsafe_allow_html=True)

        with st.form("add_medication_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                med_name = st.text_input("💊 Medication Name *", placeholder="e.g. Metformin, Paracetamol")
                dosage = st.text_input("⚖️ Dosage *", placeholder="e.g. 500mg, 1 tablet, 5ml")
                frequency = st.selectbox("🔄 Frequency *", FREQUENCY_OPTIONS)
            with col_b:
                start_date = st.date_input("📅 Start Date", value=date.today())
                end_date = st.date_input("📅 End Date (optional)", value=None)
                notes = st.text_area("📝 Special Instructions", placeholder="e.g. Take with food, Avoid alcohol",
                                     height=80)

            submitted = st.form_submit_button("➕ Add Medication Reminder", use_container_width=True)

            if submitted:
                if not med_name or not dosage:
                    st.error("Please fill in medication name and dosage.")
                else:
                    times = FREQUENCY_TIMES.get(frequency, ["08:00"])
                    times_json = json.dumps(times)
                    med_id = db.add_medication(
                        user_id=user_id,
                        name=med_name,
                        dosage=dosage,
                        frequency=frequency,
                        time_slots=times_json,
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
                        notes=notes if notes else None,
                    )
                    st.success(f"✅ **{med_name}** ({dosage}) added successfully!")
                    st.info(f"⏰ Scheduled at: {', '.join(times)}")
                    st.rerun()

        # Show inactive medications
        with st.expander("📜 View All Medications (including inactive)"):
            all_meds = db.get_medications(user_id, active_only=False)
            if all_meds:
                for m in all_meds:
                    status = "🟢 Active" if m["is_active"] else "🔴 Inactive"
                    st.markdown(f"**{m['name']}** — {m['dosage']} | {m['frequency']} | {status}")
            else:
                st.info("No medications recorded yet.")

    # ── Tab 3: Adherence Report ─────────────────────────────────────────────
    with tab3:
        days_filter = st.slider("Report period (days)", min_value=3, max_value=30, value=7)
        logs = db.get_medication_logs(user_id, days=days_filter)

        if logs:
            adh_fig = chart_medication_adherence(logs, days=days_filter)
            st.plotly_chart(adh_fig, use_container_width=True, config={"displayModeBar": False})

            # Log table
            st.markdown("<h3 style='color:#e2e8f0;font-size:1rem;margin:16px 0 8px'>Recent Medication Logs</h3>",
                        unsafe_allow_html=True)
            import pandas as pd
            log_df = pd.DataFrame(logs)[["med_name", "dosage", "scheduled_at", "taken_at", "status", "notes"]]
            log_df.columns = ["Medication", "Dosage", "Scheduled", "Taken At", "Status", "Notes"]
            st.dataframe(log_df, use_container_width=True, hide_index=True)

            # Export
            csv_data = log_df.to_csv(index=False)
            st.download_button(
                label="📥 Export Report (CSV)",
                data=csv_data,
                file_name=f"medication_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.info(f"No medication logs found for the last {days_filter} days. Start tracking your medications!")
