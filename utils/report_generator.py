"""
Automated Health Report Generator for HealthGuard AI
Creates downloadable HTML and Markdown health summary reports with adherence stats, vitals, and risk scores.
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db
from utils import analytics


def generate_comprehensive_report(user_id: int) -> dict:
    """
    Generate a full health summary report with metrics, risk scores, adherence, and insights.

    Returns:
        Dict with keys: 'markdown', 'html', 'filename'
    """
    user = db.get_user(user_id) or {"name": "User", "age": 40, "gender": "Male"}
    cvd = analytics.calculate_cardiovascular_risk(user_id)
    diab = analytics.calculate_diabetes_risk(user_id)
    med_logs = db.get_medication_logs(user_id, days=7)
    adherence_rate = db.get_adherence_rate(user_id, days=7)
    taken_count = sum(1 for l in med_logs if l["status"] == "taken") if med_logs else 0
    missed_count = sum(1 for l in med_logs if l["status"] == "missed") if med_logs else 0
    recent_metrics = db.get_health_metrics(user_id, days=7)
    anomalies = analytics.detect_anomalies(user_id, days=7)

    today_str = datetime.now().strftime("%B %d, %Y")

    # Generate Markdown
    md_lines = [
        f"# 🏥 HealthGuard AI — Comprehensive Health Summary Report",
        f"**Patient Name:** {user['name']}  |  **Age:** {user.get('age', 'N/A')}  |  **Date:** {today_str}\n",
        "---",
        "## 📊 1. Predictive Risk Assessment",
        f"- **10-Year Cardiovascular Disease (CVD) Risk:** {cvd.get('risk_percentage', 0)}% ({cvd.get('risk_category', 'Normal')})",
        f"  - *Advice:* {cvd.get('advice', '')}",
        f"- **Type 2 Diabetes Risk Category:** {diab.get('risk_category', 'Normal')}",
        f"  - *Advice:* {diab.get('advice', '')}\n",
        "## 💊 2. Medication Adherence (Last 7 Days)",
        f"- **Adherence Rate:** {adherence_rate}%",
        f"- **Doses Taken:** {taken_count}",
        f"- **Doses Missed:** {missed_count}\n",
        "## 📈 3. Recent Vitals Summary",
    ]

    for m in recent_metrics[:8]:
        md_lines.append(f"- **{m['metric_type'].replace('_',' ').title()}:** {m['value']} {m['unit']} (Recorded: {m['recorded_at']})")

    if anomalies:
        md_lines.append("\n## 🚨 4. Flagged Health Anomalies")
        for a in anomalies:
            md_lines.append(f"- [{a['severity']}] **{a['display_name']}**: {a['value']} {a['unit']} ({a['reason']})")

    md_lines.append("\n---\n*Report compiled autonomously by HealthGuard AI Medical Engine.*")
    markdown_content = "\n".join(md_lines)

    # HTML format for web preview/printing
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HealthGuard AI Report - {user['name']}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 30px; }}
            .card {{ background: #1e293b; border-radius: 12px; padding: 24px; margin-bottom: 20px; border: 1px solid rgba(79,142,247,0.2); }}
            h1 {{ color: #4f8ef7; }}
            h2 {{ color: #38bdf8; border-bottom: 1px solid rgba(148,163,184,0.2); padding-bottom: 8px; }}
            .badge {{ display: inline-block; padding: 4px 12px; border-radius: 99px; font-weight: bold; background: #4f8ef7; color: white; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🏥 HealthGuard AI Clinical Report</h1>
            <p><strong>Patient:</strong> {user['name']} | <strong>Generated:</strong> {today_str}</p>
        </div>
        <div class="card">
            <h2>Predictive Health Risk Scores</h2>
            <p><strong>Cardiovascular Risk:</strong> <span class="badge">{cvd.get('risk_percentage', 0)}% ({cvd.get('risk_category')})</span></p>
            <p><strong>Diabetes Risk:</strong> <span class="badge">{diab.get('risk_category')}</span></p>
        </div>
        <div class="card">
            <h2>Medication Adherence Rate</h2>
            <p>7-Day Adherence: <strong>{adherence_rate}%</strong> ({taken_count} doses taken)</p>
        </div>
    </body>
    </html>
    """

    filename = f"HealthGuard_Report_{user['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.html"

    return {
        "markdown": markdown_content,
        "html": html_content,
        "filename": filename
    }
