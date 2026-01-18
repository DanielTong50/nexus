"""
Tool schemas for all agent tools.

Defines Pydantic models for tool input validation and documentation.
All tools use LangChain's @tool decorator - these schemas provide
structured input validation.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


# =============================================================================
# Partnership Tools Schemas
# =============================================================================

class SearchPartnershipSheetInput(BaseModel):
    """Input for searching partnership sheet."""
    event_name: str = Field(..., description="Name of the event (e.g., 'Blueprint')")
    category: Literal["Sponsors", "Judges", "Mentors", "StudentMentors"] = Field(
        ..., description="Category of partners to search"
    )


class DraftLinkedInOutreachInput(BaseModel):
    """Input for drafting LinkedIn outreach message."""
    profile_url: str = Field(..., description="LinkedIn profile URL of the recipient")
    template: str = Field(..., description="Template name or content for the message")


class DraftEmailOutreachInput(BaseModel):
    """Input for drafting email outreach."""
    recipient: str = Field(..., description="Email address of recipient")
    template: str = Field(..., description="Template name or content")
    event_name: str = Field(..., description="Name of the event")


class LogPartnershipStatusInput(BaseModel):
    """Input for logging partnership status."""
    event_name: str = Field(..., description="Name of the event")
    partner_name: str = Field(..., description="Company or person name")
    category: Literal["Sponsors", "Judges", "Mentors", "StudentMentors"] = Field(
        ..., description="Category of partner"
    )
    status: Literal["pending", "verbal confirmation", "secured", "rejected"] = Field(
        ..., description="Current status of the partnership"
    )


class PrepareCalendlyLinkInput(BaseModel):
    """Input for preparing Calendly link."""
    assignee: str = Field(..., description="Team member to assign meeting to")
    meeting_type: str = Field(..., description="Type of meeting (e.g., 'sponsor_call', 'mentor_intro')")


# =============================================================================
# Marketing Tools Schemas
# =============================================================================

class CreateContentTimelineInput(BaseModel):
    """Input for creating content timeline."""
    event_name: str = Field(..., description="Name of the event")
    launch_date: str = Field(..., description="Event launch date in YYYY-MM-DD format")


class DraftSocialPostInput(BaseModel):
    """Input for drafting social media post."""
    platform: Literal["instagram", "linkedin"] = Field(..., description="Target platform")
    topic: str = Field(..., description="Topic or theme for the post")
    campaign_name: str = Field(..., description="Name of the marketing campaign")


class CheckFigmaAssetInput(BaseModel):
    """Input for checking Figma asset status."""
    file_id: str = Field(..., description="Figma file ID to check")


class ScheduleInstagramPostInput(BaseModel):
    """Input for scheduling Instagram post."""
    content: str = Field(..., description="Post caption")
    image_url: str = Field(..., description="URL of the image to post")
    publish_time: str = Field(..., description="Scheduled publish time in ISO format")


class ScheduleLinkedInPostInput(BaseModel):
    """Input for scheduling LinkedIn post."""
    content: str = Field(..., description="Post content")
    publish_time: str = Field(..., description="Scheduled publish time in ISO format")


class UpdateSponsorInContentInput(BaseModel):
    """Input for updating sponsor in marketing content."""
    event_name: str = Field(..., description="Name of the event")
    sponsor_name: str = Field(..., description="Name of the sponsor")
    tier: Literal["platinum", "gold", "silver", "bronze"] = Field(
        ..., description="Sponsorship tier"
    )


# =============================================================================
# Finance Tools Schemas
# =============================================================================

class DraftMOUInput(BaseModel):
    """Input for drafting MOU."""
    sponsor_name: str = Field(..., description="Name of the sponsor")
    amount: float = Field(..., description="Sponsorship amount in dollars")
    deliverables: str = Field(..., description="Comma-separated list of deliverables")


class GenerateInvoiceInput(BaseModel):
    """Input for generating invoice."""
    sponsor_name: str = Field(..., description="Name of the sponsor")
    amount: float = Field(..., description="Invoice amount in dollars")
    due_date: str = Field(..., description="Due date in YYYY-MM-DD format")


class UpdateBudgetSheetInput(BaseModel):
    """Input for updating budget sheet."""
    event_name: str = Field(..., description="Name of the event")
    category: str = Field(..., description="Budget category (e.g., 'venue', 'food', 'prizes')")
    amount: float = Field(..., description="Amount in dollars")
    type: Literal["income", "expense"] = Field(..., description="Type of transaction")


class CheckBudgetStatusInput(BaseModel):
    """Input for checking budget status."""
    event_name: str = Field(..., description="Name of the event")


# =============================================================================
# Events Tools Schemas
# =============================================================================

class SendAvailabilityPollInput(BaseModel):
    """Input for sending availability poll."""
    attendees: list[str] = Field(..., description="List of attendee names or emails")
    duration: str = Field(..., description="Meeting duration (e.g., '1h', '30m')")
    date_range: str = Field(..., description="Date range for poll (e.g., 'Jan 20-25')")
    slack_channel: str = Field(..., description="Slack channel to post poll to")


class UpdateLogisticsSheetInput(BaseModel):
    """Input for updating logistics sheet."""
    event_name: str = Field(..., description="Name of the event")
    category: Literal["venue", "food", "schedule", "equipment", "boothing"] = Field(
        ..., description="Logistics category"
    )
    details: str = Field(..., description="Details to update")


class CreateRoomBookingRequestInput(BaseModel):
    """Input for creating room booking request."""
    building: str = Field(..., description="Building name")
    room: str = Field(..., description="Room number or name")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(..., description="Time range (e.g., '9:00-17:00')")


class SendTeamReminderInput(BaseModel):
    """Input for sending team reminder."""
    team: str = Field(..., description="Team name (e.g., 'partnerships', 'logistics')")
    message: str = Field(..., description="Reminder message")


class AnnounceToSlackInput(BaseModel):
    """Input for announcing to Slack."""
    channel: str = Field(..., description="Slack channel name")
    message: str = Field(..., description="Announcement message")
    mention_team: Optional[bool] = Field(False, description="Whether to @channel")


# =============================================================================
# Developers Tools Schemas
# =============================================================================

class CreateGitHubIssueInput(BaseModel):
    """Input for creating GitHub issue."""
    repo: str = Field(..., description="Repository name (e.g., 'nexus-app')")
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description in markdown")
    labels: list[str] = Field(default_factory=list, description="Issue labels")


class CheckPRStatusInput(BaseModel):
    """Input for checking PR status."""
    repo: str = Field(..., description="Repository name")


class GetRepoUpdatesInput(BaseModel):
    """Input for getting repo updates."""
    repo: str = Field(..., description="Repository name")
    days: int = Field(7, description="Number of days to look back")


class AssignIssueInput(BaseModel):
    """Input for assigning issue."""
    repo: str = Field(..., description="Repository name")
    issue_number: int = Field(..., description="Issue number")
    assignee: str = Field(..., description="GitHub username to assign")


# =============================================================================
# HITL (Human-in-the-Loop) Actions Registry
# =============================================================================

# Actions that require human approval before execution
HITL_REQUIRED_ACTIONS = {
    "draft_mou",
    "generate_invoice",
    "schedule_instagram_post",
    "schedule_linkedin_post",
    "announce_to_slack",
    "create_room_booking_request",
}

# Actions that should notify but not block
HITL_NOTIFY_ACTIONS = {
    "log_partnership_status",
    "update_budget_sheet",
    "update_logistics_sheet",
}
