"""
Notion tools for Nexus.

Provides timeline database access and updates via MCP.
"""

from langchain_core.tools import tool

from src.services.mcp_client import mcp_client


# =============================================================================
# NOTION CONFIGURATION
# =============================================================================
# TODO: Move to MongoDB user_settings collection for per-user customization
# Schema: { user_id: str, notion_timeline_database_id: str, ... }
# Query: db.user_settings.find_one({"user_id": current_user.id})
# =============================================================================
TIMELINE_DATABASE_ID = "2ecf9472a05380b89d83e48dfb05bfe9?v=2ecf9472a05380429abe000c27eddba3"  # Paste your Notion timeline database ID here


def get_timeline_database_id() -> str:
    """Get the Notion timeline database ID.
    
    Currently returns a hardcoded value. 
    
    TODO: Replace with MongoDB lookup from user_settings collection:
        user_settings = await db.user_settings.find_one({"user_id": user_id})
        return user_settings.get("notion_timeline_database_id", "")
    
    Returns:
        Notion database ID string
    """
    # Clean up ID if user pasted full URL query string
    if "?" in TIMELINE_DATABASE_ID:
        return TIMELINE_DATABASE_ID.split("?")[0]
        
    return TIMELINE_DATABASE_ID


@tool
async def get_timeline(status_filter: str = "") -> str:
    """Get timeline items from the Notion database.
    
    Args:
        status_filter: Optional status to filter by (e.g., 'In Progress', 'Done')
        
    Returns:
        Formatted list of timeline items
    """
    db_id = get_timeline_database_id()
    if not db_id:
        return "Error: Notion timeline database ID not configured. Set TIMELINE_DATABASE_ID in notion.py"
    
    try:
        args = {"limit": 20}
        if status_filter:
            args["filter_status"] = status_filter
        
        result = await mcp_client.call_notion_tool("query_timeline", args)
        
        if isinstance(result, dict):
            if result.get("error"):
                return f"Failed to get timeline: {result['error']}"
            
            items = result.get("items", [])
            count = result.get("count", 0)
            
            if count == 0:
                filter_msg = f" with status '{status_filter}'" if status_filter else ""
                return f"No timeline items found{filter_msg}"
            
            lines = [f"Timeline items ({count}):"]
            for item in items:
                # Extract common fields - adjust based on your database schema
                name = item.get("Name") or item.get("Title") or "Untitled"
                status = item.get("Status", "")
                date = item.get("Date", "")
                
                status_str = f" [{status}]" if status else ""
                date_str = f" ({date})" if date else ""
                lines.append(f"  - {name}{status_str}{date_str}")
            
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Failed to get timeline: {str(e)}"


@tool
async def update_timeline_item(
    page_id: str,
    status: str = "",
    date: str = ""
) -> str:
    """Update a timeline item's status or date.
    
    Args:
        page_id: The Notion page ID to update
        status: New status value (e.g., 'In Progress', 'Done')
        date: New date in YYYY-MM-DD format
        
    Returns:
        Confirmation or error
    """
    if not status and not date:
        return "Error: Must provide either status or date to update"
    
    try:
        args = {"page_id": page_id}
        if status:
            args["status"] = status
        if date:
            args["date"] = date
        
        result = await mcp_client.call_notion_tool("update_timeline_item", args)
        
        if isinstance(result, dict):
            if result.get("success"):
                updates = []
                if status:
                    updates.append(f"status to '{status}'")
                if date:
                    updates.append(f"date to '{date}'")
                return f"Updated timeline item: {', '.join(updates)}"
            elif result.get("error"):
                return f"Failed to update: {result['error']}"
        return str(result)
    except Exception as e:
        return f"Failed to update timeline item: {str(e)}"


@tool
async def create_timeline_item(
    title: str,
    status: str = "",
    date: str = ""
) -> str:
    """Create a new timeline item.
    
    Args:
        title: Item title
        status: Initial status (e.g., 'Not Started', 'In Progress')
        date: Date in YYYY-MM-DD format
        
    Returns:
        Confirmation with page URL or error
    """
    db_id = get_timeline_database_id()
    if not db_id:
        return "Error: Notion timeline database ID not configured. Set TIMELINE_DATABASE_ID in notion.py"
    
    try:
        args = {"title": title}
        if status:
            args["status"] = status
        if date:
            args["date"] = date
        
        result = await mcp_client.call_notion_tool("create_timeline_item", args)
        
        if isinstance(result, dict):
            if result.get("success"):
                url = result.get("url", "")
                return f"Created timeline item: '{title}'" + (f"\nURL: {url}" if url else "")
            elif result.get("error"):
                return f"Failed to create: {result['error']}"
        return str(result)
    except Exception as e:
        return f"Failed to create timeline item: {str(e)}"


# Export all tools for agent binding
NOTION_TOOLS = [
    get_timeline,
    update_timeline_item,
    create_timeline_item,
]
