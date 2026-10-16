"""Debug Dojo — FastAPI application entry point.

Provides all API endpoints, health checks, CORS, and startup initialization.
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query, Request, status, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from config import get_settings
from database.connection import async_session, init_db, get_db
from database.seed import seed_challenges
from database.models import Submission, LearnerProfile
from modules.auth.dependencies import get_current_user, get_optional_user
from modules.challenges.service import list_challenges, get_challenge
from modules.submission.service import process_submission
from modules.hints.service import get_next_hint, get_hint_history
from modules.learner.service import get_learner_dashboard, get_or_create_learner
from modules.execution.judge0 import get_execution_provider

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info("Starting Debug Dojo backend...")
    
    # Initialize database tables
    await init_db()
    logger.info("Database tables created")
    
    # Seed challenges
    async with async_session() as session:
        count = await seed_challenges(session)
        await session.commit()
        logger.info("Seeded %d challenges", count)
    
    yield
    
    logger.info("Shutting down Debug Dojo backend...")


app = FastAPI(
    title="Debug Dojo API",
    description="AI-powered coding coach that teaches students to debug Python code",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please slow down."},
    )

app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================================================================
# Health endpoints
# ===================================================================

@app.get("/health", tags=["Health"])
async def health():
    """Health check — does not reveal secrets."""
    return {"status": "healthy", "service": "debug-dojo-api"}


@app.get("/health/ready", tags=["Health"])
async def readiness():
    """Readiness check — verifies database and execution provider."""
    checks = {"database": False, "judge0": False}
    
    try:
        async with async_session() as session:
            await session.execute(select(1))
        checks["database"] = True
    except Exception:
        pass
    
    try:
        provider = get_execution_provider()
        checks["judge0"] = await provider.is_healthy()
    except Exception:
        pass
    
    overall = all(checks.values())
    return {
        "status": "ready" if overall else "degraded",
        "checks": checks,
    }


# ===================================================================
# Challenge endpoints
# ===================================================================

@app.get("/api/challenges", tags=["Challenges"])
async def api_list_challenges(
    difficulty: Optional[str] = Query(None, description="Filter by difficulty: easy, medium, hard"),
    concept: Optional[str] = Query(None, description="Filter by concept tag"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    db: AsyncSession = Depends(get_db),
    user: Optional[dict] = Depends(get_optional_user),
):
    """List all challenges with optional filters.
    
    Public endpoint — does not require authentication.
    Hidden test details are never included.
    """
    challenges = await list_challenges(db, difficulty=difficulty, concept=concept, search=search)
    
    # If authenticated, add completion status
    if user:
        learner = await get_or_create_learner(db, user["sub"])
        completed_result = await db.execute(
            select(Submission.challenge_id)
            .where(Submission.learner_id == learner.id, Submission.overall_status == "passed")
            .distinct()
        )
        completed_ids = {row[0] for row in completed_result.all()}
        
        for c in challenges:
            c["completed"] = c["id"] in completed_ids
    
    return {"challenges": challenges}


@app.get("/api/challenges/{challenge_id}", tags=["Challenges"])
async def api_get_challenge(
    challenge_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get challenge details including visible tests.
    
    Hidden test inputs and expected outputs are NEVER returned.
    """
    challenge = await get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge


# ===================================================================
# Submission endpoint
# ===================================================================

class SubmitRequest(BaseModel):
    challenge_id: str = Field(..., description="Challenge ID or slug")
    code: str = Field(..., min_length=1, max_length=10000, description="Learner's code")


