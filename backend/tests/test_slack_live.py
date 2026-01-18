"""Live test for Slack MCP integration.

Run with: uv run python tests/test_slack_live.py

Make sure to set these environment variables in .env:
- SLACK_BOT_TOKEN=xoxb-your-token
- SLACK_ALLOWED_CHANNELS=#test-channel (optional)
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.mcp_client import mcp_client


async def test_list_channels():
    """Test listing Slack channels."""
    print("\n=== Testing list_channels ===")
    try:
        result = await mcp_client.call_slack_tool("list_channels", {})
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


async def test_post_message(channel: str, message: str):
    """Test posting a message to Slack."""
    print(f"\n=== Testing post_message to {channel} ===")
    try:
        result = await mcp_client.call_slack_tool(
            "post_message",
            {"channel": channel, "text": message}
        )
        print(f"Result: {result}")
        return result.get("success", False) if isinstance(result, dict) else False
    except Exception as e:
        print(f"Error: {e}")
        return False


async def main():
    print("Slack MCP Integration Test")
    print("=" * 40)
    
    # Test list channels
    await test_list_channels()
    
    # Test post message - modify this channel to match your setup
    test_channel = "#nexus-test-announcement"  # Change this to your test channel
    test_message = "🤖 Hello from Nexus MCP! This is a test message."
    
    await test_post_message(test_channel, test_message)
    
    print("\n" + "=" * 40)
    print("Tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
