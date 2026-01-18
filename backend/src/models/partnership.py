"""Partnership models for sponsors, judges, and mentors."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import Field

from src.models.base import BaseDocument


class PartnershipBase(BaseDocument):
    """Base model for all partnership types."""

    company: str = Field(description="Company/organization name")
    contact_name: str = Field(description="Primary contact name")
    contact_email: str = Field(description="Primary contact email")
    contact_position: Optional[str] = Field(default=None, description="Contact's job title")
    status: Literal[
        "Lead",
        "Contacted",
        "In Discussion",
        "Pending",
        "Confirmed",
        "Declined",
        "Withdrawn",
    ] = Field(default="Lead", description="Current partnership status")
    notes: Optional[str] = Field(default=None, description="Additional notes")

    # Sync metadata for Google Sheets integration
    sheets_row_number: Optional[int] = Field(
        default=None, description="Row number in Google Sheets"
    )
    last_synced_at: Optional[datetime] = Field(
        default=None, description="Last sync with Google Sheets"
    )
    sync_status: Literal["synced", "pending", "conflict"] = Field(
        default="pending", description="Sync status with Google Sheets"
    )

    # Activity tracking
    last_contacted_at: Optional[datetime] = Field(
        default=None, description="Last contact date"
    )
    follow_up_date: Optional[datetime] = Field(
        default=None, description="Scheduled follow-up date"
    )

    def needs_sync(self) -> bool:
        """Check if this record needs to be synced to Google Sheets."""
        if not self.last_synced_at:
            return True
        return self.updated_at > self.last_synced_at


class SponsorPartnership(PartnershipBase):
    """MongoDB document for sponsor partnerships."""

    tier: Literal[
        "Platinum Sponsor",
        "Gold Sponsor",
        "Silver Sponsor",
        "Bronze Sponsor",
        "In-Kind Sponsor",
        "Boothing Company",
        "TBD",
    ] = Field(default="TBD", description="Sponsorship tier")
    amount: Optional[float] = Field(default=None, description="Sponsorship amount in USD")
    benefits: list[str] = Field(
        default_factory=list, description="List of sponsor benefits"
    )
    payment_status: Literal["pending", "invoiced", "paid", "cancelled"] = Field(
        default="pending", description="Payment status"
    )
    payment_date: Optional[datetime] = Field(default=None, description="Payment received date")
    mou_status: Literal["not_started", "drafted", "sent", "signed"] = Field(
        default="not_started", description="MOU status"
    )
    mou_signed_date: Optional[datetime] = Field(default=None, description="MOU signed date")

    # Logo and branding
    logo_url: Optional[str] = Field(default=None, description="Company logo URL")
    website: Optional[str] = Field(default=None, description="Company website")
    social_handles: dict = Field(
        default_factory=dict, description="Social media handles (e.g., {'linkedin': '...'})"
    )

    @property
    def tier_amount(self) -> float:
        """Get the standard amount for this tier."""
        tier_amounts = {
            "Platinum Sponsor": 25000,
            "Gold Sponsor": 15000,
            "Silver Sponsor": 5000,
            "Bronze Sponsor": 2500,
            "In-Kind Sponsor": 0,
            "Boothing Company": 0,
            "TBD": 0,
        }
        return tier_amounts.get(self.tier, 0)


class JudgePartnership(PartnershipBase):
    """MongoDB document for judge partnerships."""

    role: Literal["Lead Judge", "Technical Judge", "Industry Judge", "Student Judge"] = Field(
        default="Technical Judge", description="Judging role"
    )
    expertise: list[str] = Field(
        default_factory=list, description="Areas of expertise"
    )
    availability: Optional[str] = Field(default=None, description="Availability notes")
    judging_slots: list[str] = Field(
        default_factory=list, description="Assigned judging time slots"
    )
    bio: Optional[str] = Field(default=None, description="Judge bio for program")
    headshot_url: Optional[str] = Field(default=None, description="Headshot URL")


class MentorPartnership(PartnershipBase):
    """MongoDB document for mentor partnerships."""

    role: Literal["Technical Mentor", "Design Mentor", "Business Mentor", "General Mentor"] = Field(
        default="General Mentor", description="Mentoring role"
    )
    expertise: list[str] = Field(
        default_factory=list, description="Areas of expertise"
    )
    availability: Optional[str] = Field(default=None, description="Availability notes")
    mentoring_slots: list[str] = Field(
        default_factory=list, description="Assigned mentoring time slots"
    )
    bio: Optional[str] = Field(default=None, description="Mentor bio for program")
    headshot_url: Optional[str] = Field(default=None, description="Headshot URL")
    max_teams: int = Field(default=3, description="Maximum teams to mentor")


class PartnershipStats(BaseDocument):
    """Aggregated partnership statistics."""

    event_name: str = Field(description="Event these stats are for")
    sponsor_stats: dict = Field(
        default_factory=dict,
        description="Sponsor counts by tier and status",
    )
    judge_stats: dict = Field(
        default_factory=dict,
        description="Judge counts by role and status",
    )
    mentor_stats: dict = Field(
        default_factory=dict,
        description="Mentor counts by role and status",
    )
    total_sponsorship_confirmed: float = Field(default=0)
    total_sponsorship_pending: float = Field(default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
