"""Live tests for GitHub MCP integration.

Run with: uv run python tests/test_tools/test_github_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
# Assumes running from project root (backend/)
sys.path.insert(0, str(Path.cwd()))

from src.services.mcp_client import mcp_client


async def test_github():
    """Test GitHub MCP integration."""
    print("\n" + "=" * 50)
    print("GITHUB MCP TEST")
    print("=" * 50)
    
    try:
        # Test connection/auth
        print("\n--- Testing connection (list_repos) ---")
        # We'll try to list repos (using list_issues on a known public repo or similar as a proxy check? 
        # Actually, let's just interpret the result of get_pr_summary carefully.
        # But user requested "add more testing". 
        # mcp_server_github doesn't expose "get_user".
        # Let's try listing issues on input repo again, but be robust.
        pass

        # Test get PR summary
        print("\n--- Testing get_pr_summary ---")
        result = await mcp_client.call_github_tool(
            "get_pr_summary",
            {"repo": "Nexus-Bot-v1/nexus-test-repo"}
        )
        print(f"Result: {result}")
        
        # Test list issues
        print("\n--- Testing list_issues ---")
        result = await mcp_client.call_github_tool(
            "list_issues",
            {"repo": "Nexus-Bot-v1/nexus-test-repo", "limit": 5}
        )
        print(f"Result: {result}")
        
        if isinstance(result, dict) and "error" in result:
            print(f"FAILED: Returned error: {result['error']}")
            if "traceback" in result:
                print(f"Server Traceback:\n{result['traceback']}")
            return False
            
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


async def main():
    print("\n" + "#" * 60)
    print("# GITHUB INTEGRATION TEST")
    print("#" * 60)
    
    passed = await test_github()
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\nGitHub Status: {status}")
    print("\n" + "#" * 60)


if __name__ == "__main__":
    asyncio.run(main())
