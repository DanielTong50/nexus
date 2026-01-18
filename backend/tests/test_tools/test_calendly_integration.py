"""Live tests for Calendly MCP integration.

Run with: uv run python tests/test_tools/test_calendly_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
# Assumes running from project root (backend/)
sys.path.insert(0, str(Path.cwd()))

from src.services.mcp_client import mcp_client


async def test_calendly():
    """Test Calendly MCP integration."""
    print("\n" + "=" * 50)
    print("CALENDLY MCP TEST")
    print("=" * 50)
    
    try:
        # Test get current user
        print("\n--- Testing get_current_user ---")
        result = await mcp_client.call_calendly_tool("get_current_user", {})
        print(f"Result: {result}")
        
        # Test list event types
        print("\n--- Testing list_event_types ---")
        result = await mcp_client.call_calendly_tool(
            "list_event_types",
            {"active_only": True}
        )
        print(f"Result: {result}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


async def main():
    print("\n" + "#" * 60)
    print("# CALENDLY INTEGRATION TEST")
    print("#" * 60)
    
    passed = await test_calendly()
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\nCalendly Status: {status}")
    print("\n" + "#" * 60)


if __name__ == "__main__":
    asyncio.run(main())
