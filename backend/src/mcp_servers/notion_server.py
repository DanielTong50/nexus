"""Notion MCP Server using Python.

This is a local MCP server that exposes Notion operations
as MCP tools. Uses httpx for REST API calls (more reliable than notion-client SDK).

Run with: uv run python -m src.mcp_servers.notion_server
"""

import asyncio
import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP Server
server = Server("notion-server")

# Notion config
API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
TOKEN: str = ""
TIMELINE_DATABASE_ID: str = ""


def get_headers() -> dict:
    """Get authenticated headers for Notion API."""
    global TOKEN, TIMELINE_DATABASE_ID
    TOKEN = os.environ.get("NOTION_TOKEN", "")
    TIMELINE_DATABASE_ID = os.environ.get("NOTION_TIMELINE_DATABASE_ID", "")
    
    if not TOKEN:
        raise ValueError("NOTION_TOKEN environment variable not set")
    
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }


def extract_text_from_property(prop: dict) -> str:
    """Extract text value from a Notion property."""
    prop_type = prop.get("type")
    
    if prop_type == "title":
        return "".join([t.get("plain_text", "") for t in prop.get("title", [])])
    elif prop_type == "rich_text":
        return "".join([t.get("plain_text", "") for t in prop.get("rich_text", [])])
    elif prop_type == "select":
        select = prop.get("select")
        return select.get("name", "") if select else ""
    elif prop_type == "multi_select":
        return ", ".join([s.get("name", "") for s in prop.get("multi_select", [])])
    elif prop_type == "date":
        date = prop.get("date")
        return date.get("start", "") if date else ""
    elif prop_type == "people":
        return ", ".join([p.get("name", "") for p in prop.get("people", [])])
    elif prop_type == "checkbox":
        return str(prop.get("checkbox", False))
    elif prop_type == "status":
        status = prop.get("status")
        return status.get("name", "") if status else ""
    else:
        return str(prop)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Notion tools."""
    return [
        Tool(
            name="query_timeline",
            description="Query timeline items from the Notion database",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_id": {
                        "type": "string",
                        "description": "Database ID (optional, uses default if not provided)"
                    },
                    "filter_status": {
                        "type": "string",
                        "description": "Filter by status (e.g., 'In Progress', 'Done')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max items to return",
                        "default": 20
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="update_timeline_item",
            description="Update a timeline item's properties",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "The Notion page ID to update"
                    },
                    "status": {
                        "type": "string",
                        "description": "New status value"
                    },
                    "date": {
                        "type": "string",
                        "description": "New date (YYYY-MM-DD format)"
                    }
                },
                "required": ["page_id"]
            }
        ),
        Tool(
            name="create_timeline_item",
            description="Create a new timeline item",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_id": {
                        "type": "string",
                        "description": "Database ID (optional, uses default if not provided)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Item title"
                    },
                    "status": {
                        "type": "string",
                        "description": "Initial status"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date (YYYY-MM-DD format)"
                    }
                },
                "required": ["title"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Notion tool."""
    try:
        headers = get_headers()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            if name == "query_timeline":
                db_id = arguments.get("database_id") or TIMELINE_DATABASE_ID
                if not db_id:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": "No database_id provided and NOTION_TIMELINE_DATABASE_ID not set"})
                    )]
                
                # Build request body
                body: dict[str, Any] = {}
                
                # Add filter if status provided
                if arguments.get("filter_status"):
                    body["filter"] = {
                        "property": "Status",
                        "status": {"equals": arguments["filter_status"]}
                    }
                
                # Add page size limit
                page_size = min(arguments.get("limit", 20), 100)
                body["page_size"] = page_size
                
                # Query the database
                response = await client.post(
                    f"{API_BASE}/databases/{db_id}/query",
                    headers=headers,
                    json=body
                )
                response.raise_for_status()
                data = response.json()
                
                items = []
                for page in data.get("results", [])[:arguments.get("limit", 20)]:
                    props = page.get("properties", {})
                    item = {"id": page["id"], "url": page.get("url", "")}
                    
                    for prop_name, prop_value in props.items():
                        item[prop_name] = extract_text_from_property(prop_value)
                    
                    items.append(item)
                
                return [TextContent(
                    type="text",
                    text=json.dumps({"items": items, "count": len(items)})
                )]
            
            elif name == "update_timeline_item":
                page_id = arguments["page_id"]
                properties = {}
                
                if arguments.get("status"):
                    properties["Status"] = {"status": {"name": arguments["status"]}}
                
                if arguments.get("date"):
                    properties["Date"] = {"date": {"start": arguments["date"]}}
                
                if not properties:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": "No properties to update"})
                    )]
                
                response = await client.patch(
                    f"{API_BASE}/pages/{page_id}",
                    headers=headers,
                    json={"properties": properties}
                )
                response.raise_for_status()
                
                return [TextContent(
                    type="text",
                    text=json.dumps({"success": True, "message": f"Updated page {page_id}"})
                )]
            
            elif name == "create_timeline_item":
                db_id = arguments.get("database_id") or TIMELINE_DATABASE_ID
                if not db_id:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": "No database_id provided and NOTION_TIMELINE_DATABASE_ID not set"})
                    )]
                
                properties = {
                    "Name": {"title": [{"text": {"content": arguments["title"]}}]}
                }
                
                if arguments.get("status"):
                    properties["Status"] = {"status": {"name": arguments["status"]}}
                
                if arguments.get("date"):
                    properties["Date"] = {"date": {"start": arguments["date"]}}
                
                response = await client.post(
                    f"{API_BASE}/pages",
                    headers=headers,
                    json={
                        "parent": {"database_id": db_id},
                        "properties": properties
                    }
                )
                response.raise_for_status()
                page = response.json()
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "page_id": page["id"],
                        "url": page.get("url", "")
                    })
                )]
            
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except httpx.HTTPStatusError as e:
        error_body = ""
        try:
            error_body = e.response.json()
        except Exception:
            error_body = e.response.text
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": f"{type(e).__name__}: {str(e)}",
                "status_code": e.response.status_code,
                "details": error_body,
                "traceback": "Traceback available in server logs" 
            })
        )]
    except Exception as e:
        import traceback
        return [TextContent(type="text", text=json.dumps({
            "error": f"{type(e).__name__}: {repr(e)}",
            "traceback": traceback.format_exc()
        }))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
