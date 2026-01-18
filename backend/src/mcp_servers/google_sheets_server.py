"""Custom Google Sheets MCP Server using Python.

This is a local MCP server that exposes Google Sheets operations
as MCP tools. It uses the Google Sheets API directly with service
account authentication.

Run with: uv run python -m src.mcp_servers.google_sheets_server
"""

import asyncio
import json
import os
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP Server
server = Server("google-sheets-server")

# Google Sheets client (initialized on startup)
sheets_service = None
SPREADSHEET_ID = None


def get_sheets_service():
    """Initialize Google Sheets API client."""
    global sheets_service, SPREADSHEET_ID
    
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    SPREADSHEET_ID = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID", "")
    
    if not creds_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set")
    
    if not SPREADSHEET_ID:
        raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID environment variable not set")
    
    creds_data = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    
    sheets_service = build("sheets", "v4", credentials=credentials)
    return sheets_service


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Google Sheets tools."""
    return [
        Tool(
            name="read_range",
            description="Read data from a range in the spreadsheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "range": {
                        "type": "string",
                        "description": "The A1 notation range to read (e.g., 'Sheet1!A1:D10')"
                    }
                },
                "required": ["range"]
            }
        ),
        Tool(
            name="append_row",
            description="Append a row to a sheet",
            inputSchema={
                "type": "object",
                "properties": {
                    "range": {
                        "type": "string",
                        "description": "The range to append to (e.g., 'Partnerships!A:G')"
                    },
                    "values": {
                        "type": "array",
                        "items": {"type": "array"},
                        "description": "2D array of values to append"
                    }
                },
                "required": ["range", "values"]
            }
        ),
        Tool(
            name="update_range",
            description="Update a specific range with new values",
            inputSchema={
                "type": "object",
                "properties": {
                    "range": {
                        "type": "string",
                        "description": "The A1 notation range to update"
                    },
                    "values": {
                        "type": "array",
                        "items": {"type": "array"},
                        "description": "2D array of values to write"
                    }
                },
                "required": ["range", "values"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Google Sheets tool."""
    global sheets_service, SPREADSHEET_ID
    
    if sheets_service is None:
        get_sheets_service()
    
    try:
        if name == "read_range":
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=arguments["range"]
            ).execute()
            values = result.get("values", [])
            return [TextContent(type="text", text=json.dumps(values))]
        
        elif name == "append_row":
            body = {"values": arguments["values"]}
            result = sheets_service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=arguments["range"],
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()
            return [TextContent(
                type="text", 
                text=json.dumps({"updatedCells": result.get("updates", {}).get("updatedCells", 0)})
            )]
        
        elif name == "update_range":
            body = {"values": arguments["values"]}
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=arguments["range"],
                valueInputOption="RAW",
                body=body
            ).execute()
            return [TextContent(
                type="text",
                text=json.dumps({"updatedCells": result.get("updatedCells", 0)})
            )]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    get_sheets_service()  # Initialize on startup
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
