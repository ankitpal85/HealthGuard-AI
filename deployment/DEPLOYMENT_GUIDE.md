# HealthGuard AI — Deployment Guide & Architecture Setup

This directory contains cloud deployment configurations for **Render.com**, **Vercel**, **Railway**, and **Docker**.

## 📁 Repository Structure Overview

```text
Healthcare Monitoring AI Agent/
├── backend/
│   ├── main.py              # FastAPI REST API & SSE Server
│   ├── agents/              # LangGraph Stateful Clinical Agents
│   ├── database/            # SQLite & Supabase PostgreSQL Managers
│   ├── tools/               # Medical Tools (Drug interaction, AYUSH, Research, Vision/Voice)
│   └── utils/               # PDF Generator, Analytics & Security
├── frontend/
│   ├── src/                 # React 18 + TypeScript + Tailwind CSS UI
│   ├── public/              # Static assets
│   ├── package.json         # Node dependencies
│   └── vercel.json          # Vercel Single-Page Routing Rewrite Rules
├── deployment/
│   ├── Procfile             # PaaS Gunicorn/Uvicorn startup configuration
│   ├── render.yaml          # Render.com Blueprint configuration
│   ├── vercel.json          # Frontend Vercel deployment rules
│   └── DEPLOYMENT_GUIDE.md  # Detailed Deployment Instructions
├── tests/                   # Automated Unit & Integration Test Suite
├── requirements.txt         # Python dependencies for Backend
├── Procfile                 # Root PaaS startup script
├── render.yaml              # Root Render Blueprint
└── start.bat                # 1-Click Local Development Launcher
```

---

## 🚀 1-Click Cloud Deployment Steps

### Option 1: Backend Deployment (Render.com / Railway)
1. Go to [Render Dashboard](https://dashboard.render.com/) -> **New Web Service**.
2. Connect repository `ankitpal85/HealthGuard-AI`.
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `OPENAI_API_KEY`: *(Your OpenAI API Key)*
   - `GOOGLE_API_KEY`: *(Your Gemini API Key)*

### Option 2: Frontend Deployment (Vercel)
1. Go to [Vercel Dashboard](https://vercel.com/) -> **Add New Project**.
2. Select repository `ankitpal85/HealthGuard-AI`.
3. Set **Root Directory**: `frontend`
4. Framework Preset: **Vite**
5. Click **Deploy**. Vercel will automatically build and serve the application!

---

## 💻 Local Development Launcher
To run both Backend & Frontend locally with 1-click:
```bash
start.bat
```
- **Backend API**: `http://localhost:8000/docs`
- **Frontend App**: `http://localhost:5173/`
