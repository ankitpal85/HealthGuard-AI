"""
HealthGuard AI — Nutrition Tracker Page
Allows logging meals, macronutrients, water intake, and visualizing diet analytics.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os
import plotly.graph_objects as go
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db

# Theme colors matching visualizations.py
COLORS = {
    "primary": "#4f8ef7",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "purple": "#a855f7",
    "teal": "#14b8a6",
    "bg": "rgba(30,41,59,0.9)",
    "text": "#e2e8f0",
    "muted": "#94a3b8",
}


def show_nutrition():
    user_id = st.session_state.get("user_id", 1)

    st.markdown(
        '<div style="margin-bottom:24px">'
        '<h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;margin:0">🍎 Nutrition &amp; Diet</h1>'
        '<p style="color:#94a3b8;margin:4px 0 0 0">Log your meals, macronutrients, and monitor hydration levels</p>'
        '</div>',
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["📝 Log Nutrition", "📊 Diet Analytics"])

    # ── Tab 1: Log Nutrition ────────────────────────────────────────────────
    with tab1:
        col_form, col_water = st.columns([1.2, 1])

        with col_form:
            st.markdown("<h3 style='color:#e2e8f0;font-size:1.1rem;margin-bottom:14px'>🍴 Log a Meal</h3>",
                        unsafe_allow_html=True)
            
            with st.form("nutrition_form", clear_on_submit=True):
                meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
                food_items = st.text_input("What did you eat? *", placeholder="e.g. Oatmeal with fruits, Grilled chicken breast")
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    calories = st.number_input("Calories (kcal) *", min_value=0.0, max_value=5000.0, step=10.0, value=350.0)
                    protein = st.number_input("Protein (g)", min_value=0.0, max_value=200.0, step=1.0, value=20.0)
                with col_c2:
                    carbs = st.number_input("Carbs (g)", min_value=0.0, max_value=500.0, step=1.0, value=40.0)
                    fat = st.number_input("Fat (g)", min_value=0.0, max_value=200.0, step=1.0, value=10.0)

                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    logged_date = st.date_input("Date", value=date.today())
                with col_d2:
                    logged_time = st.time_input("Time", value=datetime.now().time())

                submitted = st.form_submit_button("✅ Log Meal", use_container_width=True)

                if submitted:
                    if not food_items.strip():
                        st.error("Please enter food description.")
                    else:
                        recorded_at = f"{logged_date} {logged_time.strftime('%H:%M')}"
                        db.log_nutrition(
                            user_id=user_id,
                            meal_type=meal_type.lower(),
                            calories=calories,
                            protein_g=protein,
                            carbs_g=carbs,
                            fat_g=fat,
                            food_items=food_items.strip(),
                            recorded_at=recorded_at
                        )
                        # Also log calories as a health metric for general trend charts
                        db.log_health_metric(
                            user_id=user_id,
                            metric_type="calories_burned", # or calorie intake
                            value=calories,
                            unit="kcal",
                            recorded_at=recorded_at,
                            notes=f"Intake: {meal_type} - {food_items}"
                        )
                        st.success(f"✅ logged {meal_type}: **{food_items}** ({calories} kcal)")
                        st.rerun()

        with col_water:
            st.markdown("<h3 style='color:#e2e8f0;font-size:1.1rem;margin-bottom:14px'>💧 Hydration Tracker</h3>",
                        unsafe_allow_html=True)
            
            # Show today's current water level
            today_str = date.today().strftime("%Y-%m-%d")
            water_logs = db.get_health_metrics(user_id, "water_intake", days=1)
            
            # Filter logs specifically for today
            today_water_logs = [w for w in water_logs if w["recorded_at"].startswith(today_str)]
            total_water = sum(w["value"] for w in today_water_logs)

            target_water = 2.5
            pct = min(100.0, (total_water / target_water) * 100)
            pct_int = min(100, int(pct))

            # Use native Streamlit components — no HTML parsing issues
            st.markdown("<div style='text-align:center;font-size:3rem'>💧</div>", unsafe_allow_html=True)
            st.metric(label="Today's Water Intake", value=f"{total_water:.2f} L", delta=f"Goal: {target_water} L")
            st.progress(pct_int, text=f"{pct:.0f}% of daily goal achieved")

            col_w1, col_w2 = st.columns(2)
            with col_w1:
                if st.button("➕ Add 250 ml (Glass)", use_container_width=True):
                    db.log_health_metric(
                        user_id=user_id,
                        metric_type="water_intake",
                        value=0.25,
                        unit="liters",
                        recorded_at=datetime.now().strftime("%Y-%m-%d %H:%M")
                    )
                    st.success("Added 250ml water!")
                    st.rerun()
            with col_w2:
                if st.button("➕ Add 500 ml (Bottle)", use_container_width=True):
                    db.log_health_metric(
                        user_id=user_id,
                        metric_type="water_intake",
                        value=0.5,
                        unit="liters",
                        recorded_at=datetime.now().strftime("%Y-%m-%d %H:%M")
                    )
                    st.success("Added 500ml water!")
                    st.rerun()

            # Custom Water Add
            with st.expander("Log Custom Hydration"):
                custom_water = st.number_input("Water Amount (liters)", min_value=0.05, max_value=5.0, value=0.33, step=0.05)
                if st.button("✅ Add Water", use_container_width=True):
                    db.log_health_metric(
                        user_id=user_id,
                        metric_type="water_intake",
                        value=custom_water,
                        unit="liters",
                        recorded_at=datetime.now().strftime("%Y-%m-%d %H:%M")
                    )
                    st.success(f"Added {custom_water} L water!")
                    st.rerun()


    # ── Tab 2: Diet Analytics ───────────────────────────────────────────────
    with tab2:
        logs = db.get_nutrition_logs(user_id, days=7)
        
        if not logs:
            st.info("No meal logs found. Start logging your meals on the first tab to view analytics.")
        else:
            df = pd.DataFrame(logs)
            df["date"] = pd.to_datetime(df["recorded_at"]).dt.date
            
            # Row 1: Daily Intake Chart & Macros Pie Chart
            col_chart_left, col_chart_right = st.columns([1.3, 1])

            with col_chart_left:
                # Group by date to show daily calories
                daily_cals = df.groupby("date")["calories"].sum().reset_index()
                daily_cals = daily_cals.sort_values("date")

                fig_cal = go.Figure()
                fig_cal.add_trace(go.Bar(
                    x=daily_cals["date"],
                    y=daily_cals["calories"],
                    name="Daily Intake",
                    marker_color=COLORS["primary"],
                    hovertemplate="<b>%{y:.0f} kcal</b><br>%{x}<extra></extra>",
                ))
                # Add Goal line
                fig_cal.add_shape(
                    type="line", line=dict(color=COLORS["danger"], width=2, dash="dash"),
                    x0=daily_cals["date"].min(), x1=daily_cals["date"].max(),
                    y0=2000, y1=2000
                )
                fig_cal.add_annotation(
                    x=daily_cals["date"].max(), y=2100, text="Calorie Target (2000 kcal)",
                    showarrow=False, font=dict(color=COLORS["danger"], size=10)
                )

                fig_cal.update_layout(
                    title="Daily Caloric Intake (Last 7 Days)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": COLORS["text"], "family": "Inter, sans-serif"},
                    margin={"l": 20, "r": 20, "t": 40, "b": 20},
                    xaxis={"gridcolor": "rgba(148,163,184,0.1)", "tickcolor": COLORS["muted"]},
                    yaxis={"gridcolor": "rgba(148,163,184,0.1)", "tickcolor": COLORS["muted"]},
                    height=300
                )
                st.plotly_chart(fig_cal, use_container_width=True, config={"displayModeBar": False})

            with col_chart_right:
                # Pie chart of macros for today
                today_str_check = date.today()
                today_logs = df[df["date"] == today_str_check]
                
                if not today_logs.empty:
                    p = today_logs["protein_g"].sum()
                    c = today_logs["carbs_g"].sum()
                    f = today_logs["fat_g"].sum()
                    
                    labels = ["Protein (g)", "Carbohydrates (g)", "Fat (g)"]
                    values = [p, c, f]
                    
                    fig_pie = go.Figure(go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.4,
                        marker_colors=[COLORS["success"], COLORS["warning"], COLORS["danger"]],
                        hovertemplate="<b>%{label}</b><br>%{value:.1f}g (%{percent})<extra></extra>"
                    ))
                    fig_pie.update_layout(
                        title="Today's Macro Ratio",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font={"color": COLORS["text"], "family": "Inter, sans-serif"},
                        margin={"l": 20, "r": 20, "t": 40, "b": 20},
                        height=300,
                        legend=dict(orientation="h", y=-0.1)
                    )
                    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
                else:
                    empty_html = (
                        '<div style="background:rgba(30,41,59,0.5);border:1px solid rgba(148,163,184,0.1);'
                        'border-radius:12px;padding:60px 20px;text-align:center;height:270px;">'
                        '<span style="color:#94a3b8;font-size:0.9rem">No meals logged today yet.<br>'
                        'Log today\'s meals to see macronutrient ratio.</span></div>'
                    )
                    st.markdown(empty_html, unsafe_allow_html=True)

            # Row 2: Meal History Table
            st.markdown("<h3 style='color:#e2e8f0;font-size:1.1rem;margin:24px 0 12px 0'>📜 Meal Log History</h3>",
                        unsafe_allow_html=True)
            
            history_df = df[["recorded_at", "meal_type", "food_items", "calories", "protein_g", "carbs_g", "fat_g"]].copy()
            history_df["meal_type"] = history_df["meal_type"].str.title()
            history_df.columns = ["Logged At", "Meal", "Food Eaten", "Calories (kcal)", "Protein (g)", "Carbs (g)", "Fat (g)"]
            
            st.dataframe(history_df, use_container_width=True, hide_index=True)

            # Export Button
            csv = history_df.to_csv(index=False)
            st.download_button(
                label="📥 Export Nutrition History (CSV)",
                data=csv,
                file_name=f"nutrition_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
