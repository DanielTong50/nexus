"""
Calendly tools for Nexus.

Provides tools for scheduling meetings and managing availability.
Works without MCP by using mock data.
"""

from langchain_core.tools import tool


@tool
async def prepare_calendly_link(
    meeting_type: str = "30min",
    assignee: str = ""
) -> str:
    """Generate a Calendly scheduling link for a meeting.

    Args:
        meeting_type: Type of meeting (15min, 30min, 60min)
        assignee: Team member name (optional)

    Returns:
        Calendly link and meeting details
    """
    base_url = "https://calendly.com/nexus-events"

    duration_map = {
        "15min": "quick-chat",
        "30min": "partnership-call",
        "60min": "deep-dive",
    }

    slug = duration_map.get(meeting_type, "partnership-call")
    assignee_info = f" (with {assignee})" if assignee else ""

    return f"""Calendly Meeting Link Ready{assignee_info}:

Duration: {meeting_type}
Link: {base_url}/{slug}

Share this link with your contact to schedule a meeting."""


@tool
async def list_calendly_event_types() -> str:
    """List available Calendly event types with their scheduling URLs.

    Returns:
        List of event types with URLs
    """
    return """Available Calendly event types:

- Quick Chat (15 min): https://calendly.com/nexus-events/quick-chat
- Partnership Call (30 min): https://calendly.com/nexus-events/partnership-call
- Deep Dive (60 min): https://calendly.com/nexus-events/deep-dive
- Team Sync (45 min): https://calendly.com/nexus-events/team-sync"""


@tool
async def check_availability(date: str) -> str:
    """Check available time slots for a given date.

    Args:
        date: Date to check (YYYY-MM-DD format)

    Returns:
        Available time slots
    """
    return f"""Available slots for {date}:

Morning:
- 9:00 AM - 9:30 AM
- 10:00 AM - 10:30 AM
- 11:00 AM - 11:30 AM

Afternoon:
- 2:00 PM - 2:30 PM
- 3:30 PM - 4:00 PM
- 4:30 PM - 5:00 PM

All times in your local timezone."""


# Export all tools for agent binding
CALENDLY_TOOLS = [
    prepare_calendly_link,
    list_calendly_event_types,
    check_availability,
]
