"""Google Docs MCP Server using Python.

This is a local MCP server that exposes Google Docs operations
as MCP tools. Uses the same service account as Google Sheets.

Run with: uv run python -m src.mcp_servers.google_docs_server
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
server = Server("google-docs-server")

# Google Docs client (initialized on startup)
docs_service = None


def get_docs_service():
    """Initialize Google Docs API client."""
    global docs_service
    
    creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    
    if not creds_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set")
    
    creds_data = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_data,
        scopes=["https://www.googleapis.com/auth/documents.readonly"]
    )
    
    docs_service = build("docs", "v1", credentials=credentials)
    return docs_service


def extract_text_from_document(doc: dict) -> str:
    """Extract plain text content from a Google Doc."""
    text_parts = []
    
    body = doc.get("body", {})
    content = body.get("content", [])
    
    for element in content:
        if "paragraph" in element:
            paragraph = element["paragraph"]
            for elem in paragraph.get("elements", []):
                if "textRun" in elem:
                    text_parts.append(elem["textRun"].get("content", ""))
    
    return "".join(text_parts)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Google Docs tools."""
    return [
        Tool(
            name="read_document",
            description="Read the full text content of a Google Doc",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "The Google Doc ID (from the URL)"
                    }
                },
                "required": ["doc_id"]
            }
        ),
        Tool(
            name="get_document_metadata",
            description="Get metadata about a Google Doc (title, last modified, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "The Google Doc ID"
                    }
                },
                "required": ["doc_id"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Google Docs tool."""
    global docs_service
    
    if docs_service is None:
        get_docs_service()
    
    try:
        if name == "read_document":
            doc_id = arguments["doc_id"]
            
            doc = docs_service.documents().get(documentId=doc_id).execute()
            text_content = extract_text_from_document(doc)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "title": doc.get("title", ""),
                    "content": text_content,
                    "character_count": len(text_content)
                })
            )]
        
        elif name == "get_document_metadata":
            doc_id = arguments["doc_id"]
            
            doc = docs_service.documents().get(documentId=doc_id).execute()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "title": doc.get("title", ""),
                    "document_id": doc.get("documentId", ""),
                    "revision_id": doc.get("revisionId", "")
                })
            )]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Run the MCP server."""
    get_docs_service()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
