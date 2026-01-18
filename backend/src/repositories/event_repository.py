"""Repository for event logistics and room bookings."""

from datetime import date, datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.models.event import (
    EventLogistics,
    RoomBooking,
    LogisticsTask,
    ScheduleItem,
)
from src.repositories.base import BaseRepository
from src.services.database import Collections


class EventLogisticsRepository(BaseRepository[EventLogistics]):
    """Repository for event logistics."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.EVENT_LOGISTICS, EventLogistics)

    async def create_indexes(self) -> None:
        """Create indexes for event logistics collection."""
        await self.collection.create_index([("event_name", ASCENDING)], unique=True)
        await self.collection.create_index([("event_date", ASCENDING)])
        await self.collection.create_index([("status", ASCENDING)])

    async def find_by_event_name(self, event_name: str) -> Optional[EventLogistics]:
        """Find event logistics by event name."""
        return await self.find_one({"event_name": event_name})

    async def find_upcoming(self, limit: int = 10) -> list[EventLogistics]:
        """Find upcoming events."""
        today = date.today()
        return await self.find_many(
            {"event_date": {"$gte": today}, "status": {"$ne": "cancelled"}},
            sort=[("event_date", ASCENDING)],
            limit=limit,
        )

    async def update_venue(
        self,
        event_name: str,
        venue_data: dict,
    ) -> Optional[EventLogistics]:
        """Update venue information for an event."""
        return await self.update_one(
            {"event_name": event_name},
            {"venue": venue_data},
        )

    async def update_schedule(
        self,
        event_name: str,
        schedule: list[dict],
    ) -> Optional[EventLogistics]:
        """Update schedule for an event."""
        return await self.update_one(
            {"event_name": event_name},
            {"schedule": schedule},
        )

    async def update_catering(
        self,
        event_name: str,
        catering_data: dict,
    ) -> Optional[EventLogistics]:
        """Update catering information for an event."""
        return await self.update_one(
            {"event_name": event_name},
            {"catering": catering_data},
        )

    async def update_equipment(
        self,
        event_name: str,
        equipment: dict,
    ) -> Optional[EventLogistics]:
        """Update equipment inventory for an event."""
        return await self.update_one(
            {"event_name": event_name},
            {"equipment": equipment},
        )

    async def update_attendance(
        self,
        event_name: str,
        registered: Optional[int] = None,
        checked_in: Optional[int] = None,
    ) -> Optional[EventLogistics]:
        """Update attendance counts for an event."""
        update_data = {}
        if registered is not None:
            update_data["registered_attendees"] = registered
        if checked_in is not None:
            update_data["checked_in_attendees"] = checked_in

        if not update_data:
            return None

        return await self.update_one({"event_name": event_name}, update_data)


class RoomBookingRepository(BaseRepository[RoomBooking]):
    """Repository for room bookings."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.ROOM_BOOKINGS, RoomBooking)

    async def create_indexes(self) -> None:
        """Create indexes for room bookings collection."""
        await self.collection.create_index(
            [("event_name", ASCENDING), ("date", ASCENDING), ("room_name", ASCENDING)]
        )
        await self.collection.create_index([("status", ASCENDING)])
        await self.collection.create_index([("date", ASCENDING)])

    async def find_by_event(
        self,
        event_name: str,
        date_filter: Optional[date] = None,
    ) -> list[RoomBooking]:
        """Find room bookings for an event."""
        query = {"event_name": event_name}
        if date_filter:
            query["booking_date"] = date_filter
        return await self.find_many(query, sort=[("booking_date", ASCENDING), ("start_time", ASCENDING)])

    async def find_by_room(
        self,
        room_name: str,
        date_filter: Optional[date] = None,
    ) -> list[RoomBooking]:
        """Find bookings for a specific room."""
        query = {"room_name": room_name}
        if date_filter:
            query["booking_date"] = date_filter
        return await self.find_many(query, sort=[("booking_date", ASCENDING), ("start_time", ASCENDING)])

    async def check_availability(
        self,
        room_name: str,
        booking_date: date,
        start_time: str,
        end_time: str,
    ) -> bool:
        """Check if a room is available for a time slot."""
        existing = await self.find_many(
            {
                "room_name": room_name,
                "booking_date": booking_date,
                "status": {"$ne": "cancelled"},
                "$or": [
                    {"start_time": {"$lt": end_time}, "end_time": {"$gt": start_time}},
                ],
            }
        )
        return len(existing) == 0

    async def confirm_booking(self, booking_id: str, confirmed_by: str) -> Optional[RoomBooking]:
        """Confirm a room booking."""
        return await self.update_by_id(
            booking_id,
            {"status": "confirmed", "confirmed_by": confirmed_by},
        )

    async def cancel_booking(self, booking_id: str) -> Optional[RoomBooking]:
        """Cancel a room booking."""
        return await self.update_by_id(booking_id, {"status": "cancelled"})


