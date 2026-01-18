"""
Notion tools for Nexus.

Provides timeline database access, search, and updates via MCP.
Supports organization-specific configuration loaded from MongoDB.
"""

import logging
from typing import Optional

from langchain_core.tools import tool

from src.services.mcp_client import mcp_client
from src.services.organization import org_service, DEFAULT_ORG_ID

logger = logging.getLogger(__name__)


async def get_timeline_database_id(org_id: str = DEFAULT_ORG_ID) -> str:
    """Get the Notion timeline database ID from org config.
    
    Args:
        org_id: Organization identifier
        
    Returns:
        Notion database ID string
    """
    try:
        org_config = await org_service.get_config(org_id)
        db_id = org_config.data_sources.marketing_timeline
        
        # Clean up ID if it contains query string
        if db_id and "?" in db_id:
            return db_id.split("?")[0]
        
        return db_id or ""
    except Exception as e:
        logger.error(f"Error getting timeline database ID: {e}")
        return ""


@tool
async def get_timeline(
    status_filter: str = "",
    org_id: str = DEFAULT_ORG_ID,
) -> str:
    """Get timeline items from the Notion database.
    
    Args:
        status_filter: Optional status to filter by (e.g., 'In Progress', 'Done')
        org_id: Organization identifier
        
    Returns:
        Formatted list of timeline items
    """
    db_id = await get_timeline_database_id(org_id)
    if not db_id:
        return "Error: Notion timeline database ID not configured in organization settings."
    
    try:
        args = {"database_id": db_id, "limit": 20}
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
async def search_notion(
    query: str,
    database_type: str = "timeline",
    org_id: str = DEFAULT_ORG_ID,
) -> str:
    """Search Notion databases for specific content.
    
    Use this to answer questions like "When will we be filming the teaser video?"
    by searching the marketing timeline or other Notion databases.
    
    Args:
        query: Search query (what you're looking for)
        database_type: Type of database to search ("timeline", "tasks", or a database ID)
        org_id: Organization identifier
        
    Returns:
        Search results
    """
    try:
        # Get the appropriate database ID
        org_config = await org_service.get_config(org_id)
        
        if database_type == "timeline":
            db_id = org_config.data_sources.marketing_timeline
        elif database_type == "tasks":
            db_id = org_config.data_sources.tasks_database
        else:
            # Assume it's a direct database ID
            db_id = database_type
        
        if not db_id:
            return f"Error: Notion {database_type} database not configured in organization settings."
        
        # Clean up database ID
        if "?" in db_id:
            db_id = db_id.split("?")[0]
        
        # Call MCP tool to search
        result = await mcp_client.call_notion_tool("search_database", {
            "database_id": db_id,
            "query": query,
            "limit": 10,
        })
        
        if isinstance(result, dict):
            if result.get("error"):
                # Fall back to querying all items and filtering locally
                return await _fallback_search(db_id, query)
            
            items = result.get("items", [])
            count = result.get("count", 0)
            
            if count == 0:
                return f"No results found for '{query}' in {database_type}."
            
            return _format_search_results(items, query, database_type)
        
        return str(result)
        
    except Exception as e:
        logger.error(f"Notion search error: {e}")
        return f"Error searching Notion: {str(e)}"


async def _fallback_search(db_id: str, query: str) -> str:
    """Fallback search by querying all items and filtering locally.
    
    Used when the MCP server doesn't support direct search.
    """
    try:
        result = await mcp_client.call_notion_tool("query_timeline", {
            "database_id": db_id,
            "limit": 100,
        })
        
        if isinstance(result, dict) and result.get("items"):
            items = result["items"]
            query_lower = query.lower()
            
            # Filter items that match the query
            matches = []
            for item in items:
                # Check all text fields
                for key, value in item.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        matches.append(item)
                        break
            
            if not matches:
                return f"No results found for '{query}'."
            
            return _format_search_results(matches, query, "database")
        
        return f"No results found for '{query}'."
        
    except Exception as e:
        return f"Search error: {str(e)}"


def _format_search_results(items: list, query: str, database_type: str) -> str:
    """Format search results for display."""
    lines = [f"Found {len(items)} results for '{query}' in {database_type}:\n"]
    
    for item in items:
        name = item.get("Name") or item.get("Title") or "Untitled"
        status = item.get("Status", "")
        date = item.get("Date", "")
        
        line = f"• **{name}**"
        if status:
            line += f" [{status}]"
        if date:
            line += f" - {date}"
        
        # Add any additional context
        for key in ["Description", "Notes", "Details"]:
            if key in item and item[key]:
                # Truncate long text
                text = str(item[key])[:100]
                if len(str(item[key])) > 100:
                    text += "..."
                line += f"\n  {text}"
        
        lines.append(line)
    
    return "\n".join(lines)


@tool
async def update_timeline_item(
    page_id: str,
    status: str = "",
    date: str = "",
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
    date: str = "",
    org_id: str = DEFAULT_ORG_ID,
) -> str:
    """Create a new timeline item.
    
    Args:
        title: Item title
        status: Initial status (e.g., 'Not Started', 'In Progress')
        date: Date in YYYY-MM-DD format
        org_id: Organization identifier
        
    Returns:
        Confirmation with page URL or error
    """
    db_id = await get_timeline_database_id(org_id)
    if not db_id:
        return "Error: Notion timeline database ID not configured in organization settings."
    
    try:
        args = {"database_id": db_id, "title": title}
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


@tool
async def find_timeline_item(
    search_query: str,
    org_id: str = DEFAULT_ORG_ID,
) -> str:
    """Find a specific timeline item by name or description.
    
    Use this to answer questions like "When will we be filming the teaser video?"
    
    Args:
        search_query: What to search for (e.g., "teaser video", "sponsor deadline")
        org_id: Organization identifier
        
    Returns:
        Matching timeline items with dates and status
    """
    return await search_notion(query=search_query, database_type="timeline", org_id=org_id)


# Export all tools for agent binding
NOTION_TOOLS = [
    get_timeline,
    search_notion,
    find_timeline_item,
    update_timeline_item,
    create_timeline_item,
]
