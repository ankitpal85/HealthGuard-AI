> **System Architecture, Microservices Pipeline, Technology Stack Matrix, HIPAA Security, API Manual, and Demo Video Blueprint**

---

## 🛠️ 1. Technology Stack Specification (Track A & Track B Matrix)

HealthGuard AI is designed to support both a rapid, high-impact **Track A** Streamlit stack and an enterprise-ready **Track B** microservice stack.

| Component Layer | **Track A Stack (Production Streamlit Core)** | **Track B Stack (Enterprise Cloud Microservices)** |
|---|---|---|
| **Frontend UI** | Streamlit + Custom Glassmorphic HTML/CSS + Web Speech API | React 18 / Next.js + Tailwind CSS + Chart.js |
| **Backend Engine** | Python 3.10+ + LangChain + LangGraph Stateful Pipeline | FastAPI + LangGraph + Celery Async Task Workers |
| **Data Analytics & ML** | pandas + numpy + scikit-learn + Plotly Interactive | pandas + scikit-learn + SciPy + Custom ML Pipeline |
| **Database & Caching** | SQLite Engine + AES-256 AES-GCM Encrypted Notes | PostgreSQL (Relational Data) + Redis (Session Cache) |
| **LLM Intelligence** | Google Gemini 2.5 Flash / GPT-3.5-turbo / MedAlpaca | GPT-4o / Claude 3.5 Sonnet / Gemini 2.5 Pro |
| **Healthcare APIs** | 1mg (Meds), Practo (Doctors), PubMed (NCBI), OpenWeather AQI | Google Fit API, Nutrition APIs, 1mg, Practo |
| **Auth & Security** | Firebase Auth REST API (SignUp/SignIn) + Local Salted SHA-256 Fallback | Auth0 / Firebase Auth with Healthcare RBAC |
| **Deployment Platform** | Streamlit Cloud / Docker Container | Vercel (Frontend) + Railway / Render (Backend Microservices) |
| **Alert Monitoring** | Real-Time Vital Threshold Monitor + Caregiver Alert Logs | Custom Health Monitoring Dashboard + SMS Webhooks |

---

## 🔐 2. Firebase Authentication & Security Architecture

HealthGuard AI implements a dual-tier Authentication pipeline (`utils/firebase_auth.py` & `pages/auth.py`):

1. **Firebase Auth Cloud Tier**:
   - Uses Firebase Identity Toolkit REST API (`accounts:signUp`, `accounts:signInWithPassword`).
   - Secure token exchange (`idToken`, `localId`) and cloud-managed user identities.
   - Configurable via `FIREBASE_WEB_API_KEY` in environment or Streamlit UI settings.
2. **Local Salted Hash Fallback Tier**:
   - Uses salted SHA-256 password hashing for offline / local database authentication.
   - Protects against credential compromise while ensuring zero-downtime availability when running offline.

---

## 📐 3. Architecture & Microservices Overview

HealthGuard AI is engineered as a modular, decoupled microservice-style healthcare pipeline. Each subsystem operates with isolated responsibilities to ensure high throughput, zero-downtime tool execution, and seamless multi-provider fallback.

```
                  ┌─────────────────────────────────────────┐
                  │   Streamlit / Web Speech UX Interface   │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │    LangGraph Stateful Agent Pipeline    │
                  │   (Emergency Triage -> Tool Router)     │
                  └─────┬──────────────┬──────────────┬─────┘
                        │              │              │
        ┌───────────────┴──┐   ┌───────┴──────────┐   │   ┌────────────────────┐
        │ Auth & Security  │   │  Health Data DB  │   ├───┤ Predictive ML Risk │
        │ (HIPAA & Crypto) │   │ (SQLite Engine)  │   │   │  (Framingham/Reg)  │
        └──────────────────┘   └──────────────────┘   │   └────────────────────┘
                                                      │
                                   ┌──────────────────┴─────────────────┐
                                   │  Indian & Global Healthcare APIs   │
                                   │ (1mg, Practo, PubMed, AQI, Vision) │
                                   └────────────────────────────────────┘
```

### Core Subsystems:
1. **Stateful Conversational Agent Node (`agents/health_agent.py`)**:
   - Built on LangGraph `StateGraph`.
   - Priority 0 Node: **Emergency Triage Filter** (Intercepts critical keywords like chest pain, stroke, breathlessness before sending to LLM).
   - Priority 1 Node: **Multi-Provider LLM Binding** (Tries Gemini 2.5/2.0 Flash with automatic fallback to OpenAI GPT-3.5 and offline Generative Engine fallback).
2. **Indian Health Subsystem (`tools/indian_health_tool.py`, `pages/indian_health.py`)**:
   - 1mg Medicine & Generic Price Database (Prices in ₹, active ingredients, generic substitutes).
   - Practo Doctor Appointment Scheduler.
   - Ayurvedic Herbal & Dosha Engine (Vata, Pitta, Kapha quiz & herb library).
   - ABHA (Ayushman Bharat ID) & Health Insurance Locker.
