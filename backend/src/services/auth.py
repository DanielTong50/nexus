"""
Authentication and user identity service.

Provides user identity for the application. In the hackathon MVP,
this uses a simple mock implementation. Production would integrate
with OAuth/JWT.
"""

from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """User identity model."""
    id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User's display name")
    email: str = Field(..., description="User's email address")
    role: str = Field(..., description="User's role in the organization")
    team: Optional[str] = Field(None, description="User's team (e.g., 'partnerships', 'marketing')")


# Mock user for development
_MOCK_USER = User(
    id="dev-user-001",
    name="Dev User",
    email="dev@nexus.local",
    role="admin",
    team="core"
)


async def get_current_user(token: Optional[str] = None) -> User:
    """
    Get the current authenticated user.
    
    In the hackathon MVP, this returns a mock user. In production,
    this would validate the JWT/session token and return the real user.
    
    Args:
        token: Optional auth token (unused in mock implementation)
        
    Returns:
        User model with identity information
    """
    # TODO: Implement real auth in production
    # - Validate JWT token
    # - Fetch user from database
    # - Check permissions
    return _MOCK_USER


async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get a user by their ID.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        User model if found, None otherwise
    """
    # Mock implementation - only knows about the dev user
    if user_id == _MOCK_USER.id:
        return _MOCK_USER
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
