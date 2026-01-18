"""Calendly MCP Server using Python.

This is a local MCP server that exposes Calendly operations
as MCP tools. Uses httpx for REST API calls.

Run with: uv run python -m src.mcp_servers.calendly_server
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
server = Server("calendly-server")

# Calendly config
API_BASE = "https://api.calendly.com"
API_KEY: str = ""


def get_headers() -> dict:
    """Get authenticated headers."""
    global API_KEY
    API_KEY = os.environ.get("CALENDLY_API_KEY", "")
    
    if not API_KEY:
        raise ValueError("CALENDLY_API_KEY environment variable not set")
    
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Calendly tools."""
    return [
        Tool(
            name="get_current_user",
            description="Get the current Calendly user's info and main scheduling URL",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_event_types",
            description="List available event types with their scheduling URLs",
            inputSchema={
                "type": "object",
                "properties": {
                    "active_only": {
                        "type": "boolean",
                        "description": "Only return active event types",
                        "default": True
                    }
                },
                "required": []
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Calendly tool."""
    try:
        headers = get_headers()
        
        async with httpx.AsyncClient() as client:
            if name == "get_current_user":
                response = await client.get(
                    f"{API_BASE}/users/me",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                user = data.get("resource", {})
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "name": user.get("name"),
                        "email": user.get("email"),
                        "scheduling_url": user.get("scheduling_url"),
                        "timezone": user.get("timezone"),
                        "uri": user.get("uri")
                    })
                )]
            
            elif name == "list_event_types":
                # First get current user to get their URI
                user_response = await client.get(
                    f"{API_BASE}/users/me",
                    headers=headers
                )
                user_response.raise_for_status()
                user_uri = user_response.json().get("resource", {}).get("uri")
                
                # Get event types for this user
                params = {"user": user_uri}
                if arguments.get("active_only", True):
                    params["active"] = "true"
                
                response = await client.get(
                    f"{API_BASE}/event_types",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                event_types = []
                for et in data.get("collection", []):
                    event_types.append({
                        "name": et.get("name"),
                        "slug": et.get("slug"),
                        "scheduling_url": et.get("scheduling_url"),
                        "duration": et.get("duration"),
                        "active": et.get("active")
                    })
                
                return [TextContent(
                    type="text",
                    text=json.dumps({"event_types": event_types})
                )]
            
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
                
    except httpx.HTTPStatusError as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e), "status_code": e.response.status_code})
        )]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