@app.post("/api/submit", tags=["Submissions"])
@limiter.limit("10/minute")
async def api_submit(
    request: Request,
    body: SubmitRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Submit code for evaluation.
    
    Requires authentication. Returns visible test results in full,
    hidden test results as number + outcome only.
    """
    result = await process_submission(
        db=db,
        learner_supabase_id=user["sub"],
        challenge_id=body.challenge_id,
        code=body.code,
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=result.get("status_code", 400),
            detail=result["error"],
        )
    
    return result


# ===================================================================
# Hint endpoint
# ===================================================================

class HintRequest(BaseModel):
    submission_id: str = Field(..., description="The submission to get a hint for")


@app.post("/api/hint", tags=["Hints"])
@limiter.limit("20/minute")
async def api_hint(
    request: Request,
    body: HintRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get the next progressive hint for a submission.
    
    Requires authentication. Enforces ownership — only the submission
    author can request hints.
    """
    # Verify submission exists and belongs to user
    sub_result = await db.execute(
        select(Submission).where(Submission.id == body.submission_id)
    )
    submission = sub_result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Verify ownership
    learner = await get_or_create_learner(db, user["sub"])
    if submission.learner_id != learner.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get challenge info
    from database.models import Challenge
    challenge_result = await db.execute(
        select(Challenge).where(Challenge.id == submission.challenge_id)
    )
    challenge = challenge_result.scalar_one_or_none()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Build visible test results for context (no hidden data)
    visible_results = []
    for r in submission.results:
        if not r.is_hidden:
            visible_results.append({
                "call": f"test {r.test_number}",
                "expected": "",  # Don't pass raw expected to AI
                "actual": r.actual_output,
                "outcome": r.outcome,
            })
    
    # Get the function name from the first test
    from database.models import ChallengeTest
    first_test_result = await db.execute(
        select(ChallengeTest)
        .where(ChallengeTest.challenge_id == challenge.id)
        .order_by(ChallengeTest.test_number)
        .limit(1)
    )
    first_test = first_test_result.scalar_one_or_none()
    function_name = first_test.function_name if first_test else "solution"
    
    hint_text, hint_level, source = await get_next_hint(
        db=db,
        submission_id=submission.id,
        learner_id=learner.id,
        challenge_slug=challenge.slug,
        challenge_id=challenge.id,
        challenge_description=challenge.description,
        function_name=function_name,
        learner_code=submission.code,
        visible_test_results=visible_results,
    )
    
    # Get full hint history
    history = await get_hint_history(db, submission.id)
    
    return {
        "hint": hint_text,
        "level": hint_level,
        "source": source,
        "history": history,
    }


# ===================================================================
# Learner dashboard endpoint
# ===================================================================

@app.get("/api/learner/{learner_id}", tags=["Learner"])
async def api_learner_dashboard(
    learner_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get learner dashboard: mistakes, mastery, progress, recommendation.
    
    Requires authentication. Rejects cross-user access.
    """
    # The learner_id in the URL should match the authenticated user's learner profile
    learner = await get_or_create_learner(db, user["sub"])
    
    if learner.id != learner_id:
        raise HTTPException(status_code=403, detail="Access denied: cross-user access not allowed")
    
    dashboard = await get_learner_dashboard(db, learner_id)
    
    if "error" in dashboard:
        raise HTTPException(status_code=404, detail=dashboard["error"])
    
    return dashboard


@app.get("/api/learner/me/dashboard", tags=["Learner"])
async def api_my_dashboard(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get the authenticated user's dashboard. Convenience endpoint."""
    learner = await get_or_create_learner(db, user["sub"])
    return await get_learner_dashboard(db, learner.id)


@app.get("/api/learner/me/profile", tags=["Learner"])
async def api_my_profile(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get the authenticated user's profile."""
    learner = await get_or_create_learner(db, user["sub"])
    return {
        "learner_id": learner.id,
        "email": user.get("email", ""),
        "display_name": learner.display_name,
        "created_at": learner.created_at.isoformat(),
    }


@app.get("/api/learner/me/submissions", tags=["Learner"])
async def api_my_submissions(
    challenge_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get the authenticated user's submission history."""
    learner = await get_or_create_learner(db, user["sub"])
    
    query = select(Submission).where(Submission.learner_id == learner.id)
    if challenge_id:
        query = query.where(Submission.challenge_id == challenge_id)
    query = query.order_by(Submission.created_at.desc()).limit(50)
    
    result = await db.execute(query)
    submissions = result.scalars().all()
    
    return {
        "submissions": [
            {
                "id": s.id,
                "challenge_id": s.challenge_id,
                "overall_status": s.overall_status,
                "created_at": s.created_at.isoformat(),
            }
            for s in submissions
        ]
    }


# ===================================================================
# Run with uvicorn
# ===================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=not settings.is_production,
    )
