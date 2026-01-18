"""
Slack tools for Nexus.

Provides messaging and announcement capabilities for Slack via MCP.
"""

from typing import Optional

from langchain_core.tools import tool

from src.services.mcp_client import mcp_client


# =============================================================================
# CHANNEL WHITELIST CONFIGURATION
# TODO: Replace with database lookup or user settings in the future
# =============================================================================
ALLOWED_CHANNELS = [
    "#nexus-test-announcement",
    "#blueprint-team",
    "#partnerships",
    # Add more channels as needed
]


def get_allowed_channels() -> list[str]:
    """Get the list of allowed Slack channels.
    
    Currently returns a static list, but can be replaced with:
    - Database query
    - User settings from MongoDB
    - API call to configuration service
    
    Returns:
        List of allowed channel names (with # prefix)
    """
    # TODO: Replace with dynamic lookup
    # Example future implementation:
    # return await db.get_user_slack_channels(user_id)
    return ALLOWED_CHANNELS


def get_allowed_channels_str() -> str:
    """Get allowed channels as comma-separated string for MCP server."""
    return ",".join(get_allowed_channels())


@tool
async def send_availability_poll(
    attendees: list[str],
    duration: str,
    date_range: str,
    slack_channel: str,
    user_id: Optional[str] = None
) -> str:
    """Post When2Meet/LettuceMeet poll link to Slack channel.
    
    Args:
        attendees: List of attendee names or emails
        duration: Meeting duration (e.g., '1h', '30m')
        date_range: Date range for poll (e.g., 'Jan 20-25')
        slack_channel: Slack channel to post poll to
        user_id: Optional user ID for per-user OAuth token
        
    Returns:
        Confirmation with poll link or error
    """
    # TODO: Implement When2Meet/LettuceMeet integration
    poll_message = (
        f"*Availability Poll*\n"
        f"Please fill out your availability for {date_range}\n"
        f"Duration: {duration}\n"
        f"Attendees: {', '.join(attendees)}\n"
        f"_(Poll link would go here)_"
    )
    
    try:
        result = await mcp_client.call_slack_tool(
            "post_message",
            {"channel": slack_channel, "text": poll_message},
            user_id=user_id
        )
        
        if isinstance(result, dict) and result.get("success"):
            return f"Posted availability poll for {len(attendees)} attendees to {slack_channel}"
        elif isinstance(result, dict) and result.get("error"):
            return f"Failed to post poll: {result['error']}"
        return f"Posted availability poll to {slack_channel}"
    except Exception as e:
        return f"Failed to post availability poll: {str(e)}"


@tool
async def send_team_reminder(
    team: str, 
    message: str,
    user_id: Optional[str] = None
) -> str:
    """Post reminder to a team's Slack channel.
    
    Args:
        team: Team name (e.g., 'partnerships', 'logistics')
        message: Reminder message
        user_id: Optional user ID for per-user OAuth token
        
    Returns:
        Confirmation or error
    """
    channel = f"#{team}"
    reminder_message = f"*Reminder*\n{message}"
    
    try:
        result = await mcp_client.call_slack_tool(
            "post_message",
            {"channel": channel, "text": reminder_message},
            user_id=user_id
        )
        
        if isinstance(result, dict) and result.get("success"):
            return f"Sent reminder to {channel}"
        elif isinstance(result, dict) and result.get("error"):
            return f"Failed to send reminder: {result['error']}"
        return f"Sent reminder to {channel}"
    except Exception as e:
        return f"Failed to send reminder: {str(e)}"


@tool
async def announce_to_slack(
    channel: str,
    message: str,
    mention_team: Optional[bool] = False,
    user_id: Optional[str] = None
) -> str:
    """Post announcement to Slack channel.
    
    Args:
        channel: Slack channel name (e.g., '#blueprint-team')
        message: Announcement message
        mention_team: Whether to include @channel mention
        user_id: Optional user ID for per-user OAuth token
        
    Returns:
        Confirmation or error
    """
    try:
        result = await mcp_client.call_slack_tool(
            "post_message",
            {
                "channel": channel,
                "text": message,
                "mention_channel": mention_team
            },
            user_id=user_id
        )
        
        if isinstance(result, dict) and result.get("success"):
            mention = " (with @channel)" if mention_team else ""
            return f"Posted announcement to {channel}{mention}"
        elif isinstance(result, dict) and result.get("error"):
            return f"Failed to post announcement: {result['error']}"
        return f"Posted announcement to {channel}"
    except Exception as e:
        return f"Failed to post announcement: {str(e)}"


@tool
async def list_slack_channels(user_id: Optional[str] = None) -> str:
    """List available Slack channels that the bot can post to.
    
    Args:
        user_id: Optional user ID for per-user OAuth token
    
    Returns:
        List of available channels
    """
    try:
        result = await mcp_client.call_slack_tool("list_channels", {}, user_id=user_id)
        
        if isinstance(result, dict) and "channels" in result:
            channels = result["channels"]
            if not channels:
                return "No channels available (bot may not be invited to any channels)"
            
            channel_list = [f"- {ch['name']}" + (" ✓" if ch.get("is_member") else "") 
                          for ch in channels]
            return "Available Slack channels:\n" + "\n".join(channel_list)
        elif isinstance(result, dict) and result.get("error"):
            return f"Failed to list channels: {result['error']}"
        return "Could not retrieve channel list"
    except Exception as e:
        return f"Failed to list channels: {str(e)}"


# Export all tools for agent binding
SLACK_TOOLS = [
    send_availability_poll,
    send_team_reminder,
    announce_to_slack,
    list_slack_channels,
]
