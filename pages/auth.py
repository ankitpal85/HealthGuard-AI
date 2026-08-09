"""
Firebase Authentication & Security Page for HealthGuard AI
Provides Login, Signup, and Firebase Cloud API key configuration interface.
"""

import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db_manager as db
from utils.firebase_auth import firebase_sign_in, firebase_sign_up, get_firebase_api_key


def show_auth_page():
    st.markdown("""
    <style>
    /* Center container for auth page */
    .auth-container {
        max-width: 480px;
        margin: 40px auto;
        background: linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
        border: 1px solid rgba(79,142,247,0.3);
        border-radius: 20px;
        padding: 32px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    .auth-title {
        color: #4f8ef7;
        font-size: 1.8rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 6px;
    }
    .auth-subtitle {
        color: #94a3b8;
        font-size: 0.85rem;
        text-align: center;
        margin-bottom: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="font-size: 3rem;">🏥</div>
        <h1 style="color: #e2e8f0; font-size: 2.2rem; font-weight: 800; margin: 0;">HealthGuard AI</h1>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 4px;">
            Firebase Authenticated Personal Health Portal
        </p>
    </div>
    """, unsafe_allow_html=True)

    api_key = get_firebase_api_key()
    badge_color = "#22c55e" if api_key else "#f59e0b"
    badge_text = "🔥 Firebase Cloud Auth Active" if api_key else "🔒 Local Database Security Active (No Firebase Key)"

    st.markdown(f"""
    <div style="background: rgba(30,41,59,0.6); border: 1px solid {badge_color}; border-radius: 12px;
                padding: 10px 16px; margin-bottom: 20px; text-align: center;">
        <span style="color: {badge_color}; font-size: 0.85rem; font-weight: 600;">{badge_text}</span>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup, tab_config = st.tabs(["🔐 Sign In", "📝 Sign Up", "⚙️ Firebase Config"])

    # ── TAB 1: LOGIN ────────────────────────────────────────────────────────
    with tab_login:
        st.markdown("### 🔐 Account Login")
        with st.form("login_form"):
            login_email = st.text_input("Email Address*", placeholder="e.g. ankit@healthguard.ai")
            login_password = st.text_input("Password*", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("Remember session", value=True)

            btn_login = st.form_submit_button("🚀 Sign In", use_container_width=True)

            if btn_login:
                with st.spinner("Authenticating..."):
                    result = firebase_sign_in(login_email, login_password)
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user_id = result["user_id"]
                        st.session_state.user_name = result["name"]
                        st.session_state.user_email = result["email"]
                        st.session_state.auth_provider = result["provider"]
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])

    # ── TAB 2: SIGNUP ───────────────────────────────────────────────────────
    with tab_signup:
        st.markdown("### 📝 Create New Account")
        with st.form("signup_form"):
            su_name = st.text_input("Full Name*", placeholder="e.g. Ankit Sharma")
            su_email = st.text_input("Email Address*", placeholder="e.g. ankit@healthguard.ai")
            su_password = st.text_input("Password (min 6 chars)*", type="password")

            col_u1, col_u2 = st.columns(2)
            with col_u1:
                su_age = st.number_input("Age", min_value=1, max_value=120, value=35)
                su_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                su_bg = st.selectbox("Blood Group", ["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"])
            with col_u2:
                su_weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=75.0)
                su_height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=175.0)

            btn_signup = st.form_submit_button("✨ Create Account", use_container_width=True)

            if btn_signup:
                if su_email and su_password and su_name:
                    with st.spinner("Creating secure account..."):
                        result = firebase_sign_up(
                            email=su_email,
                            password=su_password,
                            name=su_name,
                            age=su_age,
                            gender=su_gender,
                            weight_kg=su_weight,
                            height_cm=su_height,
                            blood_group=su_bg
                        )
                        if result["success"]:
                            st.session_state.authenticated = True
                            st.session_state.user_id = result["user_id"]
                            st.session_state.user_name = result["name"]
                            st.session_state.user_email = result["email"]
                            st.session_state.auth_provider = result["provider"]
                            st.success(result["message"])
                            st.rerun()
                        else:
                            st.error(result["message"])
                else:
                    st.warning("Please fill in all required fields (Name, Email, Password).")

    # ── TAB 3: FIREBASE & SUPABASE CONFIG ──────────────────────────────────
    with tab_config:
        st.markdown("### ⚙️ Cloud Database & Auth Configuration")

        st.markdown("#### 🔥 Firebase Authentication Setup")
        fb_key_input = st.text_input(
            "Firebase Web API Key",
            type="password",
            value=get_firebase_api_key(),
            placeholder="AIzaSy..."
        )

        if st.button("Save Firebase API Key"):
            clean_key = fb_key_input.strip()
            os.environ["FIREBASE_WEB_API_KEY"] = clean_key

            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
            env_lines = []
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    env_lines = f.readlines()

            new_lines = [l for l in env_lines if not l.startswith("FIREBASE_WEB_API_KEY=")]
            new_lines.append(f"FIREBASE_WEB_API_KEY={clean_key}\n")

            with open(env_path, "w") as f:
                f.writelines(new_lines)

            st.success("✅ Firebase Web API Key saved!")
            st.rerun()

        st.markdown("---")
        st.markdown("#### ⚡ Supabase PostgreSQL Database Setup")
        st.markdown("To connect your **[Supabase Console](https://supabase.com)** PostgreSQL database:")

        supa_url_input = st.text_input(
            "Supabase Project URL",
            value=os.getenv("SUPABASE_URL", ""),
            placeholder="https://xyzcompany.supabase.co"
        )
        supa_key_input = st.text_input(
            "Supabase Anon / API Key",
            type="password",
            value=os.getenv("SUPABASE_KEY", ""),
            placeholder="eyJhbGciOiJIUzI1Ni..."
        )

        if st.button("Save Supabase Database Credentials"):
            url_clean = supa_url_input.strip()
            key_clean = supa_key_input.strip()

            os.environ["SUPABASE_URL"] = url_clean
            os.environ["SUPABASE_KEY"] = key_clean

            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
            env_lines = []
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    env_lines = f.readlines()

            new_lines = [l for l in env_lines if not (l.startswith("SUPABASE_URL=") or l.startswith("SUPABASE_KEY="))]
            new_lines.append(f"SUPABASE_URL={url_clean}\n")
            new_lines.append(f"SUPABASE_KEY={key_clean}\n")

            with open(env_path, "w") as f:
                f.writelines(new_lines)

            st.success("✅ Supabase credentials saved to environment!")
            st.rerun()

        with st.expander("📜 View Supabase PostgreSQL DDL SQL Query"):
            from database.supabase_manager import get_supabase_schema_sql
            st.code(get_supabase_schema_sql(), language="sql")

