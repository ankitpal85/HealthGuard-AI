# 🏥 HealthGuard AI — Personal Health Monitoring Assistant

> **Track A | Week 1-2 Milestone** — AI-powered personal health assistant with medication tracking, fitness monitoring, and medical information lookup.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💊 **Medication Tracker** | Add medications, set reminders, mark doses as taken/missed |
| 📊 **Health Dashboard** | Real-time metrics overview with interactive Plotly charts |
| 🤖 **AI Health Chatbot** | LangChain-powered agent with medical information lookup |
| 📝 **Health Log** | Log steps, heart rate, blood pressure, glucose, sleep, and more |
| 🔍 **MedlinePlus Lookup** | Reliable medical info from the US National Library of Medicine |
| 📈 **Adherence Reports** | Visual medication adherence tracking with export capability |
| ⚖️ **BMI Calculator** | Calculate and track BMI over time |
| 📤 **Data Import/Export** | JSON, CSV, XML health data support |
| 🎯 **Health Goals** | Set and track wellness targets |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd "Healthcare Monitoring AI Agent"
```

### 2. Create a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
```bash
# Copy the template
cp .env.example .env

# Edit .env and add your API key
```

**Option A — Google Gemini (Recommended, Free Tier Available)**
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Set `GOOGLE_API_KEY=your_key` in `.env`
3. Set `LLM_PROVIDER=gemini`

**Option B — OpenAI GPT-3.5**
1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set `OPENAI_API_KEY=your_key` in `.env`
3. Set `LLM_PROVIDER=openai`

> ⚡ **No API key?** The app still works! It runs in rule-based mode with full medication tracking, health logging, and dashboard features. Only the AI chatbot requires an API key.

### 5. Run the Application
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```
Healthcare Monitoring AI Agent/
├── app.py                    # Main Streamlit entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── README.md                 # This file
├── .streamlit/
│   └── config.toml           # Streamlit dark theme configuration
├── database/
│   └── db_manager.py         # SQLite CRUD for all health data
├── agents/
│   └── health_agent.py       # LangChain ReAct agent with all tools
├── tools/
│   ├── medication_tool.py    # Medication management LangChain tools
│   ├── health_data_tool.py   # Health metrics LangChain tools
│   └── medical_info_tool.py  # MedlinePlus API tool
├── pages/
│   ├── dashboard.py          # Health dashboard with charts
│   ├── medications.py        # Medication tracker UI
│   ├── chatbot.py            # AI chatbot interface
│   └── health_log.py         # Health metrics logging
└── utils/
    ├── visualizations.py     # Plotly chart utilities
    └── data_parser.py        # JSON/CSV/XML data parsing
```

---

## 🗃️ Database Schema

| Table | Purpose |
|-------|---------|
| `users` | Patient profiles (name, age, gender, vitals) |
| `medications` | Active medication schedules |
| `medication_logs` | Dose-by-dose adherence tracking |
| `health_metrics` | Time-series health measurements |
| `health_goals` | Wellness targets with progress |
| `chat_history` | AI conversation history |

---

## 🤖 AI Agent Tools

The LangChain ReAct agent has access to these tools:

| Tool | Function |
|------|----------|
| `medical_info_lookup` | Search MedlinePlus for health topics |
| `add_medication_reminder` | Add new medication schedules |
| `get_todays_medications` | Retrieve today's medication schedule |
| `mark_medication_taken` | Log a dose as taken |
| `get_medication_adherence_report` | Generate adherence statistics |
| `log_health_metric` | Record health measurements |
| `get_health_summary` | Summarize recent health trends |
| `parse_health_data_json` | Bulk import health data |
| `calculate_bmi` | BMI calculation and logging |

---

## 🌐 Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" → Select your repository → Select `app.py`
4. Add secrets in the Streamlit Cloud dashboard:
   ```toml
   GOOGLE_API_KEY = "your_key_here"
   LLM_PROVIDER = "gemini"
   ```
5. Click Deploy!

---

## ⚠️ Medical Disclaimer

> **HealthGuard AI is for informational and educational purposes only.**
> It is NOT a substitute for professional medical advice, diagnosis, or treatment.
> Always consult a qualified healthcare professional for medical decisions.
> **In case of medical emergency, call 112 (India) immediately.**

---

## 🔒 Privacy & Security

- All data is stored locally in an SQLite database (`health_data.db`)
- No health data is sent to external servers (only anonymized LLM queries)
- API keys are stored in `.env` (never commit this to version control)
- Add `.env` and `health_data.db` to `.gitignore`

---

## 📊 Week 1-2 Milestone Checklist

- [x] GitHub repo with healthcare project structure
- [x] Development environment setup (Python, pandas, LangChain, Streamlit)
- [x] Basic health data chatbot with medication reminder functionality
- [x] Health data parsing and storage (JSON/CSV/XML)
- [x] Medication scheduling and alerts system
- [x] Health metrics database (SQLite)
- [x] Deployable on Streamlit Cloud
- [x] Working demo with medication tracking and health monitoring

---

## 👥 Team

Built as part of the **Healthcare Monitoring AI Agent Development Project**.

---

*Made with ❤️ for better health outcomes*
