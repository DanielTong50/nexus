"""
Events tools for Nexus.

Provides tools for event logistics, scheduling, and coordination.
Uses MongoDB for data storage and Slack SDK for messaging.
"""

import logging
from langchain_core.tools import tool

from config.settings import settings
from src.services.database import db_service

logger = logging.getLogger(__name__)

# Slack client (initialized lazily)
_slack_client = None


def _get_slack_client():
    """Initialize and return Slack WebClient."""
    global _slack_client

    if _slack_client is not None:
        return _slack_client

    if not settings.slack_bot_token:
        logger.warning("Slack bot token not configured")
        return None

    try:
        from slack_sdk import WebClient
        _slack_client = WebClient(token=settings.slack_bot_token)
        logger.info("Slack client initialized")
        return _slack_client
    except ImportError:
        logger.error("slack_sdk not installed. Run: pip install slack_sdk")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Slack client: {e}")
        return None


async def _post_to_slack(channel: str, message: str, mention_channel: bool = False) -> dict:
    """Post a message to Slack.

    Args:
        channel: Channel name (with or without #)
        message: Message text
        mention_channel: Whether to @channel

    Returns:
        Result dict with success status
    """
    client = _get_slack_client()
    if not client:
        return {"success": False, "error": "Slack not configured"}

    try:
        # Normalize channel name
        channel_name = channel.lstrip("#")

        # Add @channel if requested
        if mention_channel:
            message = f"<!channel> {message}"

        response = client.chat_postMessage(
            channel=channel_name,
            text=message
        )

        return {
            "success": True,
            "channel": response["channel"],
            "ts": response["ts"],
            "message": f"Posted to #{channel_name}"
        }
    except Exception as e:
        logger.error(f"Slack post failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_logistics_from_mongodb(event_name: str) -> dict:
    """Fetch logistics data from MongoDB.

    Args:
        event_name: Name of the event

    Returns:
        Logistics data dictionary
    """
    try:
        collection = db_service.db["event_logistics"]
        data = await collection.find_one({"event_name": event_name})
        return data or {}
    except Exception as e:
        logger.error(f"Failed to read logistics from MongoDB: {e}")
        return {}


@tool
async def get_logistics_summary(event_name: str = "Blueprint") -> str:
    """Get a summary of event logistics.

    Args:
        event_name: Name of the event

    Returns:
        Logistics summary
    """
    # Try to get from MongoDB first
    data = await _get_logistics_from_mongodb(event_name)

    if data and any(key in data for key in ["venue", "schedule", "catering", "equipment"]):
        venue = data.get("venue", {})
        schedule = data.get("schedule", {})
        catering = data.get("catering", {})
        equipment = data.get("equipment", {})

        venue_str = "\n".join([f"- {k}: {v}" for k, v in venue.items()]) if venue else "- Not configured"
        schedule_str = "\n".join([f"- {k}: {v}" for k, v in schedule.items()]) if schedule else "- Not configured"
        catering_str = "\n".join([f"- {k}: {v}" for k, v in catering.items()]) if catering else "- Not configured"
        equipment_str = "\n".join([f"- {k}: {v}" for k, v in equipment.items()]) if equipment else "- Not configured"

        return f"""Logistics Summary - {event_name}:

Venue:
{venue_str}

Schedule:
{schedule_str}

Catering:
{catering_str}

Equipment:
{equipment_str}"""

    # Return default template if no data in MongoDB
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
- Extension cords: 50 (pending)

Note: No custom logistics data found. Use update_logistics_sheet to configure."""


@tool
async def update_logistics_sheet(
    category: str,
    item: str,
    status: str,
    notes: str = "",
    event_name: str = "Blueprint"
) -> str:
    """Update an item in the logistics sheet.

    Args:
        category: Category (venue, catering, equipment, etc.)
        item: Specific item
        status: New status
        notes: Additional notes
        event_name: Event name (default: Blueprint)

    Returns:
        Confirmation
    """
    # Save to MongoDB
    try:
        collection = db_service.db["event_logistics"]

        update_data = {
            f"{category.lower()}.{item}": {
                "status": status,
                "notes": notes
            }
        }

        await collection.update_one(
            {"event_name": event_name},
            {"$set": update_data},
            upsert=True
        )

        return f"""Logistics Updated:

Category: {category.title()}
Item: {item}
Status: {status}
Notes: {notes or 'N/A'}

The logistics sheet has been updated in the database."""

    except Exception as e:
        logger.error(f"Failed to update logistics: {e}")
        return f"Error updating logistics: {str(e)}"


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
    schedule = f"""Event Schedule - {event_name}:

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

    # Save to MongoDB
    try:
        collection = db_service.db["event_logistics"]
        await collection.update_one(
            {"event_name": event_name},
            {"$set": {
                "schedule": {
                    "start_time": start_time,
                    "end_time": end_time,
                    "include_breaks": include_breaks
                }
            }},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Failed to save schedule: {e}")

    return schedule


@tool
async def send_team_reminder(
    team: str,
    message: str,
    urgency: str = "normal"
) -> str:
    """Send a reminder to a team via Slack.

    Args:
        team: Team name (logistics, marketing, etc.)
        message: Reminder message
        urgency: Urgency level (low, normal, high)

    Returns:
        Confirmation
    """
    channel = f"#{team}"
    urgency_prefix = {"low": "", "normal": "*Reminder*\n", "high": "*URGENT REMINDER*\n"}
    formatted_message = f"{urgency_prefix.get(urgency, '')}{message}"

    # Try to send via Slack
    if settings.slack_bot_token:
        result = await _post_to_slack(channel, formatted_message)

        if result.get("success"):
            return f"""Team Reminder Sent:

To: {team.title()} Team ({channel})
Urgency: {urgency.upper()}
Message: {message}

Notification has been sent via Slack."""
        else:
            return f"""Failed to send reminder to Slack: {result.get('error')}

Reminder was NOT sent. Please check:
1. Bot is invited to {channel}
2. Channel name is correct"""

    # Fallback - just log it
    return f"""Team Reminder (NOT SENT - Slack not configured):

To: {team.title()} Team
Urgency: {urgency.upper()}
Message: {message}

Configure SLACK_BOT_TOKEN to enable Slack notifications."""


@tool
async def create_room_booking_request(
    room_name: str,
    date: str,
    start_time: str,
    end_time: str,
    purpose: str,
    event_name: str = "Blueprint"
) -> str:
    """Create a room booking request.

    Args:
        room_name: Name of the room
        date: Date needed
        start_time: Start time
        end_time: End time
        purpose: Purpose of booking
        event_name: Event name (default: Blueprint)

    Returns:
        Booking request confirmation
    """
    # Save to MongoDB
    try:
        collection = db_service.db["room_bookings"]
        booking = {
            "event_name": event_name,
            "room_name": room_name,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "purpose": purpose,
            "status": "pending"
        }
        await collection.insert_one(booking)
    except Exception as e:
        logger.error(f"Failed to save booking: {e}")

    return f"""[PENDING APPROVAL] Room Booking Request Created:

Room: {room_name}
Date: {date}
Time: {start_time} - {end_time}
Purpose: {purpose}

Request has been submitted to facilities.
Expected response: 24-48 hours.

This booking requires your approval."""


@tool
async def send_availability_poll(
    recipients: str,
    dates: str,
    purpose: str,
    slack_channel: str = ""
) -> str:
    """Send an availability poll to team members.

    Args:
        recipients: Who to send to (comma-separated or team name)
        dates: Date options
        purpose: What the poll is for
        slack_channel: Optional Slack channel to post to

    Returns:
        Confirmation
    """
    poll_message = f"""*Availability Poll*
Please indicate your availability for: {purpose}

Date Options: {dates}
Recipients: {recipients}

React with :white_check_mark: for available, :x: for unavailable."""

    # Try to send via Slack if channel provided
    if slack_channel and settings.slack_bot_token:
        result = await _post_to_slack(slack_channel, poll_message)

        if result.get("success"):
            return f"""Availability Poll Created and Posted:

Channel: {slack_channel}
Recipients: {recipients}
Date Options: {dates}
Purpose: {purpose}

Poll has been posted to Slack. Responses will be collected for 48 hours."""

    return f"""Availability Poll Created:

Recipients: {recipients}
Date Options: {dates}
Purpose: {purpose}

Poll is ready. Provide a slack_channel to post it automatically."""


@tool
async def announce_to_slack(
    channel: str,
    message: str,
    mention: str = ""
) -> str:
    """Post an announcement to a Slack channel (requires approval).

    This is a HITL action - it creates a draft that must be approved
    before actually posting to Slack.

    Args:
        channel: Slack channel name
        message: Announcement message
        mention: Who to mention (@here, @channel, specific users)

    Returns:
        Draft for approval
    """
    # Format the message with mentions
    full_message = message
    if mention:
        if mention == "@channel":
            full_message = f"<!channel> {message}"
        elif mention == "@here":
            full_message = f"<!here> {message}"
        else:
            full_message = f"{mention} {message}"

    # This returns a draft - actual posting happens after approval
    return f"""[PENDING APPROVAL] Slack Announcement:

Channel: #{channel}
Mention: {mention or 'None'}
Message:
{message}

Full formatted message:
{full_message}

This announcement requires your approval before posting.
Once approved, it will be sent to #{channel} via Slack."""


@tool
async def execute_slack_announcement(
    channel: str,
    message: str,
    mention_channel: bool = False
) -> str:
    """Actually execute a Slack announcement (called after approval).

    Args:
        channel: Slack channel name
        message: Announcement message
        mention_channel: Whether to @channel

    Returns:
        Result of posting
    """
    if not settings.slack_bot_token:
        return "Error: SLACK_BOT_TOKEN not configured"

    result = await _post_to_slack(channel, message, mention_channel)

    if result.get("success"):
        return f"Announcement posted successfully to #{channel}"
    else:
        return f"Failed to post: {result.get('error')}"


EVENTS_TOOLS = [
    get_logistics_summary,
    update_logistics_sheet,
    generate_event_schedule,
    send_team_reminder,
    create_room_booking_request,
    send_availability_poll,
    announce_to_slack,
    execute_slack_announcement,
]
