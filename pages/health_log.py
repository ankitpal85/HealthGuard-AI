"""
HealthGuard AI — Health Log Page
Log health metrics, view history, calculate BMI, and set goals.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db
from utils.visualizations import chart_health_metric
from utils.data_parser import generate_sample_json, parse_auto, export_metrics_to_csv


METRIC_INFO = {
    "Steps": {"key": "steps", "unit": "steps", "icon": "🚶", "min": 0.0, "max": 50000.0, "step": 100.0, "default": 8000.0},
    "Heart Rate": {"key": "heart_rate", "unit": "bpm", "icon": "❤️", "min": 30.0, "max": 220.0, "step": 1.0, "default": 72.0},
    "Blood Pressure (Systolic)": {"key": "blood_pressure_systolic", "unit": "mmHg", "icon": "🩺", "min": 60.0, "max": 250.0, "step": 1.0, "default": 120.0},
    "Blood Pressure (Diastolic)": {"key": "blood_pressure_diastolic", "unit": "mmHg", "icon": "🩺", "min": 40.0, "max": 160.0, "step": 1.0, "default": 80.0},
    "Blood Glucose": {"key": "blood_glucose", "unit": "mg/dL", "icon": "🍬", "min": 50.0, "max": 600.0, "step": 1.0, "default": 100.0},
    "Weight": {"key": "weight", "unit": "kg", "icon": "⚖️", "min": 1.0, "max": 300.0, "step": 0.1, "default": 70.0},
    "Oxygen Saturation": {"key": "oxygen_saturation", "unit": "%", "icon": "🫁", "min": 50.0, "max": 100.0, "step": 0.1, "default": 98.0},
    "Sleep Hours": {"key": "sleep_hours", "unit": "hours", "icon": "🌙", "min": 0.0, "max": 24.0, "step": 0.5, "default": 7.5},
    "Calories Burned": {"key": "calories_burned", "unit": "kcal", "icon": "🔥", "min": 0.0, "max": 10000.0, "step": 10.0, "default": 2000.0},
    "Water Intake": {"key": "water_intake", "unit": "liters", "icon": "💧", "min": 0.0, "max": 10.0, "step": 0.1, "default": 2.0},
}

NORMAL_RANGES = {
    "steps": "7,000 – 10,000 steps/day recommended",
    "heart_rate": "60 – 100 bpm (resting)",
    "blood_pressure_systolic": "< 120 mmHg (normal), 120-129 (elevated), ≥130 (high)",
    "blood_pressure_diastolic": "< 80 mmHg (normal), ≥80 (high)",
    "blood_glucose": "70 – 100 mg/dL (fasting), < 140 (post-meal)",
    "weight": "Varies by height – use BMI as a guide",
    "oxygen_saturation": "95 – 100% (normal), < 90% (seek medical help)",
    "sleep_hours": "7 – 9 hours/night for adults",
    "calories_burned": "~2000 kcal/day varies by age, sex, activity",
    "water_intake": "2 – 3 liters/day recommended",
}


def show_health_log():
    user_id = st.session_state.get("user_id", 1)

    st.markdown("""
    <div style="margin-bottom:24px">
        <h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;margin:0">
            📝 Health Log
        </h1>
        <p style="color:#94a3b8;margin:4px 0 0 0">Record and track your daily health metrics</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Log Metrics", "📈 View History", "⚖️ BMI Calculator", "📤 Import / Export"])

    # ── Tab 1: Log Metrics ──────────────────────────────────────────────────
    with tab1:
        st.markdown("<h3 style='color:#e2e8f0;font-size:1.1rem;margin-bottom:16px'>Record a Health Metric</h3>",
                    unsafe_allow_html=True)

        with st.form("log_metric_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                metric_label = st.selectbox("📊 Metric Type", list(METRIC_INFO.keys()))
                info = METRIC_INFO[metric_label]
                metric_value = st.number_input(
                    f"{info['icon']} Value ({info['unit']})",
                    min_value=info["min"], max_value=info["max"],
                    step=info["step"], value=info["default"]
                )
            with col_b:
                recorded_date = st.date_input("📅 Date", value=date.today())
                recorded_time = st.time_input("⏰ Time", value=datetime.now().time())
                notes = st.text_input("📝 Notes (optional)", placeholder="e.g. After morning walk")

            submitted = st.form_submit_button("✅ Log Metric", use_container_width=True)

            if submitted:
                key = info["key"]
                recorded_at = f"{recorded_date} {recorded_time.strftime('%H:%M')}"
                unit = info["unit"]
                db.log_health_metric(
                    user_id=user_id,
                    metric_type=key,
                    value=metric_value,
                    unit=unit,
                    recorded_at=recorded_at,
                    notes=notes if notes else None,
                )
                st.success(f"✅ {metric_label}: **{metric_value} {unit}** logged at {recorded_at}!")

                # Show normal range info
                if key in NORMAL_RANGES:
                    st.info(f"ℹ️ Normal range: {NORMAL_RANGES[key]}")

        # Quick-log buttons for common metrics
        st.markdown("<h3 style='color:#e2e8f0;font-size:1rem;margin:20px 0 12px 0'>⚡ Quick Log</h3>",
                    unsafe_allow_html=True)
        ql_cols = st.columns(4)
        quick_metrics = [
            ("🚶 8,000 Steps", "steps", 8000),
            ("💧 2L Water", "water_intake", 2.0),
            ("🌙 8hrs Sleep", "sleep_hours", 8.0),
            ("❤️ 72 bpm HR", "heart_rate", 72),
        ]
        for i, (label, mtype, val) in enumerate(quick_metrics):
            with ql_cols[i]:
                if st.button(label, key=f"quick_{mtype}", use_container_width=True):
                    unit = METRIC_INFO.get(next(k for k, v in METRIC_INFO.items() if v["key"] == mtype), {}).get("unit", "units")
                    db.log_health_metric(user_id=user_id, metric_type=mtype, value=val,
                                         unit=unit, recorded_at=datetime.now().strftime("%Y-%m-%d %H:%M"))
                    st.success(f"Logged: {label}")
                    st.rerun()

    # ── Tab 2: View History ─────────────────────────────────────────────────
    with tab2:
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            view_metric_label = st.selectbox("📊 Select Metric", list(METRIC_INFO.keys()), key="view_metric")
        with col_filter2:
            days_view = st.slider("Time range (days)", 7, 90, 30, key="view_days")

        view_key = METRIC_INFO[view_metric_label]["key"]
        metrics_data = db.get_health_metrics(user_id, metric_type=view_key, days=days_view)

        if metrics_data:
            fig = chart_health_metric(metrics_data, view_key, title=f"{view_metric_label} — Last {days_view} Days")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            df = pd.DataFrame(metrics_data)[["recorded_at", "value", "unit", "notes"]]
            df.columns = ["Recorded At", "Value", "Unit", "Notes"]
            df["Value"] = df["Value"].round(2)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Stats
            vals = [m["value"] for m in metrics_data]
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            unit = METRIC_INFO[view_metric_label]["unit"]
            col_s1.metric("Average", f"{sum(vals)/len(vals):.1f} {unit}")
            col_s2.metric("Minimum", f"{min(vals):.1f} {unit}")
            col_s3.metric("Maximum", f"{max(vals):.1f} {unit}")
            col_s4.metric("Readings", len(vals))

            if key in NORMAL_RANGES:
                st.info(f"ℹ️ {NORMAL_RANGES.get(view_key, '')}")

            # Export
            csv = df.to_csv(index=False)
            st.download_button("📥 Export (CSV)", csv,
                                f"{view_key}_{datetime.now().strftime('%Y%m%d')}.csv",
                                "text/csv")
        else:
            st.info(f"No {view_metric_label} data found for the last {days_view} days. Start logging above!")

    # ── Tab 3: BMI Calculator ───────────────────────────────────────────────
    with tab3:
        st.markdown("<h3 style='color:#e2e8f0;font-size:1.1rem;margin-bottom:16px'>⚖️ BMI Calculator</h3>",
                    unsafe_allow_html=True)

        col_bmi1, col_bmi2 = st.columns(2)
        with col_bmi1:
            weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1)
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.5)
            save_bmi = st.checkbox("Save BMI to health records", value=True)

            if st.button("Calculate BMI", use_container_width=True):
                height_m = height / 100
                bmi = round(weight / (height_m ** 2), 1)

                if bmi < 18.5:
                    category, color, advice = "Underweight", "#f59e0b", "Consider consulting a nutritionist."
                elif bmi < 25:
                    category, color, advice = "Normal weight", "#22c55e", "Great! Keep maintaining your healthy lifestyle."
                elif bmi < 30:
                    category, color, advice = "Overweight", "#f59e0b", "Consider balanced diet and regular exercise."
                elif bmi < 35:
                    category, color, advice = "Obese (Class I)", "#ef4444", "Please consult a healthcare provider."
                else:
                    category, color, advice = "Obese (Class II/III)", "#ef4444", "Seek medical guidance urgently."

                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.9);border:1px solid rgba(79,142,247,0.2);
                     border-radius:16px;padding:24px;text-align:center;margin-top:16px">
                    <div style="font-size:3.5rem;font-weight:800;color:{color}">{bmi}</div>
                    <div style="color:#94a3b8;font-size:0.9rem">kg/m²</div>
                    <div style="color:{color};font-size:1.1rem;font-weight:600;margin-top:8px">{category}</div>
                    <div style="color:#94a3b8;font-size:0.85rem;margin-top:8px">{advice}</div>
                </div>
                """, unsafe_allow_html=True)

                if save_bmi:
                    db.log_health_metric(user_id=user_id, metric_type="bmi", value=bmi, unit="kg/m²")
                    st.success("✅ BMI saved to your health records.")

        with col_bmi2:
            st.markdown("""
            <div style="background:rgba(30,41,59,0.9);border:1px solid rgba(79,142,247,0.1);
                 border-radius:14px;padding:20px;margin-top:8px">
                <h4 style="color:#e2e8f0;margin:0 0 14px 0">BMI Categories</h4>
                <div style="color:#94a3b8;font-size:0.85rem;line-height:1.8">
                    <div><span style="color:#f59e0b">●</span> Underweight: &lt; 18.5</div>
                    <div><span style="color:#22c55e">●</span> Normal weight: 18.5 – 24.9</div>
                    <div><span style="color:#f59e0b">●</span> Overweight: 25 – 29.9</div>
                    <div><span style="color:#ef4444">●</span> Obese Class I: 30 – 34.9</div>
                    <div><span style="color:#ef4444">●</span> Obese Class II+: ≥ 35</div>
                </div>
                <hr style="border-color:rgba(148,163,184,0.1);margin:14px 0">
                <p style="color:#94a3b8;font-size:0.8rem;margin:0">
                    ⚠️ BMI is a screening tool, not a diagnostic measure.
                    Factors like muscle mass, age, and ethnicity affect interpretation.
                    Consult your doctor for a comprehensive health assessment.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 4: Import / Export ──────────────────────────────────────────────
    with tab4:
        col_imp, col_exp = st.columns(2)

        with col_imp:
            st.markdown("<h3 style='color:#e2e8f0;font-size:1rem;margin-bottom:12px'>📤 Import Health Data</h3>",
                        unsafe_allow_html=True)
            st.markdown("<p style='color:#94a3b8;font-size:0.85rem'>Paste JSON, CSV, or XML health data to bulk import.</p>",
                        unsafe_allow_html=True)

            with st.expander("📋 See sample JSON format"):
                st.code(generate_sample_json(), language="json")

            import_text = st.text_area("Paste your data here:", height=200)
            if st.button("Import Data", use_container_width=True) and import_text:
                try:
                    records = parse_auto(import_text)
                    if records:
                        imported = 0
                        for rec in records:
                            db.log_health_metric(
                                user_id=user_id,
                                metric_type=rec["metric_type"],
                                value=rec["value"],
                                unit=rec["unit"],
                                recorded_at=rec["recorded_at"],
                                value2=rec.get("value2"),
                                notes=rec.get("notes"),
                            )
                            imported += 1
                        st.success(f"✅ Imported {imported} health records successfully!")
                    else:
                        st.error("No valid records found. Check the format.")
                except Exception as e:
                    st.error(f"Import error: {e}")

        with col_exp:
            st.markdown("<h3 style='color:#e2e8f0;font-size:1rem;margin-bottom:12px'>📥 Export Health Data</h3>",
                        unsafe_allow_html=True)
            export_days = st.slider("Export period (days)", 7, 90, 30)
            export_mtype = st.selectbox("Metric to export", ["All"] + list(METRIC_INFO.keys()))

            if st.button("Generate Export", use_container_width=True):
                if export_mtype == "All":
                    all_data = db.get_health_metrics(user_id, days=export_days)
                else:
                    key = METRIC_INFO[export_mtype]["key"]
                    all_data = db.get_health_metrics(user_id, metric_type=key, days=export_days)

                if all_data:
                    csv_str = export_metrics_to_csv(all_data)
                    st.download_button(
                        "📥 Download CSV",
                        csv_str,
                        f"health_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        use_container_width=True,
                    )
                else:
                    st.info("No data found for the selected period.")
