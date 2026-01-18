"""Event logistics and room booking models."""

import datetime as dt
from typing import Literal, Optional

from pydantic import Field

from src.models.base import BaseDocument


class RoomBooking(BaseDocument):
    """MongoDB document for room bookings."""

    event_name: str = Field(description="Event this booking is for")
    room_name: str = Field(description="Name of the room")
    booking_date: dt.date = Field(description="Booking date")
    start_time: str = Field(description="Booking start time (e.g., '09:00')")
    end_time: str = Field(description="Booking end time (e.g., '17:00')")
    purpose: str = Field(description="Purpose of the booking")
    capacity: Optional[int] = Field(default=None, description="Room capacity")
    status: Literal["pending", "confirmed", "cancelled"] = Field(
        default="pending", description="Booking status"
    )
    requested_by: Optional[str] = Field(default=None, description="Who requested the booking")
    confirmed_by: Optional[str] = Field(default=None, description="Who confirmed the booking")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    equipment_needed: list[str] = Field(
        default_factory=list, description="Required equipment"
    )


class LogisticsTask(BaseDocument):
    """MongoDB document for logistics tasks."""

    event_name: str = Field(description="Event this task belongs to")
    title: str = Field(description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    category: Literal[
        "venue",
        "catering",
        "equipment",
        "volunteers",
        "swag",
        "signage",
        "sponsors",
        "other",
    ] = Field(default="other", description="Task category")
    status: Literal["pending", "in_progress", "completed", "blocked"] = Field(
        default="pending", description="Task status"
    )
    priority: Literal["low", "medium", "high", "urgent"] = Field(
        default="medium", description="Task priority"
    )
    assigned_to: Optional[str] = Field(default=None, description="Person assigned")
    due_date: Optional[dt.datetime] = Field(default=None, description="Due date")
    completed_at: Optional[dt.datetime] = Field(default=None, description="Completion date")
    dependencies: list[str] = Field(
        default_factory=list, description="IDs of dependent tasks"
    )
    notes: Optional[str] = Field(default=None, description="Additional notes")


class VenueInfo(BaseDocument):
    """Venue information embedded in EventLogistics."""

    name: str = Field(description="Venue name")
    address: Optional[str] = Field(default=None, description="Venue address")
    capacity: int = Field(description="Venue capacity")
    contact_name: Optional[str] = Field(default=None, description="Venue contact person")
    contact_email: Optional[str] = Field(default=None, description="Venue contact email")
    contact_phone: Optional[str] = Field(default=None, description="Venue contact phone")
    status: Literal["pending", "confirmed", "cancelled"] = Field(
        default="pending", description="Venue booking status"
    )
    setup_time: Optional[str] = Field(default=None, description="Setup time window")
    teardown_time: Optional[str] = Field(default=None, description="Teardown time window")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class CateringInfo(BaseDocument):
    """Catering information embedded in EventLogistics."""

    provider: Optional[str] = Field(default=None, description="Catering provider")
    contact_email: Optional[str] = Field(default=None, description="Provider contact")
    status: Literal["pending", "confirmed", "cancelled"] = Field(
        default="pending", description="Catering status"
    )
    menu: dict = Field(
        default_factory=dict,
        description="Menu by meal (e.g., {'breakfast': {...}, 'lunch': {...}})",
    )
    dietary_requirements: dict = Field(
        default_factory=dict,
        description="Dietary counts (e.g., {'vegetarian': 50, 'vegan': 20})",
    )
    headcount: int = Field(default=0, description="Expected headcount")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class ScheduleItem(BaseDocument):
    """Schedule item embedded in EventLogistics."""

    name: str = Field(description="Activity name")
    start_time: str = Field(description="Start time (e.g., '09:00 AM')")
    end_time: str = Field(description="End time (e.g., '10:00 AM')")
    location: Optional[str] = Field(default=None, description="Location/room")
    description: Optional[str] = Field(default=None, description="Activity description")
    type: Literal[
        "ceremony",
        "workshop",
        "networking",
        "meal",
        "judging",
        "hacking",
        "break",
        "other",
    ] = Field(default="other", description="Activity type")
    host: Optional[str] = Field(default=None, description="Host/speaker")


class EventLogistics(BaseDocument):
    """MongoDB document for complete event logistics."""

    event_name: str = Field(description="Event name (unique identifier)")
    event_date: dt.date = Field(description="Event date")
    event_type: Literal["hackathon", "workshop", "conference", "meetup", "other"] = Field(
        default="hackathon", description="Type of event"
    )
    status: Literal["planning", "confirmed", "in_progress", "completed", "cancelled"] = Field(
        default="planning", description="Event status"
    )

    # Venue
    venue: Optional[VenueInfo] = Field(default=None, description="Venue information")

    # Schedule
    schedule: list[ScheduleItem] = Field(
        default_factory=list, description="Event schedule"
    )

    # Catering
    catering: Optional[CateringInfo] = Field(default=None, description="Catering information")

    # Equipment
    equipment: dict = Field(
        default_factory=dict,
        description="Equipment inventory (e.g., {'projectors': {'count': 5, 'status': 'confirmed'}})",
    )

    # Volunteers
    volunteer_count: int = Field(default=0, description="Number of volunteers")
    volunteer_roles: list[dict] = Field(
        default_factory=list,
        description="Volunteer roles and assignments",
    )

    # Attendance
    expected_attendees: int = Field(default=0, description="Expected attendee count")
    registered_attendees: int = Field(default=0, description="Registered attendees")
    checked_in_attendees: int = Field(default=0, description="Checked-in attendees")

    # Team assignments
    organizers: list[str] = Field(default_factory=list, description="Organizer user IDs")
    leads: dict = Field(
        default_factory=dict,
        description="Team leads by area (e.g., {'logistics': 'user_id', 'sponsors': 'user_id'})",
    )

    # Notes and links
    notes: Optional[str] = Field(default=None, description="General notes")
    important_links: dict = Field(
        default_factory=dict,
        description="Important links (e.g., {'registration': '...', 'devpost': '...'})",
    )
