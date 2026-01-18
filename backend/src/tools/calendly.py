"""
Calendly tools for Nexus.

Provides meeting link generation via MCP.
"""

from langchain_core.tools import tool

from src.services.mcp_client import mcp_client


@tool
async def prepare_calendly_link(assignee: str = "", meeting_type: str = "") -> str:
    """Get the Calendly scheduling URL for the user.
    
    Args:
        assignee: Team member name (not used currently, for future multi-user support)
        meeting_type: Type of meeting (not used currently)
        
    Returns:
        Calendly scheduling link
    """
    try:
        result = await mcp_client.call_calendly_tool("get_current_user", {})
        
        if isinstance(result, dict):
            if result.get("error"):
                return f"Failed to get Calendly link: {result['error']}"
            
            url = result.get("scheduling_url", "")
            name = result.get("name", "User")
            
            if url:
                return f"Calendly link for {name}: {url}"
            return "No scheduling URL found"
        return str(result)
    except Exception as e:
        return f"Failed to get Calendly link: {str(e)}"


@tool
async def list_calendly_event_types() -> str:
    """List available Calendly event types with their scheduling URLs.
    
    Returns:
        List of event types with URLs
    """
    try:
        result = await mcp_client.call_calendly_tool(
            "list_event_types",
            {"active_only": True}
        )
        
        if isinstance(result, dict):
            if result.get("error"):
                return f"Failed to list event types: {result['error']}"
            
            event_types = result.get("event_types", [])
            
            if not event_types:
                return "No active event types found"
            
            lines = ["Available Calendly event types:"]
            for et in event_types:
                duration = et.get("duration", 0)
                lines.append(f"  - {et['name']} ({duration} min): {et['scheduling_url']}")
            
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Failed to list event types: {str(e)}"


# Export all tools for agent binding
CALENDLY_TOOLS = [
    prepare_calendly_link,
    list_calendly_event_types,
]
