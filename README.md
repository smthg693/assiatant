# Debug Dojo 🥋

An AI-powered coding coach that teaches students to debug their own Python code — without giving away the answers.

## Philosophy

Debug Dojo doesn't fix your code for you. Instead, it:

1. **Runs your code** against visible and hidden tests using secure sandboxed execution
2. **Classifies failures** with precise outcome semantics (passed, wrong_output, runtime_error, timeout)
3. **Detects mistake patterns** across your submissions (off-by-one, boundary errors, etc.)
4. **Provides progressive hints** that guide you toward the bug without revealing the solution
5. **Tracks your mastery** and recommends challenges that target your weak spots

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite, CodeMirror 6 |
| Backend | Python 3.11 + FastAPI |
| Auth | Supabase Auth |
| Database | Supabase PostgreSQL |
| Execution | Judge0 |
| AI Coaching | Groq API |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Supabase project
- Judge0 API access
- Groq API key

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env   # Fill in your credentials
python -m uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # Fill in your credentials
npm run dev
```

## Documentation

- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Model](docs/SECURITY.md)
- [Project Context](PROJECT_CONTEXT.md)
- [Acceptance Checklist](ACCEPTANCE_CHECKLIST.md)

## License

MIT