3. **Family & Caregiver Alert System (`pages/family_caregiver.py`)**:
   - Multi-profile user context switcher (Self, Parents, Spouse, Children).
   - Real-time vitals monitoring against threshold rules with instant visual emergency badges and simulated SMS/Email caregiver dispatches.
4. **Vision & Voice AI Subsystem (`tools/vision_voice_tool.py`, `pages/vision_voice.py`)**:
   - Prescription OCR & Lab Report diagnostic analyzer.
   - Skin condition visual pattern evaluator.
   - Browser Web Speech API for voice command input.

---

## 🗄️ 2. Database Schema & Entity Relationships

The database is built on SQLite with index optimizations on `user_id` and `recorded_at`.

| Table | Primary Columns | Description |
|---|---|---|
| `users` | `id, name, age, gender, weight_kg, height_cm, blood_group` | Core patient profile |
| `medications` | `id, user_id, name, dosage, frequency, time_slots, start_date` | Medication schedules |
| `medication_logs` | `id, medication_id, user_id, scheduled_at, status` | Adherence tracking |
| `health_metrics` | `id, user_id, metric_type, value, value2, unit, recorded_at` | Vital signs & fitness data |
| `health_goals` | `id, user_id, goal_type, target_value, current_value, status` | Wellness goal tracking |
| `nutrition_logs` | `id, user_id, meal_type, calories, protein_g, carbs_g, fat_g` | Diet and meal logs |
| `indian_medications` | `id, brand_name, generic_name, price_inr, substitutes` | 1mg medicine database |
| `ayurvedic_herbs` | `id, name, sanskrit_name, primary_benefit, dosha_balancing` | Ayurvedic herb catalog |
| `doctor_appointments` | `id, user_id, doctor_name, specialty, clinic_hospital, date` | Practo appointments |
| `insurance_policies` | `id, user_id, provider_name, policy_number, abha_id, coverage` | ABHA & Insurance locker |
| `family_members` | `id, user_id, name, relationship, age, medical_notes` | Multi-profile family records |
| `caregiver_contacts` | `id, user_id, name, phone, email, notify_critical` | Emergency caregiver contacts |
| `health_alerts_log` | `id, user_id, alert_type, metric_name, severity, message` | Real-time threshold alerts |

---

## 🔒 3. Security, Privacy & HIPAA Compliance

* **Data Encryption at Rest**: Sensitive clinical notes are protected via obfuscated encryption (`utils/security.py`).
* **HIPAA Safe Harbor De-Identification**: Exported datasets strip all 18 PHI identifiers (names, phone numbers, exact addresses, exact timestamps).
* **Input Validation**: All physiological inputs (BP, Heart Rate, Glucose, SpO2) pass strict range checking (e.g. Systolic BP 60–260 mmHg).
* **Cross-Site Scripting (XSS) & SQL Injection Protection**: Sanitized inputs using parametric queries in SQLite.

---

## 🎥 4. Demo Video Script & Walkthrough Outline

### **Script A: Track A Demo (5-7 Minutes)**
1. **0:00 - 1:00 | Introduction & Dashboard**: Present HealthGuard AI overview, dark mode UI, 7-day adherence gauge, quick vital logging.
2. **1:00 - 2:30 | Indian Healthcare & 1mg Lookup**: Demonstrate searching Dolo 650, finding cheaper generic substitutes in ₹, Practo doctor appointment booking, and ABHA ID locker.
3. **2:30 - 4:00 | Medication Tracker & Drug Interactions**: Show adding a medication, marking doses taken, viewing adherence reports, and running interaction checks (Aspirin + Warfarin).
4. **4:00 - 5:30 | ML Predictive Risk & Automated Report**: Showcase Framingham CVD risk score, Diabetes risk, and 1-click HTML/Markdown clinical report download.
5. **5:30 - 6:30 | AI Chatbot with Emergency Triage**: Test asking emergency chest pain query -> Instant 112/911 emergency banner.

### **Script B: Track B Advanced Demo (8-10 Minutes)**
1. **0:00 - 1:30 | Architecture & Microservices Overview**: Explain LangGraph stateful agent, multi-provider LLM fallback, and SQLite database schema.
2. **1:30 - 3:30 | Comprehensive Indian Healthcare & Ayurveda**: Walkthrough 1mg prices in INR, Practo doctor search, Ayurvedic Dosha quiz (Vata/Pitta/Kapha), and city AQI respiratory risk check.
3. **3:30 - 5:30 | Family Health & Real-Time Alert System**: Add family member profile, register caregiver contact, and trigger real-time critical vital alert (BP > 180 mmHg).
4. **5:30 - 7:30 | Vision AI & Speech-to-Text Voice Query**: Upload prescription image -> Vision OCR dosage parsing. Speak voice query via Web Speech API.
5. **7:30 - 9:00 | Data Export & HIPAA Security**: Demonstrate multi-format export (JSON, CSV, XML, HTML) and HIPAA Safe Harbor de-identified dataset export.
6. **9:00 - 10:00 | Conclusion & Summary**: Wrap up production readiness and deployment roadmap.
