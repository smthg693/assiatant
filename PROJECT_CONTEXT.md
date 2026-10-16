# Debug Dojo — Project Context

## Purpose

Debug Dojo is a coding-coach platform that teaches students to debug Python code without providing complete solutions. It runs learner submissions securely via Direct Judge0 CE (ce.judge0.com or self-hosted), provides progressive AI hints via Groq, tracks mistake patterns, and recommends challenges that target recurring weaknesses.

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend framework | React + Vite | Fast builds, modern DX, wide ecosystem |
| Code editor | CodeMirror 6 | Lightweight, extensible, good Python support |
| Backend framework | FastAPI | Async, type-safe, auto-generated OpenAPI docs |
| Authentication | Supabase Auth | Email/password with JWT, session management |
| Database | Supabase PostgreSQL | Managed, RLS support, integrated with auth |
| Code execution | Direct Judge0 CE | Secure sandboxed execution, dynamic Python language discovery, no RapidAPI dependencies |
| AI coaching | Groq API | Fast inference, LLM-powered hint generation |
| Frontend hosting | Vercel | Zero-config React deployment |
| Backend hosting | Render | Python/FastAPI support with env vars |

## Module Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py               # Environment configuration
├── database/
│   ├── connection.py       # SQLAlchemy async engine
│   ├── models.py           # All table models
│   └── seed.py             # Challenge seeding
├── modules/
│   ├── auth/               # JWT verification, user extraction
│   ├── challenges/         # Challenge CRUD and listing
│   ├── execution/          # ExecutionProvider interface + Judge0
│   ├── judge/              # Test runner, output comparator
│   ├── hints/              # Groq client, curated hints, progression
│   ├── diagnosis/          # Mistake detection (5 categories)
│   ├── learner/            # Analytics, mastery, recommendations
│   └── submission/         # Submit orchestrator
└── tests/                  # Unit and integration tests

frontend/
├── src/
│   ├── components/         # Reusable UI components
│   ├── pages/              # Route-level page components
│   ├── lib/                # Supabase client, API client
│   ├── hooks/              # Custom React hooks
│   └── styles/             # CSS design system
└── public/                 # Static assets
```

## Mandatory Challenges

1. `last-k-total` — Sum the last k marks
2. `count-passes` — Count marks >= 40
3. `first-n-squares` — List of perfect squares
4. `middle-three` — Middle three items from list

## Mistake Categories

1. `off_by_one` — Off-by-one errors in indexing/ranges
2. `unhandled_short_input` — Missing edge case for short/empty inputs
3. `print_not_return` — Printing instead of returning
4. `boundary_comparison` — Wrong comparison operator at boundaries
5. `mutates_input` — Unintended mutation of input data

## Outcome Values

- `passed` — Test output matches expected
- `wrong_output` — Test ran but output differs 
- `runtime_error` — Exception, memory/output limit violation
- `timeout` — Execution exceeded time limit

## Security Invariants

- Hidden test fixtures (inputs + expected outputs) never leave the backend
- Raw hidden execution output is compared server-side, never sent to client
- AI prompts never contain hidden test data
- Learner code is executed only in Judge0, never in the FastAPI process
- All API endpoints verify JWT and enforce ownership
