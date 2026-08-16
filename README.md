<p align="center">
  <img src="https://img.shields.io/badge/HealthGuard-AI-00C9A7?style=for-the-badge&logo=heartbeat&logoColor=white" alt="HealthGuard AI" height="40"/>
</p>

<h1 align="center">🏥 HealthGuard AI</h1>
<h3 align="center">Your Intelligent Personal Health Assistant — Powered by AI</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/TypeScript-6.0-3178C6?style=flat-square&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/TailwindCSS-4.3-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-0.2+-1C3C3C?style=flat-square&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini%20AI-Google-4285F4?style=flat-square&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

<p align="center">
  <b>AI-powered health monitoring • Smart medication tracking • Clinical analytics<br/>Indian healthcare integration • Vision & Voice AI • Family care management</b>
</p>

---

## 🌟 What is HealthGuard AI?

**HealthGuard AI** is a comprehensive, AI-powered personal health assistant that combines the intelligence of Large Language Models (Google Gemini / OpenAI GPT) with a modern React dashboard and FastAPI backend. It helps you **track vitals, manage medications, analyze symptoms, log nutrition, and get personalized health insights** — all in one place.

Built with a **LangGraph stateful agent pipeline**, HealthGuard AI doesn't just answer health questions — it reasons, triages emergencies, checks drug interactions, runs risk assessments, and even searches Indian pharmaceutical databases.

> ⚠️ **Disclaimer**: HealthGuard AI is a health *informational* tool. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers.

---

## ✨ Key Features

### 🤖 AI Health Chatbot
- Conversational AI powered by **Google Gemini 2.5 Flash** or **OpenAI GPT**
- Real-time **SSE streaming** responses for zero-latency UX
- Emergency triage detection with automatic escalation
- Context-aware multi-turn conversations with chat history

### 💊 Medication Management
- Add, track, and manage daily medications with dosage & schedules
- **Drug-drug interaction checker** (flags severe/moderate/contraindicated combinations)
- Medication adherence tracking with 7/30-day reports
- Missed dose alerts and reminders

### 📊 Health Vitals Dashboard
- Log and visualize **blood pressure, heart rate, blood sugar, SpO₂, temperature, weight**
- Interactive charts with **Recharts** data visualization
- 7-day trend analysis with smart health summaries
- Real-time vital threshold monitoring with alerts

### 🍽️ Nutrition & Diet Tracker
- Log meals with calorie, protein, carbs, and fat breakdowns
- Daily macro summary with nutritional insights
- AI-powered diet recommendations

### 🔬 Clinical Analytics
- **Symptom Analysis**: AI-powered symptom triaging with urgency scoring
- **Risk Assessment**: Cardiovascular, diabetes, and other condition risk calculators
- **Automated Health Reports**: Generate comprehensive patient health reports
- **PubMed Research**: Search medical literature via NCBI API

### 🇮🇳 India-Specific Health Features
- **1mg Medicine Search**: Find Indian brand-name & generic medicines with ₹ prices
- **Ayurvedic & AYUSH**: Search traditional herbs, remedies, and Dosha balancing
- **Practo Doctor Search**: Find doctors by specialty and city
- **Air Quality Index (AQI)**: Check city-wise AQI for respiratory risk assessment

### 👁️ Vision & Voice AI
- **Medical Image Analysis**: Upload and analyze medical images with AI
- **Voice Query Processing**: Natural language voice-to-text health queries

### 👨‍👩‍👧‍👦 Family & Caregiver Management
- Add family members with medical profiles
- Caregiver contact management with alert preferences
- Critical health and missed medication notifications

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    React 19 + TailwindCSS 4                     │
│              (Vite + TypeScript Frontend — :5173)               │
└────────────────────────────┬────────────────────────────────────┘
                             │  REST API + SSE Streaming
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Server (:8000)                │
│              ┌─────────────────────────────────┐                │
│              │  LangGraph Stateful Agent        │                │
│              │  (Emergency Triage → Tool Router)│                │
│              └──────┬──────────┬──────────┬─────┘                │
│                     │          │          │                       │
│  ┌──────────────────┤    ┌─────┴──────┐   ├──────────────────┐   │
│  │ Clinical Tools   │    │ Health DB  │   │ Indian Health    │   │
│  │ • Symptom Triage │    │ (SQLite)   │   │ • 1mg Meds API  │   │
│  │ • Drug Interact. │    │ • Users    │   │ • Practo Search │   │
│  │ • Risk Assess.   │    │ • Vitals   │   │ • Ayurveda/AYUSH│   │
│  │ • Auto Reports   │    │ • Meds     │   │ • AQI Monitor   │   │
│  └──────────────────┘    │ • Nutrition│   └──────────────────┘   │
│                          │ • Chat     │                          │
│  ┌──────────────────┐    │ • Family   │   ┌──────────────────┐   │
│  │ Vision & Voice   │    └────────────┘   │ Medical Research │   │
│  │ • Image Analysis │                     │ • PubMed/NCBI    │   │
│  │ • Voice Queries  │                     │ • Med Info       │   │
│  └──────────────────┘                     └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │  LLM Providers           │
              │  • Google Gemini 2.5     │
              │  • OpenAI GPT-3.5/4     │
              │  (Auto-Fallback)         │
              └──────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, TypeScript 6, Vite 8, TailwindCSS 4, Recharts, Lucide Icons |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Pydantic v2 |
