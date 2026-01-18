"""
Google Docs tools for Nexus.

Provides document reading capabilities via MCP.
"""

from langchain_core.tools import tool

from src.services.mcp_client import mcp_client


# =============================================================================
# GOOGLE DOCS CONFIGURATION
# TODO: Can be replaced with database lookup for allowed docs
# =============================================================================
ALLOWED_DOC_IDS = [
    # Add Google Doc IDs that are allowed to be read
    # Example: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
]


@tool
async def read_google_doc(doc_id: str) -> str:
    """Read the text content of a Google Doc.
    
    Args:
        doc_id: The Google Doc ID (from the URL)
        
    Returns:
        Document content or error
    """
    try:
        result = await mcp_client.call_google_docs_tool(
            "read_document",
            {"doc_id": doc_id}
        )
        
        if isinstance(result, dict):
            if result.get("error"):
                return f"Failed to read doc: {result['error']}"
            
            title = result.get("title", "Untitled")
            content = result.get("content", "")
            char_count = result.get("character_count", 0)
            
            # Truncate if too long
            max_length = 5000
            if len(content) > max_length:
                content = content[:max_length] + f"\n\n... (truncated, {char_count} total characters)"
            
            return f"# {title}\n\n{content}"
        return str(result)
    except Exception as e:
        return f"Failed to read document: {str(e)}"


@tool
async def get_google_doc_info(doc_id: str) -> str:
    """Get metadata about a Google Doc (title, revision, etc.).
    
    Args:
        doc_id: The Google Doc ID
        
    Returns:
        Document metadata or error
    """
    try:
        result = await mcp_client.call_google_docs_tool(
            "get_document_metadata",
            {"doc_id": doc_id}
        )
        
        if isinstance(result, dict):
            if result.get("error"):
                return f"Failed to get doc info: {result['error']}"
            
            lines = [
                f"Title: {result.get('title', 'Unknown')}",
                f"Document ID: {result.get('document_id', doc_id)}",
                f"Revision ID: {result.get('revision_id', 'Unknown')}",
            ]
            
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Failed to get document info: {str(e)}"


# Export all tools for agent binding
GOOGLE_DOCS_TOOLS = [
    read_google_doc,
    get_google_doc_info,
]
