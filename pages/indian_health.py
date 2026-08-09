"""
Indian Personal Health Assistant Page for HealthGuard AI
Provides 1mg medicine search, Practo doctor appointment booking,
Ayurvedic medicine & Dosha recommendations, ABHA insurance locker, and AQI respiratory checks.
"""

import streamlit as st
import os
import sys
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db
from tools.indian_health_tool import (
    search_indian_medication_tool,
    search_ayurvedic_herbs_tool,
    search_practo_doctors_tool,
    check_air_quality_tool,
)


def show_indian_health():
    user_id = st.session_state.get("user_id", 1)
    user = db.get_user(user_id) or {"name": "User", "id": 1}

    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(249,115,22,0.15), rgba(79,142,247,0.15));
                border: 1px solid rgba(249,115,22,0.3); border-radius: 16px; padding: 20px; margin-bottom: 24px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="font-size: 2.2rem;">🇮🇳</div>
            <div>
                <h2 style="margin:0; color:#f97316; font-size:1.5rem;">Indian Personal Health Assistant</h2>
                <p style="margin:4px 0 0; color:#94a3b8; font-size:0.9rem;">
                    1mg Medicine Lookup • Practo Doctor Bookings • Ayurvedic Dosha Guidance • ABHA & Insurance Locker
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💊 1mg Medicine Search",
        "🩺 Practo Doctors",
        "🌿 Ayurveda & Doshas",
        "🛡️ ABHA & Insurance",
        "🌫️ AQI & Emergency"
    ])

    # ── TAB 1: 1mg Medicine Search ──────────────────────────────────────────
    with tab1:
        st.markdown("### 💊 1mg Medicine & Generic Price Comparison")
        st.markdown("Search for Indian pharmaceutical brand names, active generic components, prices in **INR (₹)**, and generic substitutes.")

        col_search, col_btn = st.columns([4, 1])
        with col_search:
            search_q = st.text_input("Search Medicine Name or Condition", value="Dolo", placeholder="e.g. Dolo 650, Pan 40, Metformin, Fever")
        with col_btn:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            search_click = st.button("🔍 Search 1mg", use_container_width=True)

        meds = db.search_indian_medications(search_q)

        if meds:
            for m in meds:
                with st.expander(f"💊 **{m['brand_name']}** — {m['strength']} ({m['form']}) | ₹{m['price_inr']:.2f}"):
                    st.markdown(f"**Generic Composition:** `{m['generic_name']}`")
                    st.markdown(f"**Manufacturer:** {m['manufacturer']}")
                    st.markdown(f"**Primary Uses:** {m['usage_purpose']}")
                    st.markdown(f"**Generic Substitutes:** {m['substitutes']}")
                    st.markdown(f"**Potential Side Effects:** {m['side_effects']}")
        else:
            st.info("No matching medicines found in offline 1mg catalog. Showing generic recommendations.")

        st.markdown("---")
        st.markdown("#### ➕ Add Custom Medicine to Indian Database")
        with st.form("add_ind_med"):
            c1, c2 = st.columns(2)
            with c1:
                b_name = st.text_input("Brand Name*", placeholder="e.g. Calpol 650")
                g_name = st.text_input("Generic Composition*", placeholder="e.g. Paracetamol")
                mfr = st.text_input("Manufacturer", placeholder="e.g. GSK India")
                price = st.number_input("Price in ₹*", min_value=1.0, value=35.0)
            with c2:
                form_type = st.selectbox("Form", ["Tablet", "Syrup", "Capsule", "Injection", "Ointment"])
                strength = st.text_input("Strength", value="650mg")
                uses = st.text_input("Usage Purpose", placeholder="Fever and pain relief")
                subst = st.text_input("Substitutes", placeholder="Dolo 650, Pacimol")

            if st.form_submit_button("Save to Indian Database"):
                if b_name and g_name:
                    db.add_indian_medication(b_name, g_name, mfr, price, form_type, strength, uses, "", subst)
                    st.success(f"✅ Added {b_name} to 1mg Indian Database!")
                    st.rerun()

    # ── TAB 2: Practo Doctor Directory ──────────────────────────────────────
    with tab2:
        st.markdown("### 🩺 Practo Doctor Appointments Directory")
        st.markdown("Find verified doctors across Indian cities and schedule simulated appointments.")

        c_city, c_spec = st.columns(2)
        with c_city:
            city_choice = st.selectbox("Select City", ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Pune"])
        with c_spec:
            spec_choice = st.selectbox("Specialty", ["Cardiologist", "General Physician", "Dermatologist", "Diabetologist", "Orthopedic"])

        doc_info = search_practo_doctors_tool.invoke({"specialty": spec_choice, "city": city_choice})
        st.markdown(doc_info)

        st.markdown("---")
        st.markdown("#### 📅 Schedule Doctor Appointment")
        with st.form("book_doctor"):
            d1, d2 = st.columns(2)
            with d1:
                doc_name = st.text_input("Doctor Name*", value=f"Dr. Rajesh Sharma ({spec_choice})")
                clinic = st.text_input("Clinic / Hospital*", value=f"Fortis Care, {city_choice}")
                app_date = st.date_input("Appointment Date", value=date.today())
            with d2:
                app_time = st.time_input("Appointment Time")
                fee = st.number_input("Consultation Fee (₹)", value=750.0)
                notes = st.text_input("Reason for Visit", placeholder="Routine heart checkup and blood pressure review")

            if st.form_submit_button("Confirm Appointment Booking"):
                db.create_doctor_appointment(
                    user_id, doc_name, spec_choice, clinic, city_choice,
                    str(app_date), str(app_time), fee, notes
                )
                st.success(f"✅ Appointment booked with {doc_name} on {app_date} at {app_time}!")

        # Show existing appointments
        user_apps = db.get_doctor_appointments(user_id)
        if user_apps:
            st.markdown("#### 📋 Scheduled Appointments")
            for ap in user_apps:
                st.info(f"🩺 **{ap['doctor_name']}** ({ap['specialty']}) | 📅 {ap['appointment_date']} at {ap['appointment_time']} | 📍 {ap['clinic_hospital']} | Fee: ₹{ap['fee_inr']}")

    # ── TAB 3: Ayurveda & Dosha Assessment ──────────────────────────────────
    with tab3:
        st.markdown("### 🌿 Ayurvedic Medicine & Dosha Assessment")
        st.markdown("Explore ancient Indian wellness, Ayurvedic herbs, and determine your Ayurvedic **Prakriti (Dosha)**.")

        herbs = db.search_ayurvedic_herbs("")
        st.markdown("#### 📜 Traditional Herbal Library")
        for h in herbs:
            with st.expander(f"🌿 **{h['name']}** ({h['sanskrit_name']}) — *{h['dosha_balancing']}*"):
                st.markdown(f"**Primary Benefit:** {h['primary_benefit']}")
                st.markdown(f"**Recommended Dosage:** {h['recommended_dosage']}")
                st.markdown(f"**Formulation:** {h['formulation']}")
                st.markdown(f"**Precautions:** {h['precautions']}")

        st.markdown("---")
        st.markdown("#### ☯️ Quick Dosha Assessment Quiz")
        q1 = st.radio("1. How would you describe your body frame?", ["Slim / Lean (Vata)", "Medium / Athletic (Pitta)", "Broad / Sturdy (Kapha)"])
        q2 = st.radio("2. How does weather affect you most?", ["Dislike cold & wind (Vata)", "Dislike heat & sun (Pitta)", "Dislike damp & humidity (Kapha)"])

        if st.button("Calculate My Dosha Profile"):
            if "Vata" in q1 or "Vata" in q2:
                st.success("☯️ **Dominant Dosha: Vata (Air & Ether)** — Recommended: Warm foods, Ashwagandha, Sesame oil massage, regular sleep schedule.")
            elif "Pitta" in q1 or "Pitta" in q2:
                st.warning("☯️ **Dominant Dosha: Pitta (Fire & Water)** — Recommended: Cooling herbs, Shatavari, Brahmi, coconut water, avoiding spicy foods.")
            else:
                st.info("☯️ **Dominant Dosha: Kapha (Earth & Water)** — Recommended: Light foods, Triphala, Tulsi tea, active daily exercise.")

    # ── TAB 4: ABHA & Insurance Locker ──────────────────────────────────────
    with tab4:
        st.markdown("### 🛡️ ABHA Health ID & Insurance Locker")
        st.markdown("Store your Ayushman Bharat Digital Health Account (ABHA ID) and track health insurance coverage.")

        with st.form("add_insurance"):
            st.markdown("#### ➕ Link Insurance Policy or ABHA ID")
            col_i1, col_i2 = st.columns(2)
            with col_i1:
                provider = st.selectbox("Insurance Provider", ["Ayushman Bharat (PM-JAY)", "Star Health Insurance", "ICICI Lombard", "HDFC ERGO", "Care Health Insurance"])
                pol_no = st.text_input("Policy Number*", placeholder="POL-108294712")
                abha = st.text_input("ABHA ID (Ayushman Bharat)", placeholder="14-digit ABHA number, e.g., 91-8274-1029-4412")
            with col_i2:
                cov_amt = st.number_input("Coverage Sum Insured (₹)", value=500000.0)
                exp_d = st.date_input("Policy Expiry Date", value=date(2027, 12, 31))
                hospitals = st.text_input("Network Hospitals", value="Apollo, Fortis, Max Healthcare, Manipal")

            if st.form_submit_button("Save Policy to Locker"):
                db.add_insurance_policy(user_id, provider, pol_no, abha, cov_amt, str(exp_d), hospitals)
                st.success("✅ Policy successfully saved to Digital Health Locker!")
                st.rerun()

        existing_pols = db.get_insurance_policies(user_id)
        if existing_pols:
            st.markdown("#### 📁 Your Saved Health Policies")
            for p in existing_pols:
                st.success(f"🛡️ **{p['provider_name']}** | Policy: `{p['policy_number']}` | ABHA ID: `{p['abha_id']}` | Coverage: ₹{p['coverage_amount']:,.0f} | Expires: {p['expiry_date']}")

    # ── TAB 5: AQI & Regional Emergency Network ─────────────────────────────
    with tab5:
        st.markdown("### 🌫️ Air Quality (AQI) & Regional Emergency Network")

        city_aqi = st.selectbox("Select City for AQI Check", ["Delhi", "Mumbai", "Bengaluru", "Hyderabad", "Chennai", "Kolkata"])
        aqi_report = check_air_quality_tool.invoke({"city": city_aqi})
        st.markdown(aqi_report)

        st.markdown("---")
        st.markdown("#### 🚨 Indian Emergency Helpline Numbers")
        st.error("""
        • **National Emergency Helpline:** 112  
        • **Ambulance Emergency:** 102 / 108  
        • **Women Emergency Helpline:** 1091  
        • **Senior Citizen Helpline:** 14567  
        """)
