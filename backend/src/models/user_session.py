"""User session and profile models for authentication and authorization."""

from datetime import datetime, timedelta
from typing import Literal, Optional

from pydantic import Field

from src.models.base import BaseDocument


class UserSession(BaseDocument):
    """MongoDB document for user sessions."""

    session_id: str = Field(description="Unique session identifier")
    user_id: str = Field(description="Reference to the user")
    expires_at: datetime = Field(description="Session expiration time")
    is_active: bool = Field(default=True, description="Whether session is active")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    last_activity: datetime = Field(
        default_factory=datetime.utcnow, description="Last activity timestamp"
    )
    metadata: dict = Field(default_factory=dict, description="Additional session data")

    @classmethod
    def create_session(
        cls,
        session_id: str,
        user_id: str,
        expires_hours: int = 24,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "UserSession":
        """Create a new session with automatic expiry."""
        return cls(
            session_id=session_id,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours),
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if session is valid (active and not expired)."""
        return self.is_active and not self.is_expired()


class UserProfile(BaseDocument):
    """MongoDB document for user profiles."""

    user_id: str = Field(description="Unique user identifier")
    email: str = Field(description="User email address")
    name: str = Field(description="User display name")
    role: Literal["admin", "organizer", "member", "viewer"] = Field(
        default="member", description="User role for authorization"
    )
    team: Optional[str] = Field(default=None, description="Team or department")
    avatar_url: Optional[str] = Field(default=None, description="Profile picture URL")
    preferences: dict = Field(default_factory=dict, description="User preferences")
    is_active: bool = Field(default=True, description="Whether user account is active")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    metadata: dict = Field(default_factory=dict, description="Additional user data")

    def can_approve(self) -> bool:
        """Check if user can approve HITL actions."""
        return self.role in ("admin", "organizer")

    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role == "admin"

    def can_view_finance(self) -> bool:
        """Check if user can view financial data."""
        return self.role in ("admin", "organizer")


class UserActivity(BaseDocument):
    """MongoDB document for tracking user activity."""

    user_id: str = Field(description="Reference to the user")
    activity_type: str = Field(description="Type of activity")
    description: str = Field(description="Activity description")
    resource_type: Optional[str] = Field(
        default=None, description="Type of resource accessed"
    )
    resource_id: Optional[str] = Field(default=None, description="ID of resource accessed")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    metadata: dict = Field(default_factory=dict, description="Additional activity data")
