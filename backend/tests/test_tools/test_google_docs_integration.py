import asyncio
import os
import sys

"""Live integration test for Google Docs tools.

Run from backend directory:
    uv run python tests/test_tools/test_google_docs_integration.py
"""

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.services.mcp_client import mcp_client

TEST_DOC_ID = "19ZsRyz6ViOsqx6uxwzgmd2MisnEWSC8PVbERnquLG-0"

async def test_google_docs_integration():
    print("=" * 50)
    print("GOOGLE DOCS MCP TEST")
    print("=" * 50)
    
    # MCP client handles session initialization per tool call
    pass

    try:
        # Test 1: Get Document Metadata
        print(f"\n--- Testing get_document_metadata (Doc ID: {TEST_DOC_ID}) ---")
        if TEST_DOC_ID == "YOUR_GOOGLE_DOC_ID_HERE":
            print("SKIPPING: Please update TEST_DOC_ID in the test file with a real Google Doc ID.")
        else:
            result = await mcp_client.call_google_docs_tool(
                "get_document_metadata",
                {"doc_id": TEST_DOC_ID}
            )
            print(f"Result: {result}")
    except Exception as e:
        print(f"Error testing metadata: {e}")

    try:
        # Test 2: Read Document Content
        print(f"\n--- Testing read_document (Doc ID: {TEST_DOC_ID}) ---")
        if TEST_DOC_ID == "YOUR_GOOGLE_DOC_ID_HERE":
            print("SKIPPING: Please update TEST_DOC_ID in the test file.")
        else:
            result = await mcp_client.call_google_docs_tool(
                "read_document",
                {"doc_id": TEST_DOC_ID}
            )
            # Truncate content for display
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if len(content) > 10000:
                    result["content"] = content[:10000] + "... (truncated)"
            
            print(f"Result: {result}")
            
    except Exception as e:
        print(f"Error testing read: {e}")

    print("\nGoogle Docs Status: [DONE]")

if __name__ == "__main__":
    asyncio.run(test_google_docs_integration())
