"""
HealthGuard AI — Main Application Entry Point
Personal Health Monitoring Assistant with AI-powered insights.
"""

import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="HealthGuard AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://medlineplus.gov",
        "Report a bug": None,
        "About": "HealthGuard AI — Personal Health Monitoring Assistant\nBuilt with LangChain + Streamlit",
    },
)

# ── Imports (after path setup) ────────────────────────────────────────────────
from database import db_manager as db

# ── Initialize database ───────────────────────────────────────────────────────
db.init_db()

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Dark Background ── */
.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1929 50%, #0a1120 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1929 0%, #0a1120 100%) !important;
    border-right: 1px solid rgba(79,142,247,0.15) !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e2e8f0 !important;
}

/* ── Navigation radio buttons ── */
[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    padding: 8px 12px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
    display: block;
    font-size: 0.9rem;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(79,142,247,0.1);
    color: #e2e8f0 !important;
}

/* ── Main content area ── */
.main .block-container {
    padding: 1.5rem 2rem 2rem;
    max-width: 1400px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(30,41,59,0.5);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(79,142,247,0.1);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #94a3b8 !important;
    font-size: 0.9rem;
    padding: 8px 16px;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: rgba(79,142,247,0.2) !important;
    color: #4f8ef7 !important;
    font-weight: 600;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select {
    background: rgba(30,41,59,0.8) !important;
    border: 1px solid rgba(79,142,247,0.2) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(79,142,247,0.6) !important;
    box-shadow: 0 0 0 2px rgba(79,142,247,0.15) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #4f8ef7, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s !important;
    box-shadow: 0 4px 12px rgba(79,142,247,0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(79,142,247,0.35) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #22c55e, #14b8a6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

/* ── Forms ── */
[data-testid="stForm"] {
    background: rgba(30,41,59,0.4);
    border: 1px solid rgba(79,142,247,0.1);
    border-radius: 16px;
    padding: 20px;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: rgba(30,41,59,0.6);
    border: 1px solid rgba(79,142,247,0.15);
    border-radius: 12px;
    padding: 12px;
}
[data-testid="metric-container"] label {
    color: #94a3b8 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    background: rgba(30,41,59,0.6);
    border-radius: 12px;
    border: 1px solid rgba(79,142,247,0.1);
}

/* ── Info / Warning / Success / Error boxes ── */
.stInfo {
    background: rgba(79,142,247,0.1) !important;
    border: 1px solid rgba(79,142,247,0.3) !important;
    border-radius: 10px !important;
    color: #93c5fd !important;
}
.stSuccess {
    background: rgba(34,197,94,0.1) !important;
    border: 1px solid rgba(34,197,94,0.3) !important;
    border-radius: 10px !important;
    color: #86efac !important;
}
.stWarning {
    background: rgba(245,158,11,0.1) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 10px !important;
    color: #fcd34d !important;
}
.stError {
    background: rgba(239,68,68,0.1) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    border-radius: 10px !important;
    color: #fca5a5 !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: rgba(30,41,59,0.5) !important;
    border: 1px solid rgba(79,142,247,0.1) !important;
    border-radius: 14px !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: rgba(30,41,59,0.8) !important;
    border: 1px solid rgba(79,142,247,0.2) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    color: #e2e8f0 !important;
}

/* ── Sliders ── */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: #4f8ef7 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(30,41,59,0.4);
    border: 1px solid rgba(79,142,247,0.1);
    border-radius: 12px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(15,23,42,0.5); }
::-webkit-scrollbar-thumb { background: rgba(79,142,247,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(79,142,247,0.5); }

/* ── Hide Streamlit branding ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Session state initialization ──────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"


# ── User profile setup ────────────────────────────────────────────────────────
def setup_user():
    """Show user profile setup if no user is selected."""
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
         min-height:60vh;text-align:center;padding:40px">
        <div style="font-size:4rem;margin-bottom:16px">🏥</div>
        <h1 style="color:#e2e8f0;font-size:2.5rem;font-weight:800;margin:0 0 8px 0;
             background:linear-gradient(135deg,#4f8ef7,#a855f7);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent">
            HealthGuard AI
        </h1>
        <p style="color:#94a3b8;font-size:1.1rem;margin:0 0 40px 0;max-width:500px">
            Your personal AI-powered health monitoring assistant.
            Track medications, monitor vitals, and get reliable health information.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='color:#e2e8f0;text-align:center;margin-bottom:20px'>Get Started</h2>",
                    unsafe_allow_html=True)

        tab_new, tab_existing = st.tabs(["👤 New Profile", "🔄 Load Existing"])

        with tab_new:
            with st.form("create_profile"):
                name = st.text_input("Full Name *", placeholder="e.g. Ankit Sharma")
                col_a, col_b = st.columns(2)
                with col_a:
                    age = st.number_input("Age", min_value=1, max_value=120, value=25)
                    gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Other"])
                    blood_group = st.selectbox("Blood Group", ["Unknown", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                with col_b:
                    weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1)
                    height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.5)

                if st.form_submit_button("🚀 Create Profile & Start", use_container_width=True):
                    if not name.strip():
                        st.error("Please enter your name.")
                    else:
                        uid = db.create_user(
                            name=name.strip(),
                            age=age,
                            gender=gender if gender != "Prefer not to say" else None,
                            weight_kg=weight,
                            height_cm=height,
                            blood_group=blood_group if blood_group != "Unknown" else None,
                        )
                        st.session_state.user_id = uid
                        st.session_state.user_name = name.strip()
                        st.success(f"✅ Welcome, {name}! Your profile is ready.")
                        st.rerun()

        with tab_existing:
            users = db.get_all_users()
            if users:
                user_options = {f"{u['name']} (ID: {u['id']})": u["id"] for u in users}
                selected = st.selectbox("Select your profile:", list(user_options.keys()))
                if st.button("Load Profile", use_container_width=True):
                    uid = user_options[selected]
                    user = db.get_user(uid)
                    st.session_state.user_id = uid
                    st.session_state.user_name = user["name"]
                    st.rerun()
            else:
                st.info("No existing profiles found. Create a new one!")


# ── Sidebar navigation ─────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo & title
        st.markdown("""
        <div style="text-align:center;padding:20px 0 10px">
            <div style="font-size:2.5rem">🏥</div>
            <h2 style="color:#e2e8f0;font-size:1.3rem;font-weight:700;margin:6px 0 2px">
                HealthGuard AI
            </h2>
            <p style="color:#94a3b8;font-size:0.75rem;margin:0">Personal Health Assistant</p>
        </div>
        <hr style="border-color:rgba(79,142,247,0.15);margin:10px 0 16px">
        """, unsafe_allow_html=True)

        # User info
        if st.session_state.user_id:
            user = db.get_user(st.session_state.user_id)
            if user:
                adherence = db.get_adherence_rate(st.session_state.user_id, days=7)
                color = "#22c55e" if adherence >= 80 else "#f59e0b" if adherence >= 60 else "#ef4444"
                st.markdown(f"""
                <div style="background:rgba(30,41,59,0.6);border:1px solid rgba(79,142,247,0.15);
                     border-radius:12px;padding:14px;margin-bottom:16px">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                        <div style="background:linear-gradient(135deg,#4f8ef7,#a855f7);
                             width:36px;height:36px;border-radius:50%;display:flex;
                             align-items:center;justify-content:center;font-size:1.1rem">
                            👤
                        </div>
                        <div>
                            <div style="color:#e2e8f0;font-weight:600;font-size:0.9rem">{user['name']}</div>
                            <div style="color:#94a3b8;font-size:0.75rem">
                                {f"Age {user['age']}" if user.get('age') else ""} 
                                {f"• {user['blood_group']}" if user.get('blood_group') else ""}
                            </div>
                        </div>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <span style="color:#94a3b8;font-size:0.75rem">7-day adherence</span>
                        <span style="color:{color};font-weight:700;font-size:0.9rem">{adherence}%</span>
                    </div>
                    <div style="background:rgba(148,163,184,0.1);border-radius:99px;height:4px;margin-top:4px">
                        <div style="background:{color};width:{adherence}%;height:100%;border-radius:99px"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Navigation
        st.markdown("<p style='color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px'>Navigation</p>",
                    unsafe_allow_html=True)

        nav_items = {
            "📊 Dashboard": "dashboard",
            "💊 Medications": "medications",
            "🤖 AI Chatbot": "chatbot",
            "📝 Health Log": "health_log",
        }

        for label, page_key in nav_items.items():
            is_active = st.session_state.page == page_key
            btn_style = "background:rgba(79,142,247,0.15);border:1px solid rgba(79,142,247,0.3);" if is_active else ""
            st.markdown(f"""
            <div style="{btn_style}border-radius:10px;margin-bottom:4px;transition:all 0.2s">
            """, unsafe_allow_html=True)
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(79,142,247,0.1);margin:16px 0'>", unsafe_allow_html=True)

        # API Configuration
        with st.expander("⚙️ AI Settings"):
            provider = st.selectbox("LLM Provider", ["gemini", "openai"],
                                     index=0 if os.getenv("LLM_PROVIDER", "gemini") == "gemini" else 1)
            api_key = st.text_input("API Key", type="password",
                                     value=os.getenv("GOOGLE_API_KEY" if provider == "gemini" else "OPENAI_API_KEY", ""),
                                     placeholder="Enter your API key")
            if st.button("Save & Apply", use_container_width=True):
                os.environ["LLM_PROVIDER"] = provider
                if provider == "gemini":
                    os.environ["GOOGLE_API_KEY"] = api_key
                else:
                    os.environ["OPENAI_API_KEY"] = api_key
                # Reset agent so it re-initializes with new key
                if "health_agent" in st.session_state:
                    del st.session_state["health_agent"]
                if "agent_error" in st.session_state:
                    del st.session_state["agent_error"]
                st.success("✅ Settings saved!")

        # Switch user
        st.markdown("<hr style='border-color:rgba(79,142,247,0.1);margin:12px 0'>", unsafe_allow_html=True)
        if st.button("🔄 Switch User", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.page = "dashboard"
            if "chat_messages" in st.session_state:
                del st.session_state["chat_messages"]
            if "health_agent" in st.session_state:
                del st.session_state["health_agent"]
            st.rerun()

        # Health emergency
        st.markdown("""
        <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.15);
             border-radius:10px;padding:12px;margin-top:8px;text-align:center">
            <span style="color:#ef4444;font-size:0.8rem;font-weight:600">🚨 Emergency</span><br>
            <span style="color:#94a3b8;font-size:0.75rem">Call <strong style="color:#ef4444">112</strong> immediately</span>
        </div>
        """, unsafe_allow_html=True)


# ── Main router ────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.user_id:
        setup_user()
        return

    render_sidebar()

    page = st.session_state.get("page", "dashboard")

    if page == "dashboard":
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif page == "medications":
        from pages.medications import show_medications
        show_medications()
    elif page == "chatbot":
        from pages.chatbot import show_chatbot
        show_chatbot()
    elif page == "health_log":
        from pages.health_log import show_health_log
        show_health_log()
    else:
        from pages.dashboard import show_dashboard
        show_dashboard()


if __name__ == "__main__":
    main()
