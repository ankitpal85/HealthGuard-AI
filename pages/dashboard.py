"""
HealthGuard AI — Health Dashboard Page
Shows key metrics, charts, goals, and medication adherence at a glance.
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db_manager as db
from utils.visualizations import (
    chart_health_metric,
    chart_medication_adherence,
    chart_health_radar,
    chart_steps_gauge,
)


def render_metric_card(label: str, value: str, delta: str = None,
                        icon: str = "📊", color: str = "#4f8ef7"):
    """Render a styled metric card."""
    delta_html = f'<p style="color:#22c55e;font-size:0.75rem;margin:0">{delta}</p>' if delta else ""
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
        border:1px solid rgba(79,142,247,0.2);
        border-radius:16px;
        padding:20px 22px;
        margin-bottom:8px;
        box-shadow:0 4px 24px rgba(0,0,0,0.3);
    ">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <span style="font-size:1.4rem">{icon}</span>
            <span style="color:#94a3b8;font-size:0.85rem;font-weight:500;text-transform:uppercase;letter-spacing:0.05em">{label}</span>
        </div>
        <p style="color:#e2e8f0;font-size:1.8rem;font-weight:700;margin:0;line-height:1">{value}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def show_dashboard():
    user_id = st.session_state.get("user_id", 1)

    st.markdown("""
    <div style="margin-bottom:24px">
        <h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;margin:0">
            📊 Health Dashboard
        </h1>
        <p style="color:#94a3b8;margin:4px 0 0 0">Your personal health overview</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick Stats ────────────────────────────────────────────────────────
    user = db.get_user(user_id)
    adherence = db.get_adherence_rate(user_id, days=7)
    active_meds = db.get_medications(user_id, active_only=True)
    goals = db.get_health_goals(user_id, active_only=True)

    # Latest metrics
    latest_steps = db.get_latest_metric(user_id, "steps")
    latest_hr = db.get_latest_metric(user_id, "heart_rate")
    latest_bp_sys = db.get_latest_metric(user_id, "blood_pressure_systolic")
    latest_sleep = db.get_latest_metric(user_id, "sleep_hours")
    latest_glucose = db.get_latest_metric(user_id, "blood_glucose")
    latest_weight = db.get_latest_metric(user_id, "weight")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            "Medication Adherence", f"{adherence}%",
            "Last 7 days", "💊",
            "#22c55e" if adherence >= 80 else "#f59e0b"
        )
    with col2:
        steps_val = f"{int(latest_steps['value']):,}" if latest_steps else "—"
        render_metric_card("Today's Steps", steps_val, "Goal: 10,000", "🚶", "#4f8ef7")
    with col3:
        hr_val = f"{int(latest_hr['value'])} bpm" if latest_hr else "—"
        render_metric_card("Heart Rate", hr_val, "Normal: 60-100", "❤️", "#ef4444")
    with col4:
        sleep_val = f"{latest_sleep['value']:.1f} hrs" if latest_sleep else "—"
        render_metric_card("Sleep", sleep_val, "Goal: 8 hours", "🌙", "#a855f7")

    # Second row
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        bp_val = f"{int(latest_bp_sys['value'])}" if latest_bp_sys else "—"
        render_metric_card("Blood Pressure (Sys)", f"{bp_val} mmHg", "Normal: <120", "🩺", "#14b8a6")
    with col6:
        glucose_val = f"{int(latest_glucose['value'])} mg/dL" if latest_glucose else "—"
        render_metric_card("Blood Glucose", glucose_val, "Normal: 70-140", "🍬", "#f59e0b")
    with col7:
        weight_val = f"{latest_weight['value']:.1f} kg" if latest_weight else "—"
        render_metric_card("Weight", weight_val, None, "⚖️", "#6366f1")
    with col8:
        render_metric_card("Active Medications", str(len(active_meds)), f"{len(goals)} goals active", "💊", "#4f8ef7")

    st.markdown("<hr style='border-color:rgba(148,163,184,0.1);margin:24px 0'>", unsafe_allow_html=True)

    # ── Charts Row ─────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        metric_options = {
            "Steps": "steps",
            "Heart Rate": "heart_rate",
            "Blood Pressure (Sys)": "blood_pressure_systolic",
            "Blood Glucose": "blood_glucose",
            "Sleep Hours": "sleep_hours",
            "Weight": "weight",
        }
        selected_metric_label = st.selectbox(
            "📈 Trend Chart",
            list(metric_options.keys()),
            label_visibility="visible",
            key="dashboard_metric_select"
        )
        selected_metric = metric_options[selected_metric_label]
        metrics = db.get_health_metrics(user_id, metric_type=selected_metric, days=30)
        fig = chart_health_metric(metrics, selected_metric)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        # Steps gauge
        steps_count = float(latest_steps["value"]) if latest_steps else 0
        gauge_fig = chart_steps_gauge(steps_count)
        st.plotly_chart(gauge_fig, use_container_width=True, config={"displayModeBar": False})

        # Adherence mini info
        st.markdown(f"""
        <div style="
            background:linear-gradient(135deg,rgba(34,197,94,0.1),rgba(20,184,166,0.1));
            border:1px solid rgba(34,197,94,0.2);
            border-radius:12px;padding:16px;text-align:center;
        ">
            <div style="font-size:2.5rem;font-weight:700;color:#22c55e">{adherence}%</div>
            <div style="color:#94a3b8;font-size:0.85rem">7-Day Medication Adherence</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Radar Chart ────────────────────────────────────────────────────────
    col_radar, col_meds = st.columns([1, 1])

    with col_radar:
        latest_for_radar = {}
        for mtype in ["steps", "heart_rate", "sleep_hours", "water_intake", "oxygen_saturation"]:
            m = db.get_latest_metric(user_id, mtype)
            if m:
                latest_for_radar[mtype] = m["value"]
        radar_fig = chart_health_radar(latest_for_radar)
        st.plotly_chart(radar_fig, use_container_width=True, config={"displayModeBar": False})

    with col_meds:
        # Medication adherence bar chart
        logs = db.get_medication_logs(user_id, days=7)
        adh_fig = chart_medication_adherence(logs, days=7)
        st.plotly_chart(adh_fig, use_container_width=True, config={"displayModeBar": False})

    # ── Health Goals ────────────────────────────────────────────────────────
    if goals:
        st.markdown("""
        <h3 style="color:#e2e8f0;font-size:1.2rem;font-weight:600;margin:16px 0 12px 0">
            🎯 Active Health Goals
        </h3>
        """, unsafe_allow_html=True)

        for goal in goals:
            progress = min(100, (goal["current_value"] / goal["target_value"]) * 100) if goal["target_value"] > 0 else 0
            color = "#22c55e" if progress >= 80 else "#f59e0b" if progress >= 50 else "#4f8ef7"
            col_g1, col_g2 = st.columns([3, 1])
            with col_g1:
                st.markdown(f"""
                <div style="margin-bottom:12px">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                        <span style="color:#e2e8f0;font-size:0.9rem">{goal['goal_type'].replace('_',' ').title()}</span>
                        <span style="color:#94a3b8;font-size:0.85rem">{goal['current_value']:.1f} / {goal['target_value']:.1f} {goal['unit']}</span>
                    </div>
                    <div style="background:rgba(148,163,184,0.1);border-radius:99px;height:8px;overflow:hidden">
                        <div style="background:{color};width:{progress:.1f}%;height:100%;border-radius:99px;transition:width 0.3s"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_g2:
                st.markdown(f'<p style="color:{color};text-align:right;font-weight:700;margin-top:4px">{progress:.0f}%</p>', unsafe_allow_html=True)

    # ── Safety Disclaimer ──────────────────────────────────────────────────
    st.markdown("""
    <div style="
        background:rgba(245,158,11,0.08);
        border:1px solid rgba(245,158,11,0.2);
        border-radius:12px;padding:14px 18px;margin-top:24px;
    ">
        <span style="color:#f59e0b;font-weight:600">⚠️ Medical Disclaimer</span>
        <span style="color:#94a3b8;font-size:0.85rem;margin-left:8px">
            HealthGuard AI is for informational and tracking purposes only.
            It is not a substitute for professional medical advice, diagnosis, or treatment.
            Always consult a qualified healthcare provider for medical decisions.
            In case of emergency, call <strong style="color:#ef4444">112</strong> (India) immediately.
        </span>
    </div>
    """, unsafe_allow_html=True)
