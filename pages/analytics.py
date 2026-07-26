"""
HealthGuard AI — Risk & Predictive Analytics Page
Computes disease risk profiles, vital signs anomalies, trend forecasting, and compiles reports.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db
from utils import analytics
from tools.clinical_tools import generate_automated_report

COLORS = {
    "primary": "#4f8ef7",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "purple": "#a855f7",
    "teal": "#14b8a6",
    "text": "#e2e8f0",
    "muted": "#94a3b8",
}


def draw_risk_gauge(title: str, val: float, color: str, subtitle: str) -> go.Figure:
    """Create a gauge chart representing the risk percentage."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={"suffix": "%", "font": {"color": COLORS["text"], "size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLORS["muted"]},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "rgba(30,41,59,0.5)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 10], "color": "rgba(34,197,94,0.1)"},
                {"range": [10, 20], "color": "rgba(245,158,11,0.1)"},
                {"range": [20, 100], "color": "rgba(239,68,68,0.1)"},
            ],
        },
        title={"text": title, "font": {"color": COLORS["text"], "size": 16}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": COLORS["text"], "family": "Inter, sans-serif"},
        height=200,
        margin={"l": 20, "r": 20, "t": 40, "b": 10},
    )
    return fig


def show_analytics():
    user_id = st.session_state.get("user_id", 1)

    st.markdown("""
    <div style="margin-bottom:24px">
        <h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;margin:0">
            📈 Health Risk & Analytics
        </h1>
        <p style="color:#94a3b8;margin:4px 0 0 0">Predictive disease risk profiles, vital signs anomaly warnings, and trend forecasts</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🫀 Predictive Disease Risks", 
        "🔮 Trend Forecasting", 
        "🚨 Anomaly Alerts", 
        "📄 Automated Reports"
    ])

    # ── Tab 1: Disease Risks ───────────────────────────────────────────────
    with tab1:
        col_cvd, col_diab = st.columns(2)

        with col_cvd:
            cvd = analytics.calculate_cardiovascular_risk(user_id)
            if "error" in cvd:
                st.info("Log vital signs (BP, weight/BMI) to view Cardiovascular Risk Assessment.")
            else:
                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.4);border:1px solid rgba(79,142,247,0.15);
                     border-radius:14px;padding:20px;margin-bottom:14px">
                    <h3 style="color:#e2e8f0;font-size:1.2rem;margin:0 0 10px 0">🫀 Cardiovascular Risk</h3>
                    <p style="color:#94a3b8;font-size:0.85rem">10-year probability of experiencing a heart-related event (Framingham scale)</p>
                </div>
                """, unsafe_allow_html=True)

                fig_cvd = draw_risk_gauge("10-Year CVD Risk", cvd["risk_percentage"], cvd["color"], cvd["risk_category"])
                st.plotly_chart(fig_cvd, use_container_width=True, config={"displayModeBar": False})

                # Parameters
                smoker_status = "Yes" if cvd["is_smoker"] else "No"
                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.7);border-radius:12px;padding:16px;margin-bottom:12px">
                    <div style="color:{cvd['color']};font-weight:700;font-size:1.2rem">{cvd['risk_category']}</div>
                    <div style="color:#94a3b8;font-size:0.85rem;margin-top:6px"><strong>Clinical Advice:</strong> {cvd['advice']}</div>
                    <hr style="border-color:rgba(148,163,184,0.1);margin:10px 0">
                    <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#94a3b8">
                        <span>Age: <strong>{cvd['age']}</strong></span>
                        <span>Gender: <strong>{cvd['gender']}</strong></span>
                        <span>Systolic BP: <strong>{cvd['systolic_bp']:.0f} mmHg</strong></span>
                        <span>BMI: <strong>{cvd['bmi']:.1f} kg/m²</strong></span>
                        <span>Smoker: <strong>{smoker_status}</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col_diab:
            diab = analytics.calculate_diabetes_risk(user_id)
            if "error" in diab:
                st.info("Log health metrics (glucose, weight/BMI) to view Diabetes Risk Profile.")
            else:
                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.4);border:1px solid rgba(79,142,247,0.15);
                     border-radius:14px;padding:20px;margin-bottom:14px">
                    <h3 style="color:#e2e8f0;font-size:1.2rem;margin:0 0 10px 0">🍬 Type-2 Diabetes Risk</h3>
                    <p style="color:#94a3b8;font-size:0.85rem">10-year risk probability of developing Type-2 Diabetes (FINDRISC scale)</p>
                </div>
                """, unsafe_allow_html=True)

                fig_diab = draw_risk_gauge("Diabetes Risk Profile", diab["risk_percentage"], diab["color"], diab["risk_category"])
                st.plotly_chart(fig_diab, use_container_width=True, config={"displayModeBar": False})

                # Parameters
                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.7);border-radius:12px;padding:16px;margin-bottom:12px">
                    <div style="color:{diab['color']};font-weight:700;font-size:1.2rem">{diab['risk_category']}</div>
                    <div style="color:#94a3b8;font-size:0.85rem;margin-top:6px"><strong>Clinical Advice:</strong> {diab['advice']}</div>
                    <hr style="border-color:rgba(148,163,184,0.1);margin:10px 0">
                    <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#94a3b8">
                        <span>FINDRISC Score: <strong>{diab['score']}/26</strong></span>
                        <span>Glucose: <strong>{diab['glucose']:.0f} mg/dL</strong></span>
                        <span>BMI: <strong>{diab['bmi']:.1f} kg/m²</strong></span>
                        <span>7-day Steps Avg: <strong>{diab['avg_steps']:,}</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 2: Trend Forecasting ───────────────────────────────────────────
    with tab2:
        st.markdown("<h3 style='color:#e2e8f0;font-size:1.1rem;margin-bottom:12px'>🔮 7-Day Trend Prediction</h3>",
                    unsafe_allow_html=True)
        
        metric_choices = {
            "Daily Steps": "steps",
            "Weight (kg)": "weight",
            "Blood Glucose (mg/dL)": "blood_glucose",
            "Sleep Duration (hours)": "sleep_hours",
            "Water Intake (liters)": "water_intake",
        }
        
        select_metric_label = st.selectbox("Select a metric to forecast", list(metric_choices.keys()))
        mtype = metric_choices[select_metric_label]
        
        fore = analytics.forecast_metric_trends(user_id, mtype)
        
        if "error" in fore:
            st.warning(f"⚠️ {fore['error']}. Log at least 4 entries for this vital metric to build trend regression models.")
        else:
            # Let's plot historical trend + predicted trend
            history = db.get_health_metrics(user_id, metric_type=mtype, days=14)
            history_df = pd.DataFrame(history)
            history_df["date"] = pd.to_datetime(history_df["recorded_at"]).dt.strftime("%Y-%m-%d")
            history_df = history_df.groupby("date")["value"].mean().reset_index()
            history_df = history_df.sort_values("date")

            forecast_df = pd.DataFrame(fore["forecast"])

            # Create interactive line chart
            fig_fore = go.Figure()
            # History
            fig_fore.add_trace(go.Scatter(
                x=history_df["date"], y=history_df["value"],
                mode="lines+markers", name="Historical Average",
                line=dict(color=COLORS["primary"], width=2.5),
                marker=dict(size=6)
            ))
            # Forecast
            fig_fore.add_trace(go.Scatter(
                x=forecast_df["date"], y=forecast_df["value"],
                mode="lines+markers", name="7-Day Linear Forecast",
                line=dict(color=COLORS["purple"], width=2.5, dash="dash"),
                marker=dict(size=6, symbol="diamond")
            ))

            fig_fore.update_layout(
                title=f"{select_metric_label} Forecast Summary",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": COLORS["text"], "family": "Inter, sans-serif"},
                margin={"l": 20, "r": 20, "t": 40, "b": 20},
                xaxis={"gridcolor": "rgba(148,163,184,0.1)", "tickcolor": COLORS["muted"]},
                yaxis={"gridcolor": "rgba(148,163,184,0.1)", "tickcolor": COLORS["muted"]},
                height=350,
                legend=dict(orientation="h", y=-0.15)
            )
            st.plotly_chart(fig_fore, use_container_width=True, config={"displayModeBar": False})

            # Trend Summary Cards
            col_t1, col_t2 = st.columns([1, 1.5])
            with col_t1:
                slope_val = fore["slope"]
                dir_icon = "📈" if slope_val > 0 else "📉" if slope_val < 0 else "➡️"
                st.metric(
                    label="Calculated Daily Trajectory",
                    value=f"{slope_val:+.2f} {fore['unit']}/day",
                    delta=f"{'Upward' if slope_val > 0 else 'Downward'} Trend",
                    delta_color="normal" if mtype != "weight" else ("inverse" if slope_val > 0 else "normal")
                )
            with col_t2:
                st.markdown(f"""
                <div style="background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.3);
                     border-radius:12px;padding:16px;height:100%">
                    <h5 style="color:{COLORS['purple']};margin:0 0 6px 0">🔮 Trend Insights</h5>
                    <p style="color:#e2e8f0;font-size:0.85rem;margin:0">{fore['insight']}</p>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 3: Anomaly Alerts ──────────────────────────────────────────────
    with tab3:
        st.markdown("<h3 style='color:#e2e8f0;font-size:1.1rem;margin-bottom:14px'>🚨 Recent Health Anomalies (Last 14 Days)</h3>",
                    unsafe_allow_html=True)
        
        anoms = analytics.detect_anomalies(user_id, days=14)
        
        if not anoms:
            st.success("✅ **Excellent!** All of your logged health metrics are within clinical and statistical normal bounds.")
        else:
            for an in anoms:
                bg_color = "rgba(239,68,68,0.1)" if an["severity"] == "Critical" else "rgba(245,158,11,0.1)"
                border_color = "rgba(239,68,68,0.3)" if an["severity"] == "Critical" else "rgba(245,158,11,0.3)"
                text_color = COLORS["danger"] if an["severity"] == "Critical" else COLORS["warning"]
                severity_badge = "CRITICAL ALERT" if an["severity"] == "Critical" else "WARNING"

                st.markdown(f"""
                <div style="
                    background:{bg_color};
                    border:1px solid {border_color};
                    border-radius:12px;
                    padding:16px;
                    margin-bottom:12px;
                ">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <span style="color:{text_color};font-weight:700;font-size:0.75rem;letter-spacing:0.05em">{severity_badge}</span>
                        <span style="color:#94a3b8;font-size:0.75rem">{an['recorded_at']}</span>
                    </div>
                    <h4 style="color:#e2e8f0;margin:6px 0;font-size:1rem">{an['display_name']}: {an['value']} {an['unit']}</h4>
                    <p style="color:#94a3b8;font-size:0.85rem;margin:0">{an['reason']}</p>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 4: Automated Reports ───────────────────────────────────────────
    with tab4:
        st.markdown("<h3 style='color:#e2e8f0;font-size:1.1rem;margin-bottom:12px'>📄 Generate Health Report</h3>",
                    unsafe_allow_html=True)
        st.markdown("<p style='color:#94a3b8;font-size:0.85rem'>Compile all your logged health metrics, medication logs, and clinical risk analysis into a unified medical report.</p>",
                    unsafe_allow_html=True)

        report_days = st.slider("Report duration (days)", min_value=3, max_value=30, value=7, key="report_slider_days")
        
        if st.button("🚀 Compile Automated Clinical Report", use_container_width=True):
            with st.spinner("Generating clinical summary..."):
                report_md = generate_automated_report(user_id, days=report_days)
                
                st.session_state.compiled_report = report_md
                st.success("Report Compiled Successfully!")

        if "compiled_report" in st.session_state:
            st.markdown("<hr style='border-color:rgba(148,163,184,0.1);margin:20px 0'>", unsafe_allow_html=True)
            
            with st.container():
                st.markdown(f"""
                <div style="
                    background:rgba(30,41,59,0.5);
                    border:1px solid rgba(79,142,247,0.1);
                    border-radius:14px;
                    padding:24px;
                    max-height:450px;
                    overflow-y:auto;
                    font-family:monospace;
                    margin-bottom:16px;
                ">
                """, unsafe_allow_html=True)
                st.markdown(st.session_state.compiled_report)
                st.markdown("</div>", unsafe_allow_html=True)

            # Download Button
            st.download_button(
                label="📥 Download Clinical Report (.md)",
                data=st.session_state.compiled_report,
                file_name=f"health_report_{date.today().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True
            )