| **AI/ML Engine** | LangChain, LangGraph (Stateful Agent Pipeline), Google Gemini, OpenAI GPT |
| **Database** | SQLite (local), Supabase PostgreSQL (cloud-ready) |
| **Healthcare APIs** | 1mg (Medicine), Practo (Doctors), PubMed/NCBI (Research), OpenWeather (AQI) |
| **HTTP Client** | Axios (frontend), Requests (backend) |
| **Dev Tools** | OxLint, PostCSS, Autoprefixer |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.10+ ([Download](https://www.python.org/downloads/))
- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Google Gemini API Key** (free tier available) — [Get Key](https://aistudio.google.com/app/apikey)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/ankitpal85/HealthGuard-AI.git
cd HealthGuard-AI
```

### 2️⃣ Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
# Choose your LLM provider
LLM_PROVIDER=gemini          # "gemini" or "openai"

# Google Gemini (recommended — free tier available)
GOOGLE_API_KEY=your_google_api_key_here

# OpenAI (alternative)
OPENAI_API_KEY=your_openai_api_key_here

# App Config
APP_SECRET_KEY=your_random_secret_key
DB_PATH=health_data.db
```

### 3️⃣ Install Backend Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4️⃣ Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 5️⃣ Start the Application

**Option A — One-Click (Windows):**
```bash
start.bat
```

**Option B — Manual Start:**

```bash
# Terminal 1: Start Backend (port 8000)
python -m uvicorn backend.main:app --port 8000 --reload

# Terminal 2: Start Frontend (port 5173)
cd frontend
npm run dev
```

### 6️⃣ Open the App

| Service | URL |
|---|---|
| 🖥️ **React Dashboard** | [http://localhost:5173](http://localhost:5173) |
| 📡 **FastAPI Backend** | [http://localhost:8000](http://localhost:8000) |
| 📄 **API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| 📘 **API Docs (ReDoc)** | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

---

## 📁 Project Structure

```
HealthGuard-AI/
├── 🖥️ frontend/                  # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── Header.tsx        # Top navigation bar with user selector
│   │   │   ├── Sidebar.tsx       # Side navigation menu
│   │   │   ├── Dashboard.tsx     # Dashboard widget component
│   │   │   └── Chatbot.tsx       # Chat message component
│   │   ├── pages/                # Page-level views
│   │   │   ├── Dashboard.tsx     # Health overview & vitals summary
│   │   │   ├── Chatbot.tsx       # AI health chatbot with SSE streaming
│   │   │   ├── Medications.tsx   # Medication management & tracking
│   │   │   ├── HealthLog.tsx     # Vital signs logging & charts
│   │   │   ├── Nutrition.tsx     # Meal & nutrition tracking
│   │   │   ├── Analytics.tsx     # Clinical analytics & risk reports
│   │   │   ├── IndianHealth.tsx  # India-specific health features
│   │   │   ├── FamilyCaregiver.tsx # Family & caregiver management
│   │   │   └── VisionVoice.tsx   # Vision & voice AI features
│   │   ├── services/
│   │   │   └── api.ts            # Axios API service layer
│   │   ├── App.tsx               # Root application component
│   │   ├── main.tsx              # React entry point
│   │   └── index.css             # Global styles & design tokens
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── ⚙️ backend/
│   └── main.py                   # FastAPI server — all REST & SSE endpoints
│
├── 🤖 agents/
│   └── health_agent.py           # LangGraph stateful AI agent pipeline
│
├── 🔧 tools/                     # LangChain tool functions
│   ├── clinical_tools.py         # Drug interactions, symptom analysis, risk assessment
│   ├── health_data_tool.py       # Vitals logging & health summary
│   ├── medication_tool.py        # Medication CRUD & adherence tracking
│   ├── indian_health_tool.py     # 1mg, Ayurveda, Practo, AQI tools
│   ├── medical_info_tool.py      # Medical information lookup
│   ├── medical_research_tool.py  # PubMed research search
│   └── vision_voice_tool.py      # Image analysis & voice processing
│
├── 🗄️ database/
│   └── db_manager.py             # SQLite database manager (800+ lines)
│
├── 📊 utils/
│   └── analytics.py              # Health analytics & ML risk models
│
├── 🧪 tests/                     # Test suite
│   ├── test_app.py
│   ├── test_integration.py
│   ├── test_supabase.py
│   └── test_week3_4.py
│
├── .env.example                  # Environment variable template
├── .gitignore
├── requirements.txt              # Python dependencies
├── start.bat                     # One-click launcher (Windows)
├── TECHNICAL_DOCUMENTATION.md    # Detailed technical architecture docs
└── README.md                     # ← You are here
```

---

## 🔌 API Reference

HealthGuard AI exposes a comprehensive REST API. Full interactive docs are available at `/docs` (Swagger UI) when the server is running.

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/users` | List all users |
| `POST` | `/api/users` | Create a new user |
| `GET` | `/api/users/{user_id}` | Get user profile |

### Dashboard & Vitals

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/summary` | Dashboard summary (vitals, adherence, alerts) |
| `GET` | `/api/vitals` | Get vital sign logs |
| `POST` | `/api/vitals` | Log a new vital sign reading |

### Medications

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/medications` | List medications |
| `POST` | `/api/medications` | Add a new medication |
| `POST` | `/api/medications/log` | Log medication intake |
| `GET` | `/api/medications/adherence` | Get adherence rate |

### AI Chat

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Send message to AI (standard response) |
| `POST` | `/api/chat/stream` | Send message to AI (SSE streaming) |
| `GET` | `/api/chat/history` | Get chat history |
| `DELETE` | `/api/chat/history` | Clear chat history |

### Nutrition

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/nutrition` | Get nutrition logs & macro summary |
| `POST` | `/api/nutrition` | Log a meal |

### Clinical & Analytics

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/symptoms/analyze` | AI symptom analysis |
| `POST` | `/api/risk-assessment` | Run health risk assessment |
| `GET` | `/api/reports/generate` | Generate automated health report |

### Indian Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/indian-health/medications` | Search Indian medicines (1mg) |
| `GET` | `/api/indian-health/ayurveda` | Search Ayurvedic herbs |
| `GET` | `/api/indian-health/doctors` | Search doctors (Practo) |
| `GET` | `/api/indian-health/aqi` | Check Air Quality Index |

### Vision & Voice

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/vision/analyze` | Analyze medical image |
| `POST` | `/api/voice/process` | Process voice query |

### Family & Caregivers

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/family` | List family members |
| `POST` | `/api/family` | Add family member |
| `GET` | `/api/caregivers` | List caregivers |
| `POST` | `/api/caregivers` | Add caregiver |

---

## 🧠 AI Agent Pipeline

HealthGuard AI uses a **LangGraph stateful agent** pipeline that goes beyond simple Q&A:

```
User Query
    │
    ▼
┌───────────────────────┐
│  Emergency Triage     │  ← Detects chest pain, stroke, poisoning, etc.
│  (Priority Router)    │    Immediate emergency response if detected
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  LLM Reasoning        │  ← Multi-provider: Gemini ↔ OpenAI auto-fallback
│  + Tool Selection      │    Selects appropriate healthcare tools
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  Tool Execution       │  ← 15+ specialized healthcare tools
│  (LangChain Tools)    │    Drug checks, vitals, nutrition, research...
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  Response Generation  │  ← Context-aware, medically informed response
│  + Chat History Save  │    Saved to database for continuity
└───────────────────────┘
```

### Available AI Tools (15+)

| Tool | Purpose |
|---|---|
| `medical_info_lookup` | Look up medical conditions & terminology |
| `add_medication_reminder` | Add medication with schedule |
| `get_todays_medications` | Retrieve today's medication list |
| `mark_medication_taken` | Mark a medication as taken |
| `get_medication_adherence_report` | Generate adherence analytics |
| `check_medication_interactions` | Check drug-drug interactions |
| `analyze_symptoms` | AI-powered symptom triaging |
| `log_health_metric` | Log vital signs |
| `get_health_summary` | Get health data summary |
| `calculate_bmi` | Calculate BMI with interpretation |
| `log_nutrition_log` | Log meal nutrition data |
| `run_risk_assessment_tool` | Run clinical risk assessment |
| `generate_automated_report` | Auto-generate patient reports |
| `search_indian_medication_tool` | Search Indian medicines |
| `search_ayurvedic_herbs_tool` | Search Ayurvedic remedies |
| `search_practo_doctors_tool` | Find doctors by specialty/city |
| `check_air_quality_tool` | Check city AQI levels |
| `search_pubmed_research` | Search PubMed medical literature |
| `analyze_medical_image_tool` | Analyze medical images with AI |
| `process_voice_query_tool` | Process voice-to-text health queries |

---

## 🧪 Running Tests

```bash
# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_app.py -v
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'feat: add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

| Type | Purpose |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `refactor:` | Code refactoring |
| `test:` | Adding/updating tests |
| `chore:` | Maintenance tasks |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Ankit Pal**

- GitHub: [@ankitpal85](https://github.com/ankitpal85)

---

<p align="center">
  <b>Built with ❤️ for better health outcomes</b><br/>
  <sub>If you find HealthGuard AI useful, consider giving it a ⭐ on GitHub!</sub>
</p>
