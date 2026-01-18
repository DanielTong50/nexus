"""
Events tools for Nexus.

Provides tools for event logistics, scheduling, and coordination.
"""

from langchain_core.tools import tool


@tool
async def get_logistics_summary(event_name: str = "Blueprint") -> str:
    """Get a summary of event logistics.

    Args:
        event_name: Name of the event

    Returns:
        Logistics summary
    """
    return f"""Logistics Summary - {event_name}:

Venue:
- Location: Tech Campus Building A
- Capacity: 500 attendees
- Status: Confirmed
- Setup: Day before, 2pm-8pm

Schedule:
- Check-in: 8:00 AM
- Opening: 9:00 AM
- Workshops: 10:00 AM - 5:00 PM
- Closing: 6:00 PM

Catering:
- Breakfast: 8:00 AM (light)
- Lunch: 12:00 PM (boxed)
- Snacks: 3:00 PM
- Dinner: Not included

Equipment:
- Projectors: 5 (confirmed)
- Microphones: 10 (confirmed)
- Extension cords: 50 (pending)"""


@tool
async def update_logistics_sheet(
    category: str,
    item: str,
    status: str,
    notes: str = ""
) -> str:
    """Update an item in the logistics sheet.

    Args:
        category: Category (venue, catering, equipment, etc.)
        item: Specific item
        status: New status
        notes: Additional notes

    Returns:
        Confirmation
    """
    return f"""Logistics Updated:

Category: {category.title()}
Item: {item}
Status: {status}
Notes: {notes or 'N/A'}

The logistics sheet has been updated."""


@tool
async def generate_event_schedule(
    event_name: str,
    start_time: str,
    end_time: str,
    include_breaks: bool = True
) -> str:
    """Generate a detailed event schedule.

    Args:
        event_name: Name of the event
        start_time: Event start time
        end_time: Event end time
        include_breaks: Whether to include breaks

    Returns:
        Generated schedule
    """
    return f"""Event Schedule - {event_name}:

{start_time} - Registration & Check-in
{start_time} + 1h - Opening Ceremony
{start_time} + 1.5h - Keynote Speaker
{start_time} + 2.5h - Break & Networking
{start_time} + 3h - Workshop Session 1
{start_time} + 4.5h - Lunch Break
{start_time} + 5.5h - Workshop Session 2
{start_time} + 7h - Break
{start_time} + 7.5h - Panel Discussion
{end_time} - 30m - Closing Ceremony
{end_time} - Event Ends

Note: This is a template. Adjust times based on actual start/end."""


@tool
async def send_team_reminder(
    team: str,
    message: str,
    urgency: str = "normal"
) -> str:
    """Send a reminder to a team.

    Args:
        team: Team name (logistics, marketing, etc.)
        message: Reminder message
        urgency: Urgency level (low, normal, high)

    Returns:
        Confirmation
    """
    return f"""Team Reminder Sent:

To: {team.title()} Team
Urgency: {urgency.upper()}
Message: {message}

Notification has been sent via Slack and email."""


@tool
async def create_room_booking_request(
    room_name: str,
    date: str,
    start_time: str,
    end_time: str,
    purpose: str
) -> str:
    """Create a room booking request.

    Args:
        room_name: Name of the room
        date: Date needed
        start_time: Start time
        end_time: End time
        purpose: Purpose of booking

    Returns:
        Booking request confirmation
    """
    return f"""Room Booking Request Created:

Room: {room_name}
Date: {date}
Time: {start_time} - {end_time}
Purpose: {purpose}

Request has been submitted to facilities.
Expected response: 24-48 hours."""


@tool
async def send_availability_poll(
    recipients: str,
    dates: str,
    purpose: str
) -> str:
    """Send an availability poll to team members.

    Args:
        recipients: Who to send to (comma-separated or team name)
        dates: Date options
        purpose: What the poll is for

    Returns:
        Confirmation
    """
    return f"""Availability Poll Created:

Recipients: {recipients}
Date Options: {dates}
Purpose: {purpose}

Poll has been sent. Responses will be collected for 48 hours."""


@tool
async def announce_to_slack(
    channel: str,
    message: str,
    mention: str = ""
) -> str:
    """Post an announcement to a Slack channel (requires approval).

    Args:
        channel: Slack channel name
        message: Announcement message
        mention: Who to mention (@here, @channel, specific users)

    Returns:
        Confirmation
    """
    return f"""[PENDING APPROVAL] Slack Announcement:

Channel: #{channel}
Mention: {mention or 'None'}
Message:
{message}

This announcement requires your approval before posting."""


EVENTS_TOOLS = [
    get_logistics_summary,
    update_logistics_sheet,
    generate_event_schedule,
    send_team_reminder,
    create_room_booking_request,
    send_availability_poll,
    announce_to_slack,
]
