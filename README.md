# 🏥 HealthGuard AI — Multi-Functional Personal Health Assistant

> **Production-Ready AI Healthcare Agent** — Powered by LangGraph stateful workflow, 21 healthcare tools, Indian healthcare integrations (1mg, Practo, Ayurveda), Family & Caregiver network, ML risk analytics, and Vision & Voice AI.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-purple.svg)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🛠️ Technology Stack Breakdown

| Component Layer | **Track A Stack (Implemented Streamlit App)** | **Track B Stack (Enterprise Microservices)** |
|---|---|---|
| **Frontend UI** | Streamlit + Custom Glassmorphic CSS + Web Speech API | React / Next.js + Tailwind CSS + Chart.js |
| **Backend Engine** | Python 3.10+ + LangChain + LangGraph StateGraph | FastAPI + LangGraph + Celery Async Processing |
| **Analytics & ML** | pandas + numpy + scikit-learn + Plotly | pandas + scikit-learn + Custom ML Pipeline |
| **Database & Cache** | SQLite Engine + **Supabase PostgreSQL** + AES-256 Data Encryption | PostgreSQL (Relational Data) + Redis (Caching & Sessions) |
| **LLM Backbone** | Google Gemini 2.5 Flash / GPT-3.5-turbo / MedAlpaca | GPT-4o / Claude 3.5 Sonnet / Gemini 2.5 Pro |
| **Healthcare APIs** | 1mg, Practo, PubMed NCBI, OpenWeather AQI | Google Fit API, Nutrition APIs, 1mg, Practo |
| **Auth & Security** | Multi-Profile Isolation + HIPAA Safe Harbor | Auth0 / Firebase Auth with Healthcare RBAC |
| **Deployment** | Streamlit Cloud / Docker | Vercel (Frontend) + Railway / Render (Backend) |
| **Alert Monitoring** | Real-Time Vital Threshold Monitor + Caregiver Network | Custom Analytics Dashboard + Webhooks |

---

## ✨ Comprehensive Feature Matrix

| Category | Feature | Description |
|---|---|---|
| 🇮🇳 **Indian Health** | 💊 **1mg Medicine Lookup** | Search Indian pharmaceuticals, compare prices in INR (₹), and find generic substitutes. |
| | 🩺 **Practo Doctor Directory** | Search verified specialists across Indian cities and schedule appointments. |
| | 🌿 **Ayurveda & Dosha Engine** | Herb lookup (Ashwagandha, Tulsi, Triphala) with Vata, Pitta, Kapha Dosha assessment. |
| | 🛡️ **ABHA & Insurance Locker** | Store Ayushman Bharat ID and manage policies (Star Health, ICICI, HDFC ERGO). |
| | 🌫️ **AQI & Emergency Helpline** | City air quality respiratory alerts & national emergency numbers (112, 102, 108). |
| 👨‍👩‍👧 **Family & Caregivers**| 👤 **Multi-Profile Management**| Track separate health profiles for Self, Parents, Spouse, and Children. |
| | 🔔 **Caregiver Alert System** | Configure phone/email contacts for simulated SMS/Email notifications on critical vitals. |
| | 🚨 **Real-Time Vitals Alerts** | Automatically flags critical vitals (e.g. BP > 180 mmHg) with emergency alert logs. |
| 👁️🎙️ **Vision & Voice AI** | 🖼️ **Vision AI OCR** | Parse prescription images, lab reports, skin condition rash photos, and food photos. |
| | 🎙️ **Speech-to-Text Voice Query**| Web Speech API browser integration for hands-free spoken health queries. |
| 📊 **Analytics & ML** | 🫀 **Predictive Disease Risk** | 10-year Framingham Cardiovascular Disease (CVD) risk, Type 2 Diabetes & Hypertension risk. |
| | 🔮 **Trend & Anomaly ML** | Z-score anomaly detection and linear regression vital trend forecasting. |
| | 📄 **Automated Clinical Reports**| 1-Click downloadable HTML and Markdown health summary reports. |
| 💊 **Medications & Vitals**| 💊 **Medication Adherence** | 7-day adherence rate breakdown, missed/taken logging, and drug-drug interaction checker. |
| | 📝 **Health Data Import/Export**| Multi-format import and export (JSON, CSV, XML, HTML, Markdown). |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- pip package manager

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd "Healthcare Monitoring AI Agent"
```

### 2. Activate Virtual Environment
```powershell
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini
```
*(No API key? The system seamlessly falls back to the built-in Smart Generative Healthcare Engine so all features work completely offline!)*

### 5. Launch the Application
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 📂 Project Structure

```
Healthcare Monitoring AI Agent/
├── app.py                    # Main Streamlit application & navigation router
├── requirements.txt          # Dependencies (Streamlit, LangChain, LangGraph, Plotly)
├── README.md                 # Project README
├── TECHNICAL_DOCUMENTATION.md # Architecture, Microservices & HIPAA Security Specs
├── .env.example              # Environment variables template
├── database/
│   └── db_manager.py         # SQLite CRUD & seeding for 13 healthcare tables
├── agents/
│   └── health_agent.py       # LangGraph stateful agent with emergency triage node & 21 tools
├── tools/
│   ├── clinical_tools.py     # Drug interactions, symptom triage & automated report tools
│   ├── indian_health_tool.py # 1mg search, Practo doctor lookup, Ayurveda & AQI tools
│   ├── medical_info_tool.py  # MedlinePlus lookup tool
│   ├── medical_research_tool.py # PubMed literature search & summarization tool
│   ├── medication_tool.py    # Medication scheduling & adherence tracking tools
│   ├── health_data_tool.py   # Fitness & vital metric logging tools
│   └── vision_voice_tool.py  # Prescription OCR, skin rash diagnostic & voice query tools
├── utils/
│   ├── analytics.py          # Predictive ML risk models (Framingham CVD, Diabetes, Anomaly)
│   ├── data_parser.py        # Multi-format import/export (JSON, CSV, XML)
│   ├── report_generator.py   # Automated HTML and Markdown report generator
│   ├── security.py          # Data encryption, input validation & HIPAA anonymization
│   └── visualizations.py    # Plotly interactive healthcare charts
└── pages/
    ├── dashboard.py          # Real-time metrics overview & quick logging
    ├── medications.py        # Medication schedule & adherence reports
    ├── nutrition.py          # Indian & global meal logger & macro breakdown
    ├── health_log.py         # Vital metrics logger & data importer/exporter
    ├── analytics.py          # ML risk models, trend forecasting & report exports
    ├── indian_health.py      # 1mg lookup, Practo, Ayurveda & ABHA locker
    ├── family_caregiver.py   # Family profiles, caregiver contacts & real-time alert logs
    ├── vision_voice.py       # Vision AI image analyzer & speech-to-text assistant
    └── chatbot.py            # AI Chatbot connected to 21 healthcare tools
```

---

## 🧪 Testing & Verification

Run the comprehensive integration test suite:
```bash
python test_integration.py
```

---

## 🔒 Healthcare Security & HIPAA Compliance
HealthGuard AI implements data encryption at rest for clinical notes, input validation bounds on physiological vitals, and HIPAA Safe Harbor 18-element de-identification on exported patient analytics. See `TECHNICAL_DOCUMENTATION.md` for complete technical architecture details.
