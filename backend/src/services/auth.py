"""
Authentication and user identity service.

Provides user identity for the application using Clerk JWT verification.
"""

import httpx
import jwt
from typing import Optional
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from config.settings import settings

# HTTP Bearer token extractor
security = HTTPBearer(auto_error=False)


class User(BaseModel):
    """User identity model from Clerk JWT."""
    id: str = Field(..., description="Clerk user ID")
    email: Optional[str] = Field(None, description="User's email address")
    name: Optional[str] = Field(None, description="User's display name")
    role: str = Field(default="user", description="User's role in the organization")
    team: Optional[str] = Field(None, description="User's team")


# Cache for Clerk's JWKS (JSON Web Key Set)
_jwks_cache: Optional[dict] = None


async def _get_clerk_jwks() -> dict:
    """Fetch Clerk's JWKS for JWT verification."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    
    async with httpx.AsyncClient() as client:
        # Use configured Clerk frontend API URL
        response = await client.get(f"{settings.clerk_frontend_api}/.well-known/jwks.json")
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


def _get_signing_key(token: str, jwks: dict) -> str:
    """Get the signing key from JWKS that matches the token's kid."""
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # Convert JWK to PEM format for PyJWT
                from jwt import algorithms
                return algorithms.RSAAlgorithm.from_jwk(key)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate signing key",
        )
    except jwt.exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )


async def verify_clerk_token(token: str) -> dict:
    """Verify a Clerk JWT token and return its claims."""
    try:
        jwks = await _get_clerk_jwks()
        signing_key = _get_signing_key(token, jwks)
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            options={"verify_aud": False},  # Clerk doesn't always include aud
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    Get the current authenticated user from the Clerk JWT token.
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        User model with identity information
        
    Raises:
        HTTPException: If no valid token is provided
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    claims = await verify_clerk_token(token)
    
    # Extract user info from Clerk JWT claims
    user_id = claims.get("sub", "")
    
    # Clerk stores email and name in different places depending on the token type
    # Session tokens have user info directly, while others may have it nested
    email = claims.get("email") or claims.get("user", {}).get("email")
    name = claims.get("name") or claims.get("user", {}).get("name") or claims.get("first_name", "")
    
    return User(
        id=user_id,
        email=email,
        name=name,
        role="admin",  # Default role for now
        team="core",
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None.
    Use this for endpoints that work both with and without auth.
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# Legacy functions for backward compatibility
async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get a user by their ID (placeholder for future implementation)."""
    return None


def get_user_team_channel(user: User) -> str:
    """
    Get the Slack channel for a user's team.
    
    Args:
        user: The user model
        
    Returns:
        Slack channel name for the user's team
    """
    team_channels = {
        "partnerships": "#partnerships",
        "marketing": "#marketing",
        "finance": "#finance",
        "logistics": "#logistics",
        "developers": "#developers",
        "core": "#core-team",
    }
    return team_channels.get(user.team or "core", "#general")
