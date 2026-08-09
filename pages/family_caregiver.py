"""
Family Health Monitoring & Caregiver Notifications Page for HealthGuard AI
Provides multi-member profile management, caregiver alert contact setup,
and real-time vitals monitoring with emergency alert triggers.
"""

import streamlit as st
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db


def show_family_caregiver():
    user_id = st.session_state.get("user_id", 1)
    user = db.get_user(user_id) or {"name": "User", "id": 1}

    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(168,85,247,0.15), rgba(79,142,247,0.15));
                border: 1px solid rgba(168,85,247,0.3); border-radius: 16px; padding: 20px; margin-bottom: 24px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="font-size: 2.2rem;">👨‍👩‍👧</div>
            <div>
                <h2 style="margin:0; color:#a855f7; font-size:1.5rem;">Family Health & Caregiver Network</h2>
                <p style="margin:4px 0 0; color:#94a3b8; font-size:0.9rem;">
                    Multi-Profile Family Monitoring • Caregiver Alert Contacts • Real-Time Vitals Threshold Alerts
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "👨‍👩‍👧 Family Profiles",
        "🔔 Caregiver Contacts & Alerts",
        "🚨 Real-Time Vitals Alert Log"
    ])

    # ── TAB 1: Family Member Profiles ──────────────────────────────────────
    with tab1:
        st.markdown("### 👨‍👩‍👧 Manage Family Profiles")
        st.markdown("Add and manage health records for family members (Parents, Spouse, Children).")

        with st.form("add_family_member_form"):
            c1, c2 = st.columns(2)
            with c1:
                mem_name = st.text_input("Full Name*", placeholder="e.g. Ramesh Pal (Father)")
                relation = st.selectbox("Relationship", ["Father", "Mother", "Spouse", "Child", "Sibling", "Dependent"])
                mem_age = st.number_input("Age", min_value=1, max_value=110, value=65)
            with c2:
                mem_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                mem_bg = st.selectbox("Blood Group", ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"])
                mem_notes = st.text_area("Medical Notes / Conditions", placeholder="Hypertension, Type 2 Diabetes, allergic to Penicillin")

            if st.form_submit_button("Add Family Profile"):
                if mem_name:
                    db.add_family_member(user_id, mem_name, relation, mem_age, mem_gender, mem_bg, mem_notes)
                    st.success(f"✅ Added family profile for {mem_name} ({relation})!")
                    st.rerun()

        members = db.get_family_members(user_id)
        if members:
            st.markdown("#### 📁 Registered Family Profiles")
            for m in members:
                with st.expander(f"👤 **{m['name']}** ({m['relationship']}) — Age: {m['age']}, Blood Group: {m['blood_group']}"):
                    st.markdown(f"**Medical Notes:** {m['medical_notes'] or 'None recorded'}")
                    if st.button(f"Switch Active View to {m['name']}", key=f"switch_{m['id']}"):
                        st.info(f"Switched monitoring context to {m['name']}.")

    # ── TAB 2: Caregiver Contacts ──────────────────────────────────────────
    with tab2:
        st.markdown("### 🔔 Caregiver Emergency Contacts & Alert Setup")
        st.markdown("Configure caregiver phone numbers and emails to receive simulated SMS and Email alerts when health metrics exceed critical safety thresholds.")

        with st.form("add_caregiver_form"):
            col_cg1, col_cg2 = st.columns(2)
            with col_cg1:
                cg_name = st.text_input("Caregiver Name*", placeholder="e.g. Dr. Anita Sharma / Priya Pal")
                cg_rel = st.text_input("Relationship", value="Daughter / Primary Caregiver")
                cg_phone = st.text_input("Phone Number*", placeholder="+91 98765 43210")
            with col_cg2:
                cg_email = st.text_input("Email Address", placeholder="caregiver@healthguard.ai")
                notify_crit = st.checkbox("Send SMS Alert on Critical Vitals (BP >180, Glucose >250)", value=True)
                notify_miss = st.checkbox("Send Alert on Missed Medication Doses", value=True)

            if st.form_submit_button("Save Caregiver Contact"):
                if cg_name and cg_phone:
                    db.add_caregiver_contact(user_id, cg_name, cg_rel, cg_phone, cg_email, int(notify_crit), int(notify_miss))
                    st.success(f"✅ Caregiver contact saved for {cg_name}!")
                    st.rerun()

        cg_list = db.get_caregiver_contacts(user_id)
        if cg_list:
            st.markdown("#### 📞 Active Caregivers")
            for cg in cg_list:
                st.info(f"📞 **{cg['name']}** ({cg['relationship']}) | Phone: `{cg['phone']}` | Email: `{cg['email']}` | Alerts: Critical Vitals ({'Yes' if cg['notify_critical'] else 'No'})")

    # ── TAB 3: Real-Time Health Alerts Log ──────────────────────────────────
    with tab3:
        st.markdown("### 🚨 Real-Time Health Threshold Alert Log")

        # Test trigger simulated critical alert
        st.markdown("#### ⚡ Test Real-Time Critical Alert System")
        test_col1, test_col2 = st.columns(2)
        with test_col1:
            metric_choice = st.selectbox("Select Metric", ["Blood Pressure Systolic", "Blood Glucose", "Heart Rate"])
            val_input = st.number_input("Value to Test", value=185.0)
        with test_col2:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            if st.button("Trigger Test Critical Alert"):
                if val_input >= 180.0 and metric_choice == "Blood Pressure Systolic":
                    db.log_health_alert(
                        user_id, "Critical Vitals", "Emergency",
                        f"CRITICAL HIGH BP DETECTED: {val_input} mmHg. Exceeds emergency threshold (180 mmHg). Caregivers notified via SMS.",
                        "blood_pressure_systolic", val_input, ">180 mmHg"
                    )
                    st.error("🚨 CRITICAL ALERT LOGGED! Automated emergency notification dispatched to active caregivers.")
                elif val_input >= 250.0 and metric_choice == "Blood Glucose":
                    db.log_health_alert(
                        user_id, "Critical Vitals", "High",
                        f"CRITICAL GLUCOSE SPIKE: {val_input} mg/dL. Caregiver SMS alert sent.",
                        "blood_glucose", val_input, ">250 mg/dL"
                    )
                    st.warning("⚠️ High Glucose Alert Logged.")
                else:
                    db.log_health_alert(
                        user_id, "Vitals Check", "Moderate",
                        f"Metric value recorded: {val_input}. Within warning zone.",
                        metric_choice.lower().replace(" ", "_"), val_input, "Normal"
                    )
                    st.info("Log recorded.")
                st.rerun()

        alerts = db.get_active_health_alerts(user_id)
        if alerts:
            st.markdown("#### 📜 Active Alert History")
            for a in alerts:
                severity_color = "#ef4444" if a['severity'] == "Emergency" else ("#f59e0b" if a['severity'] == "High" else "#38bdf8")
                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.7); border-left: 4px solid {severity_color}; border-radius:8px; padding:12px; margin-bottom:8px">
                    <span style="color:{severity_color}; font-weight:700">[{a['severity']}] {a['alert_type']}</span> — <span style="color:#94a3b8">{a['created_at']}</span><br>
                    <span style="color:#e2e8f0">{a['message']}</span>
                </div>
                """, unsafe_allow_html=True)
