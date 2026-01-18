"""Slack MCP Server using Python.

This is a local MCP server that exposes Slack operations
as MCP tools. It uses the Slack SDK with bot token authentication.

Run with: uv run python -m src.mcp_servers.slack_server
"""

import asyncio
import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Initialize MCP Server
server = Server("slack-server")

# Slack client (initialized on startup)
slack_client: WebClient | None = None
ALLOWED_CHANNELS: set[str] = set()


def get_slack_client() -> WebClient:
    """Initialize Slack WebClient."""
    global slack_client, ALLOWED_CHANNELS
    
    bot_token = os.environ.get("SLACK_BOT_TOKEN", "")
    allowed_channels_str = os.environ.get("SLACK_ALLOWED_CHANNELS", "")
    
    if not bot_token:
        raise ValueError("SLACK_BOT_TOKEN environment variable not set")
    
    # Parse allowed channels (comma-separated)
    if allowed_channels_str:
        ALLOWED_CHANNELS = {ch.strip() for ch in allowed_channels_str.split(",")}
    
    slack_client = WebClient(token=bot_token)
    return slack_client


def is_channel_allowed(channel: str) -> bool:
    """Check if channel is in the whitelist."""
    if not ALLOWED_CHANNELS:
        # If no whitelist configured, allow all
        return True
    
    # Normalize channel name (add # if missing)
    normalized = channel if channel.startswith("#") else f"#{channel}"
    return normalized in ALLOWED_CHANNELS


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Slack tools."""
    return [
        Tool(
            name="post_message",
            description="Post a message to a Slack channel. Channel must be in the allowed list.",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "The channel to post to (e.g., '#general' or 'general')"
                    },
                    "text": {
                        "type": "string",
                        "description": "The message text to post"
                    },
                    "mention_channel": {
                        "type": "boolean",
                        "description": "Whether to prepend @channel to the message",
                        "default": False
                    }
                },
                "required": ["channel", "text"]
            }
        ),
        Tool(
            name="list_channels",
            description="List available Slack channels (filtered by whitelist if configured)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Slack tool."""
    global slack_client
    
    if slack_client is None:
        get_slack_client()
    
    try:
        if name == "post_message":
            channel = arguments["channel"]
            text = arguments["text"]
            mention_channel = arguments.get("mention_channel", False)
            
            # Check whitelist
            if not is_channel_allowed(channel):
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Channel '{channel}' is not in the allowed list",
                        "allowed_channels": list(ALLOWED_CHANNELS)
                    })
                )]
            
            # Normalize channel name (remove # for API)
            channel_name = channel.lstrip("#")
            
            # Prepend @channel if requested
            if mention_channel:
                text = f"<!channel> {text}"
            
            response = slack_client.chat_postMessage(
                channel=channel_name,
                text=text
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "channel": response["channel"],
                    "ts": response["ts"],
                    "message": f"Posted to #{channel_name}"
                })
            )]
        
        elif name == "list_channels":
            response = slack_client.conversations_list(
                types="public_channel,private_channel"
            )
            
            channels = []
            for ch in response.get("channels", []):
                channel_name = f"#{ch['name']}"
                # Filter by whitelist if configured
                if is_channel_allowed(channel_name):
                    channels.append({
                        "name": channel_name,
                        "id": ch["id"],
                        "is_member": ch.get("is_member", False)
                    })
            
            return [TextContent(
                type="text",
                text=json.dumps({"channels": channels})
            )]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except SlackApiError as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e.response["error"]), "details": str(e)})
        )]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Run the MCP server."""
    get_slack_client()  # Initialize on startup
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