class LogisticsTaskRepository(BaseRepository[LogisticsTask]):
    """Repository for logistics tasks."""

    def __init__(self, db: AsyncIOMotorDatabase):
        # Using a generic collection name since it's not in Collections enum
        super().__init__(db, "logistics_tasks", LogisticsTask)

    async def create_indexes(self) -> None:
        """Create indexes for logistics tasks collection."""
        await self.collection.create_index([("event_name", ASCENDING)])
        await self.collection.create_index([("status", ASCENDING)])
        await self.collection.create_index([("assigned_to", ASCENDING)])
        await self.collection.create_index([("due_date", ASCENDING)])
        await self.collection.create_index([("category", ASCENDING)])

    async def find_by_event(
        self,
        event_name: str,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> list[LogisticsTask]:
        """Find tasks for an event."""
        query = {"event_name": event_name}
        if status:
            query["status"] = status
        if category:
            query["category"] = category
        return await self.find_many(query, sort=[("due_date", ASCENDING)])

    async def find_by_assignee(
        self,
        assigned_to: str,
        status: Optional[str] = None,
    ) -> list[LogisticsTask]:
        """Find tasks assigned to a person."""
        query = {"assigned_to": assigned_to}
        if status:
            query["status"] = status
        return await self.find_many(query, sort=[("due_date", ASCENDING)])

    async def find_overdue(self, event_name: Optional[str] = None) -> list[LogisticsTask]:
        """Find overdue tasks."""
        query = {
            "status": {"$nin": ["completed", "blocked"]},
            "due_date": {"$lt": datetime.utcnow()},
        }
        if event_name:
            query["event_name"] = event_name
        return await self.find_many(query, sort=[("due_date", ASCENDING)])

    async def complete_task(self, task_id: str) -> Optional[LogisticsTask]:
        """Mark a task as completed."""
        return await self.update_by_id(
            task_id,
            {"status": "completed", "completed_at": datetime.utcnow()},
        )

    async def assign_task(self, task_id: str, assigned_to: str) -> Optional[LogisticsTask]:
        """Assign a task to someone."""
        return await self.update_by_id(task_id, {"assigned_to": assigned_to})


class EventRepository:
    """Facade for all event-related operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.logistics = EventLogisticsRepository(db)
        self.bookings = RoomBookingRepository(db)
        self.tasks = LogisticsTaskRepository(db)

    async def create_indexes(self) -> None:
        """Create all indexes for event collections."""
        await self.logistics.create_indexes()
        await self.bookings.create_indexes()
        await self.tasks.create_indexes()

    async def get_event_summary(self, event_name: str) -> dict:
        """Get a complete summary of an event."""
        logistics = await self.logistics.find_by_event_name(event_name)
        bookings = await self.bookings.find_by_event(event_name)
        tasks = await self.tasks.find_by_event(event_name)

        pending_tasks = [t for t in tasks if t.status == "pending"]
        in_progress_tasks = [t for t in tasks if t.status == "in_progress"]
        completed_tasks = [t for t in tasks if t.status == "completed"]

        return {
            "logistics": logistics.model_dump() if logistics else None,
            "bookings": [b.model_dump() for b in bookings],
            "tasks": {
                "total": len(tasks),
                "pending": len(pending_tasks),
                "in_progress": len(in_progress_tasks),
                "completed": len(completed_tasks),
                "items": [t.model_dump() for t in tasks],
            },
        }
