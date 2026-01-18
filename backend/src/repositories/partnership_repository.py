"""Repository for partnership management (sponsors, judges, mentors)."""

from datetime import datetime
from typing import Literal, Optional, Type, TypeVar

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.models.partnership import (
    PartnershipBase,
    SponsorPartnership,
    JudgePartnership,
    MentorPartnership,
    PartnershipStats,
)
from src.repositories.base import BaseRepository
from src.services.database import Collections

T = TypeVar("T", bound=PartnershipBase)


class BasePartnershipRepository(BaseRepository[T]):
    """Base repository for all partnership types."""

    async def create_indexes(self) -> None:
        """Create indexes for partnership collection."""
        await self.collection.create_index([("company", ASCENDING)])
        await self.collection.create_index([("status", ASCENDING)])
        await self.collection.create_index([("contact_email", ASCENDING)])
        await self.collection.create_index([("sync_status", ASCENDING)])

    async def find_by_company(self, company: str) -> Optional[T]:
        """Find a partnership by company name."""
        return await self.find_one({"company": company})

    async def find_by_email(self, email: str) -> Optional[T]:
        """Find a partnership by contact email."""
        return await self.find_one({"contact_email": email.lower()})

    async def find_by_status(
        self,
        status: str,
        limit: int = 100,
    ) -> list[T]:
        """Find partnerships by status."""
        return await self.find_many(
            {"status": status},
            sort=[("updated_at", DESCENDING)],
            limit=limit,
        )

    async def update_status(
        self,
        company: str,
        new_status: str,
        notes: Optional[str] = None,
    ) -> Optional[T]:
        """Update partnership status."""
        update_data = {
            "status": new_status,
            "sync_status": "pending",
        }
        if notes:
            update_data["notes"] = notes

        return await self.update_one({"company": company}, update_data)

    async def mark_synced(
        self,
        company: str,
        row_number: Optional[int] = None,
    ) -> Optional[T]:
        """Mark a partnership as synced with Google Sheets."""
        update_data = {
            "sync_status": "synced",
            "last_synced_at": datetime.utcnow(),
        }
        if row_number is not None:
            update_data["sheets_row_number"] = row_number

        return await self.update_one({"company": company}, update_data)

    async def find_pending_sync(self) -> list[T]:
        """Find partnerships that need to be synced to Google Sheets."""
        return await self.find_many(
            {"sync_status": {"$ne": "synced"}},
            sort=[("updated_at", ASCENDING)],
        )

    async def search(
        self,
        query: str,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[T]:
        """Search partnerships by company name or contact."""
        search_query = {
            "$or": [
                {"company": {"$regex": query, "$options": "i"}},
                {"contact_name": {"$regex": query, "$options": "i"}},
                {"contact_email": {"$regex": query, "$options": "i"}},
            ]
        }
        if status:
            search_query["status"] = status

        return await self.find_many(search_query, limit=limit)


class SponsorRepository(BasePartnershipRepository[SponsorPartnership]):
    """Repository for sponsor partnerships."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.PARTNERSHIPS_SPONSORS, SponsorPartnership)

    async def create_indexes(self) -> None:
        """Create indexes for sponsors collection."""
        await super().create_indexes()
        await self.collection.create_index([("tier", ASCENDING)])
        await self.collection.create_index([("payment_status", ASCENDING)])

    async def find_by_tier(
        self,
        tier: str,
        confirmed_only: bool = False,
    ) -> list[SponsorPartnership]:
        """Find sponsors by tier."""
        query = {"tier": tier}
        if confirmed_only:
            query["status"] = "Confirmed"
        return await self.find_many(query)

    async def get_confirmed_total(self) -> float:
        """Get total confirmed sponsorship amount."""
        pipeline = [
            {"$match": {"status": "Confirmed"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]
        cursor = self.collection.aggregate(pipeline)
        async for doc in cursor:
            return doc.get("total", 0)
        return 0

    async def get_pending_total(self) -> float:
        """Get total pending sponsorship amount."""
        pipeline = [
            {"$match": {"status": {"$in": ["Pending", "In Discussion"]}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]
        cursor = self.collection.aggregate(pipeline)
        async for doc in cursor:
            return doc.get("total", 0)
        return 0

    async def get_tier_counts(self) -> dict:
        """Get counts of sponsors by tier."""
        pipeline = [
            {"$match": {"status": "Confirmed"}},
            {"$group": {"_id": "$tier", "count": {"$sum": 1}}},
        ]
        counts = {}
        cursor = self.collection.aggregate(pipeline)
        async for doc in cursor:
            counts[doc["_id"]] = doc["count"]
        return counts


class JudgeRepository(BasePartnershipRepository[JudgePartnership]):
    """Repository for judge partnerships."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.PARTNERSHIPS_JUDGES, JudgePartnership)

    async def create_indexes(self) -> None:
        """Create indexes for judges collection."""
        await super().create_indexes()
        await self.collection.create_index([("role", ASCENDING)])
        await self.collection.create_index([("expertise", ASCENDING)])

    async def find_by_role(self, role: str) -> list[JudgePartnership]:
        """Find judges by role."""
        return await self.find_many({"role": role})

    async def find_by_expertise(self, expertise: str) -> list[JudgePartnership]:
        """Find judges by area of expertise."""
        return await self.find_many({"expertise": expertise})

    async def get_confirmed_count(self) -> int:
        """Get count of confirmed judges."""
        return await self.count({"status": "Confirmed"})


class MentorRepository(BasePartnershipRepository[MentorPartnership]):
    """Repository for mentor partnerships."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.PARTNERSHIPS_MENTORS, MentorPartnership)

    async def create_indexes(self) -> None:
        """Create indexes for mentors collection."""
        await super().create_indexes()
        await self.collection.create_index([("role", ASCENDING)])
        await self.collection.create_index([("expertise", ASCENDING)])

    async def find_by_role(self, role: str) -> list[MentorPartnership]:
        """Find mentors by role."""
        return await self.find_many({"role": role})

    async def find_by_expertise(self, expertise: str) -> list[MentorPartnership]:
        """Find mentors by area of expertise."""
        return await self.find_many({"expertise": expertise})

    async def get_confirmed_count(self) -> int:
        """Get count of confirmed mentors."""
        return await self.count({"status": "Confirmed"})


class PartnershipRepository:
    """Facade for all partnership operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.sponsors = SponsorRepository(db)
        self.judges = JudgeRepository(db)
        self.mentors = MentorRepository(db)

    async def create_indexes(self) -> None:
        """Create all indexes for partnership collections."""
        await self.sponsors.create_indexes()
        await self.judges.create_indexes()
        await self.mentors.create_indexes()

    async def get_stats(self) -> dict:
        """Get aggregated partnership statistics."""
        sponsor_confirmed_total = await self.sponsors.get_confirmed_total()
        sponsor_pending_total = await self.sponsors.get_pending_total()
        sponsor_tier_counts = await self.sponsors.get_tier_counts()

        sponsor_status_counts = {}
        for status in ["Confirmed", "Pending", "In Discussion", "Lead", "Declined"]:
            sponsor_status_counts[status] = await self.sponsors.count({"status": status})

        judge_confirmed = await self.judges.get_confirmed_count()
        judge_total = await self.judges.count()

        mentor_confirmed = await self.mentors.get_confirmed_count()
        mentor_total = await self.mentors.count()

        return {
            "sponsors": {
                "total": await self.sponsors.count(),
                "confirmed": sponsor_status_counts.get("Confirmed", 0),
                "pending": sponsor_status_counts.get("Pending", 0),
                "in_discussion": sponsor_status_counts.get("In Discussion", 0),
                "leads": sponsor_status_counts.get("Lead", 0),
                "declined": sponsor_status_counts.get("Declined", 0),
                "by_tier": sponsor_tier_counts,
                "confirmed_amount": sponsor_confirmed_total,
                "pending_amount": sponsor_pending_total,
            },
            "judges": {
                "total": judge_total,
                "confirmed": judge_confirmed,
            },
            "mentors": {
                "total": mentor_total,
                "confirmed": mentor_confirmed,
            },
        }

    async def search_all(
        self,
        query: str,
        limit: int = 20,
    ) -> dict:
        """Search across all partnership types."""
        return {
            "sponsors": await self.sponsors.search(query, limit=limit),
            "judges": await self.judges.search(query, limit=limit),
            "mentors": await self.mentors.search(query, limit=limit),
        }
