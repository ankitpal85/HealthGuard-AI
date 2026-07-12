"""
Visualization utilities for HealthGuard AI
Creates Plotly charts for health metrics and medication adherence.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta


# ── Color Palette ─────────────────────────────────────────────────────────────
COLORS = {
    "primary": "#4f8ef7",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "purple": "#a855f7",
    "teal": "#14b8a6",
    "bg": "#0f172a",
    "card": "#1e293b",
    "text": "#e2e8f0",
    "muted": "#94a3b8",
}

CHART_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": COLORS["text"], "family": "Inter, sans-serif"},
    "margin": {"l": 20, "r": 20, "t": 40, "b": 20},
    "xaxis": {
        "gridcolor": "rgba(148,163,184,0.1)",
        "linecolor": "rgba(148,163,184,0.2)",
        "tickcolor": COLORS["muted"],
    },
    "yaxis": {
        "gridcolor": "rgba(148,163,184,0.1)",
        "linecolor": "rgba(148,163,184,0.2)",
        "tickcolor": COLORS["muted"],
    },
    "legend": {"bgcolor": "rgba(0,0,0,0)"},
}


def chart_health_metric(metrics: list, metric_type: str, title: str = None) -> go.Figure:
    """
    Create a line chart for a health metric over time.

    Args:
        metrics: List of dicts from db_manager.get_health_metrics().
        metric_type: The metric type (e.g. 'steps', 'heart_rate').
        title: Optional chart title.

    Returns:
        Plotly Figure.
    """
    if not metrics:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False,
                           font={"color": COLORS["muted"], "size": 14})
        fig.update_layout(**CHART_LAYOUT, height=300)
        return fig

    df = pd.DataFrame(metrics)
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])
    df = df.sort_values("recorded_at")

    unit = df["unit"].iloc[0] if "unit" in df.columns else ""
    display_name = metric_type.replace("_", " ").title()
    chart_title = title or f"{display_name} Over Time"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["recorded_at"],
        y=df["value"],
        mode="lines+markers",
        name=display_name,
        line={"color": COLORS["primary"], "width": 2.5, "shape": "spline"},
        marker={"size": 7, "color": COLORS["primary"]},
        fill="tozeroy",
        fillcolor=f"rgba(79,142,247,0.08)",
        hovertemplate=f"<b>%{{y:.1f}} {unit}</b><br>%{{x|%b %d, %H:%M}}<extra></extra>",
    ))

    layout = {**CHART_LAYOUT,
               "title": {"text": chart_title, "font": {"size": 16, "color": COLORS["text"]}},
               "height": 320,
               "yaxis": {**CHART_LAYOUT["yaxis"], "title": unit}}
    fig.update_layout(**layout)
    return fig


def chart_medication_adherence(logs: list, days: int = 7) -> go.Figure:
    """
    Create a bar chart showing daily medication adherence.

    Args:
        logs: List of medication log dicts.
        days: Number of days to display.

    Returns:
        Plotly Figure.
    """
    if not logs:
        fig = go.Figure()
        fig.add_annotation(text="No medication logs available", showarrow=False,
                           font={"color": COLORS["muted"], "size": 14})
        fig.update_layout(**CHART_LAYOUT, height=300)
        return fig

    df = pd.DataFrame(logs)
    df["date"] = pd.to_datetime(df["scheduled_at"]).dt.date

    # Build date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)
    date_range = pd.date_range(start_date, end_date).date

    summary = []
    for date in date_range:
        day_df = df[df["date"] == date]
        taken = len(day_df[day_df["status"] == "taken"])
        missed = len(day_df[day_df["status"] == "missed"])
        pending = len(day_df[day_df["status"] == "pending"])
        total = len(day_df)
        rate = round((taken / total * 100) if total > 0 else 0, 1)
        summary.append({"date": date, "taken": taken, "missed": missed, "pending": pending, "rate": rate})

    sdf = pd.DataFrame(summary)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sdf["date"], y=sdf["taken"], name="Taken",
        marker_color=COLORS["success"],
        hovertemplate="<b>Taken: %{y}</b><br>%{x}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=sdf["date"], y=sdf["missed"], name="Missed",
        marker_color=COLORS["danger"],
        hovertemplate="<b>Missed: %{y}</b><br>%{x}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=sdf["date"], y=sdf["pending"], name="Pending",
        marker_color=COLORS["warning"],
        hovertemplate="<b>Pending: %{y}</b><br>%{x}<extra></extra>",
    ))

    layout = {**CHART_LAYOUT,
               "barmode": "stack",
               "title": {"text": "Medication Adherence (Daily)", "font": {"size": 16, "color": COLORS["text"]}},
               "height": 320,
               "legend": {"bgcolor": "rgba(0,0,0,0)", "orientation": "h", "y": -0.2}}
    fig.update_layout(**layout)
    return fig


def chart_health_radar(latest_metrics: dict) -> go.Figure:
    """
    Create a radar chart showing current health status across dimensions.

    Args:
        latest_metrics: Dict of {metric_type: value} for the latest readings.

    Returns:
        Plotly Figure.
    """
    NORMAL_RANGES = {
        "steps": (0, 10000),
        "heart_rate": (60, 100),
        "sleep_hours": (0, 8),
        "water_intake": (0, 2.5),
        "oxygen_saturation": (0, 98),
    }

    labels = []
    values = []
    for metric, (lo, hi) in NORMAL_RANGES.items():
        if metric in latest_metrics and hi > 0:
            pct = min(100, (latest_metrics[metric] / hi) * 100)
            labels.append(metric.replace("_", " ").title())
            values.append(round(pct, 1))

    if not labels:
        fig = go.Figure()
        fig.add_annotation(text="Log health metrics to see radar chart",
                           showarrow=False, font={"color": COLORS["muted"], "size": 14})
        fig.update_layout(**CHART_LAYOUT, height=350)
        return fig

    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(79,142,247,0.15)",
        line={"color": COLORS["primary"], "width": 2},
        marker={"size": 6, "color": COLORS["primary"]},
        name="Health Status",
        hovertemplate="<b>%{theta}</b><br>Score: %{r:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        polar={
            "bgcolor": "rgba(0,0,0,0)",
            "radialaxis": {"visible": True, "range": [0, 100],
                           "gridcolor": "rgba(148,163,184,0.15)",
                           "linecolor": "rgba(148,163,184,0.15)",
                           "tickfont": {"color": COLORS["muted"], "size": 10}},
            "angularaxis": {"gridcolor": "rgba(148,163,184,0.15)",
                            "linecolor": "rgba(148,163,184,0.15)",
                            "tickfont": {"color": COLORS["text"], "size": 12}},
        },
        title={"text": "Health Wellness Radar", "font": {"size": 16, "color": COLORS["text"]}},
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": COLORS["text"], "family": "Inter, sans-serif"},
        height=380,
        margin={"l": 40, "r": 40, "t": 50, "b": 20},
    )
    return fig


def chart_steps_gauge(steps: float, goal: float = 10000) -> go.Figure:
    """Create a gauge chart for step count vs goal."""
    pct = min(100, (steps / goal) * 100)
    color = COLORS["success"] if pct >= 80 else COLORS["warning"] if pct >= 50 else COLORS["danger"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=steps,
        delta={"reference": goal, "valueformat": ".0f"},
        number={"valueformat": ".0f", "font": {"color": COLORS["text"], "size": 28}},
        gauge={
            "axis": {"range": [0, goal * 1.2], "tickcolor": COLORS["muted"]},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "rgba(30,41,59,0.5)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, goal * 0.5], "color": "rgba(239,68,68,0.1)"},
                {"range": [goal * 0.5, goal * 0.8], "color": "rgba(245,158,11,0.1)"},
                {"range": [goal * 0.8, goal * 1.2], "color": "rgba(34,197,94,0.1)"},
            ],
            "threshold": {"line": {"color": COLORS["text"], "width": 2},
                          "thickness": 0.75, "value": goal},
        },
        title={"text": "Daily Steps", "font": {"color": COLORS["muted"], "size": 14}},
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": COLORS["text"], "family": "Inter, sans-serif"},
        height=250,
        margin={"l": 20, "r": 20, "t": 20, "b": 10},
    )
    return fig
