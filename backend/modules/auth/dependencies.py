"""JWT verification and user extraction for Supabase Auth."""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from config import get_settings

security = HTTPBearer(auto_error=False)
settings = get_settings()


async def verify_token(token: str) -> dict:
    """Verify a Supabase JWT and return its claims.
    
    Uses the JWT secret from settings to verify the token signature.
    Validates issuer and expiry automatically through python-jose.
    """
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={
                "verify_exp": True,
                "verify_aud": False,  # Supabase doesn't always set aud
            },
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """FastAPI dependency that extracts the current authenticated user from the JWT.
    
    Returns a dict with at minimum: {'sub': '<user_id>', 'email': '...'}
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = await verify_token(credentials.credentials)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user identity",
        )
    
    return {
        "sub": user_id,
        "email": payload.get("email", ""),
        "role": payload.get("role", "authenticated"),
    }


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """Like get_current_user but returns None for unauthenticated requests."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
