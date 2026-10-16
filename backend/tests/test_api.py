"""Tests for FastAPI endpoints, OpenAPI docs, and Authentication/Authorization security."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from main import app
from database.connection import init_db, async_session
from database.seed import seed_challenges
from database.models import LearnerProfile, Submission
from modules.auth.dependencies import get_current_user
import uuid


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await init_db()
    async with async_session() as session:
        await seed_challenges(session)
        await session.commit()


@pytest.mark.asyncio
async def test_health_endpoints():
    """Verify health and readiness endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        # Must not leak secrets
        assert "api_key" not in data
        assert "jwt_secret" not in data

        resp_ready = await client.get("/health/ready")
        assert resp_ready.status_code == 200
        assert "checks" in resp_ready.json()


@pytest.mark.asyncio
async def test_openapi_documentation_generated():
    """Verify OpenAPI schema is generated and contains core paths."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "paths" in schema
        paths = schema["paths"]
        assert "/api/submit" in paths
        assert "/api/hint" in paths
        assert "/api/challenges" in paths
        assert "/api/learner/{learner_id}" in paths


@pytest.mark.asyncio
async def test_challenges_api_filtering():
    """Verify listing challenges with difficulty filter."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/challenges?difficulty=easy")
        assert resp.status_code == 200
        data = resp.json()
        assert "challenges" in data
        for c in data["challenges"]:
            assert c["difficulty"] == "easy"


@pytest.mark.asyncio
async def test_auth_protection_on_endpoints():
    """Verify unauthenticated requests to protected endpoints return 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Submit requires auth
        sub_resp = await client.post("/api/submit", json={"challenge_id": "last-k-total", "code": "pass"})
        assert sub_resp.status_code == 401
        
        # Hint requires auth
        hint_resp = await client.post("/api/hint", json={"submission_id": "test-sub-id"})
        assert hint_resp.status_code == 401
        
        # Learner dashboard requires auth
        dash_resp = await client.get("/api/learner/some-learner-id")
        assert dash_resp.status_code == 401


@pytest.mark.asyncio
async def test_cross_user_access_rejected():
    """Verify cross-user access to learner dashboards is rejected with 403."""
    user_a = {"sub": f"user-a-{uuid.uuid4()}", "email": "a@example.com", "role": "authenticated"}
    user_b = {"sub": f"user-b-{uuid.uuid4()}", "email": "b@example.com", "role": "authenticated"}
    
    # Create learner profile for User B in DB
    async with async_session() as session:
        learner_b = LearnerProfile(supabase_user_id=user_b["sub"])
        session.add(learner_b)
        await session.commit()
        learner_b_id = learner_b.id

    # Authenticate as User A and attempt to access User B's dashboard
    app.dependency_overrides[get_current_user] = lambda: user_a
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/learner/{learner_b_id}")
            assert resp.status_code == 403
            assert "cross-user" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_submission_ownership_enforced_on_hints():
    """Verify only submission author can request hints (403 on other user's submission)."""
    user_a = {"sub": f"owner-a-{uuid.uuid4()}", "email": "a@test.com", "role": "authenticated"}
    user_b = {"sub": f"attacker-b-{uuid.uuid4()}", "email": "b@test.com", "role": "authenticated"}
    
    async with async_session() as session:
        learner_a = LearnerProfile(supabase_user_id=user_a["sub"])
        session.add(learner_a)
        await session.flush()
        
        sub = Submission(
            learner_id=learner_a.id,
            challenge_id="last-k-total",
            code="def last_k_total(m, k): pass",
            overall_status="failed",
        )
        session.add(sub)
        await session.commit()
        sub_id = sub.id

    # Authenticate as User B and request hint on User A's submission
    app.dependency_overrides[get_current_user] = lambda: user_b
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/hint", json={"submission_id": sub_id})
            assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_submit_returns_503_when_execution_service_unavailable():
    """Verify submit endpoint returns HTTP 503 Service Unavailable when Judge0 cannot be reached."""
    user = {"sub": f"test-user-{uuid.uuid4()}", "email": "learner@test.com", "role": "authenticated"}
    app.dependency_overrides[get_current_user] = lambda: user
    
    mock_provider = AsyncMock()
    from modules.execution.judge0 import ExecutionResult, ExecutionStatus
    mock_provider.execute.return_value = ExecutionResult(
        status=ExecutionStatus.INTERNAL_ERROR,
        error_message="Judge0 connection refused: 503 Service Unavailable",
    )
    
    try:
        with patch("modules.judge.engine.get_execution_provider", return_value=mock_provider):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/submit",
                    json={"challenge_id": "last-k-total", "code": "def last_k_total(m, k): return 0"},
                )
                assert resp.status_code == 503
                assert "unavailable" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()

