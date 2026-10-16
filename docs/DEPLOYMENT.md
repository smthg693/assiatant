# Debug Dojo — Deployment Guide

This guide covers deploying the Debug Dojo platform across local development, staging, and production environments.

## Architecture Overview

| Component | Technology | Target Host |
|-----------|------------|-------------|
| Frontend | React 19 + Vite + CodeMirror 6 | Vercel |
| Backend | Python 3.11 + FastAPI + Uvicorn | Render |
| Database | PostgreSQL + AsyncPG (or SQLite for local) | Supabase |
| Authentication | Supabase Auth (JWT HS256) | Supabase |
| Code Execution | Judge0 CE (Sandboxed Docker) | RapidAPI / Self-hosted Judge0 |
| AI Hints | Groq API (Llama 3.3 70B) | Groq Cloud |

---

## Environment Variables

### Backend (`backend/.env`)

```bash
# Supabase Authentication
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret

# Database
# For local dev:
DATABASE_URL=sqlite+aiosqlite:///./debug_dojo.db
# For production (Supabase PostgreSQL):
# DATABASE_URL=postgresql+asyncpg://postgres:password@db.your-project.supabase.co:5432/postgres

# Code Execution (Direct Judge0 CE)
JUDGE0_BASE_URL=https://ce.judge0.com
JUDGE0_API_KEY=
JUDGE0_LANGUAGE_ID=
JUDGE0_REQUEST_TIMEOUT=10
JUDGE0_EXECUTION_TIMEOUT=5
JUDGE0_POLL_INTERVAL=1
JUDGE0_MAX_POLL_TIME=30

# AI Coaching (Groq)
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile

# Application Settings
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
APP_ENV=production
PORT=8000
```

### Frontend (`frontend/.env`)

```bash
VITE_API_BASE_URL=https://your-backend.onrender.com
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

---

## Local Development Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run FastAPI backend
python -m uvicorn main:app --reload --port 8000
```

Backend will automatically:
- Initialize SQLite schema if not present
- Seed the 12 challenges and test cases
- Expose OpenAPI documentation at `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Run Vite dev server
npm run dev
```

Frontend is accessible at `http://localhost:5173`.

---

## Production Deployment

### 1. Backend Deployment (Render)

1. Connect your repository to Render as a **Web Service**.
2. Set **Root Directory** to `backend`.
3. Set **Runtime** to `Python 3`.
4. Set **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
5. Set **Start Command**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
6. Add the backend environment variables under **Environment**.
7. Deploy! Health check endpoint is `/health`.

### 2. Frontend Deployment (Vercel)

1. Import your repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework Preset: **Vite**.
4. Set Build Command: `npm run build`.
5. Set Output Directory: `dist`.
6. Add `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY` to Vercel Environment Variables.
7. Deploy!

---

## Health Checks & Monitoring

- **Liveness Check**: `GET /health` (returns `{"status": "healthy"}`)
- **Readiness Check**: `GET /health/ready` (verifies database connectivity and Judge0 availability)
