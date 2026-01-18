"""Live tests for Notion MCP integration.

Run with: uv run python tests/test_tools/test_notion_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
# Assumes running from project root (backend/)
sys.path.insert(0, str(Path.cwd()))

from src.services.mcp_client import mcp_client


async def test_notion():
    """Test Notion MCP integration."""
    print("\n" + "=" * 50)
    print("NOTION MCP TEST")
    print("=" * 50)
    
    try:
        # Test query timeline
        print("\n--- Testing query_timeline ---")
        result = await mcp_client.call_notion_tool("query_timeline", {"limit": 5})
        print(f"Result: {result}")
        
        if isinstance(result, dict) and "error" in result:
            print(f"FAILED: Returned error: {result['error']}")
            if "details" in result:
                print(f"Details: {result['details']}")
            return False
            
        if isinstance(result, dict) and "items" not in result:
            print("FAILED: Response missing 'items' key")
            return False
            
        count = result.get("count", 0)
        print(f"Success! Found {count} items.")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


async def main():
    print("\n" + "#" * 60)
    print("# NOTION INTEGRATION TEST")
    print("#" * 60)
    
    passed = await test_notion()
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\nNotion Status: {status}")
    print("\n" + "#" * 60)


if __name__ == "__main__":
    asyncio.run(main())
