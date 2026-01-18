"""Repository for user sessions and profiles."""

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.models.user_session import UserSession, UserProfile, UserActivity
from src.repositories.base import BaseRepository
from src.services.database import Collections


class SessionRepository(BaseRepository[UserSession]):
    """Repository for user sessions."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.USER_SESSIONS, UserSession)

    async def create_indexes(self) -> None:
        """Create indexes for sessions collection."""
        await self.collection.create_index([("session_id", ASCENDING)], unique=True)
        await self.collection.create_index([("user_id", ASCENDING), ("is_active", ASCENDING)])
        await self.collection.create_index([("expires_at", ASCENDING)])

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        expires_hours: int = 24,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSession:
        """Create a new user session."""
        session = UserSession.create_session(
            session_id=session_id,
            user_id=user_id,
            expires_hours=expires_hours,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await self.create(session)

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get a session by ID."""
        return await self.find_one({"session_id": session_id})

    async def get_valid_session(self, session_id: str) -> Optional[UserSession]:
        """Get a valid (active and not expired) session."""
        session = await self.get_session(session_id)
        if session and session.is_valid():
            return session
        return None

    async def get_user_sessions(
        self,
        user_id: str,
        active_only: bool = True,
    ) -> list[UserSession]:
        """Get all sessions for a user."""
        query = {"user_id": user_id}
        if active_only:
            query["is_active"] = True
            query["expires_at"] = {"$gt": datetime.utcnow()}
        return await self.find_many(query, sort=[("created_at", DESCENDING)])

    async def revoke_session(self, session_id: str) -> Optional[UserSession]:
        """Revoke/deactivate a session."""
        return await self.update_one(
            {"session_id": session_id},
            {"is_active": False},
        )

    async def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user."""
        return await self.update_many(
            {"user_id": user_id, "is_active": True},
            {"is_active": False},
        )

    async def update_activity(self, session_id: str) -> Optional[UserSession]:
        """Update the last activity timestamp for a session."""
        return await self.update_one(
            {"session_id": session_id},
            {"last_activity": datetime.utcnow()},
        )

    async def cleanup_expired(self) -> int:
        """Delete all expired sessions."""
        return await self.delete_many(
            {"expires_at": {"$lt": datetime.utcnow()}}
        )


class UserProfileRepository(BaseRepository[UserProfile]):
    """Repository for user profiles."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.USER_PROFILES, UserProfile)

    async def create_indexes(self) -> None:
        """Create indexes for user profiles collection."""
        await self.collection.create_index([("user_id", ASCENDING)], unique=True)
        await self.collection.create_index([("email", ASCENDING)], unique=True)
        await self.collection.create_index([("role", ASCENDING)])
        await self.collection.create_index([("team", ASCENDING)])

    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        """Get a user profile by user ID."""
        return await self.find_one({"user_id": user_id})

    async def get_by_email(self, email: str) -> Optional[UserProfile]:
        """Get a user profile by email."""
        return await self.find_one({"email": email.lower()})

    async def create_profile(
        self,
        user_id: str,
        email: str,
        name: str,
        role: str = "member",
        team: Optional[str] = None,
    ) -> UserProfile:
        """Create a new user profile."""
        profile = UserProfile(
            user_id=user_id,
            email=email.lower(),
            name=name,
            role=role,
            team=team,
        )
        return await self.create(profile)

    async def create_or_update_profile(
        self,
        user_id: str,
        email: str,
        name: str,
        role: Optional[str] = None,
        team: Optional[str] = None,
    ) -> UserProfile:
        """Create or update a user profile."""
        existing = await self.get_by_user_id(user_id)
        if existing:
            update_data = {"email": email.lower(), "name": name}
            if role:
                update_data["role"] = role
            if team:
                update_data["team"] = team
            return await self.update_one({"user_id": user_id}, update_data)

        return await self.create_profile(user_id, email, name, role or "member", team)

    async def update_last_login(self, user_id: str) -> Optional[UserProfile]:
        """Update the last login timestamp for a user."""
        return await self.update_one(
            {"user_id": user_id},
            {"last_login": datetime.utcnow()},
        )

    async def deactivate_user(self, user_id: str) -> Optional[UserProfile]:
        """Deactivate a user account."""
        return await self.update_one(
            {"user_id": user_id},
            {"is_active": False},
        )

    async def get_users_by_role(self, role: str) -> list[UserProfile]:
        """Get all users with a specific role."""
        return await self.find_many({"role": role, "is_active": True})

    async def get_users_by_team(self, team: str) -> list[UserProfile]:
        """Get all users in a specific team."""
        return await self.find_many({"team": team, "is_active": True})


class UserSessionRepository:
    """Facade for all user session and profile operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.sessions = SessionRepository(db)
        self.profiles = UserProfileRepository(db)

    async def create_indexes(self) -> None:
        """Create all indexes for session and profile collections."""
        await self.sessions.create_indexes()
        await self.profiles.create_indexes()

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        expires_hours: int = 24,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSession:
        """Create a new session."""
        return await self.sessions.create_session(
            session_id, user_id, expires_hours, ip_address, user_agent
        )

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get a session by ID."""
        return await self.sessions.get_session(session_id)

    async def validate_session(self, session_id: str) -> Optional[tuple[UserSession, UserProfile]]:
        """Validate a session and return both session and user profile."""
        session = await self.sessions.get_valid_session(session_id)
        if not session:
            return None

        profile = await self.profiles.get_by_user_id(session.user_id)
        if not profile or not profile.is_active:
            return None

        # Update activity
        await self.sessions.update_activity(session_id)

        return session, profile

    async def revoke_session(self, session_id: str) -> Optional[UserSession]:
        """Revoke a session."""
        return await self.sessions.revoke_session(session_id)

    async def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get a user profile."""
        return await self.profiles.get_by_user_id(user_id)

    async def create_or_update_profile(
        self,
        user_id: str,
        email: str,
        name: str,
        role: Optional[str] = None,
        team: Optional[str] = None,
    ) -> UserProfile:
        """Create or update a user profile."""
        return await self.profiles.create_or_update_profile(
            user_id, email, name, role, team
        )
