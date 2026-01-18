"""Live OAuth integration test.

This is an interactive test that opens a browser for OAuth authorization.
Run with: uv run python tests/test_tools/test_oauth_live.py

Prerequisites:
1. Register OAuth app with Slack (or another provider)
2. Add credentials to .env:
   - SLACK_OAUTH_CLIENT_ID
   - SLACK_OAUTH_CLIENT_SECRET
3. Start MongoDB
"""

import asyncio
import os
import sys
import webbrowser
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()


async def test_oauth_flow(provider: str = "slack"):
    """Interactive OAuth test - opens browser for authorization."""
    from src.services.oauth_manager import oauth_manager
    
    print("=" * 60)
    print(f"{provider.upper()} OAUTH LIVE TEST")
    print("=" * 60)
    
    # Check credentials
    client_id = os.environ.get(f"{provider.upper()}_OAUTH_CLIENT_ID")
    client_secret = os.environ.get(f"{provider.upper()}_OAUTH_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print(f"\n❌ Missing OAuth credentials for {provider}")
        print(f"   Set {provider.upper()}_OAUTH_CLIENT_ID and {provider.upper()}_OAUTH_CLIENT_SECRET in .env")
        return False
    
    print(f"\n✓ Found OAuth credentials for {provider}")
    
    # Generate OAuth URL
    user_id = "test-user-live"
    try:
        auth_url = await oauth_manager.get_authorization_url(provider, user_id)
        print(f"\n✓ Generated OAuth URL")
        print(f"  URL: {auth_url[:80]}...")
        
        # Open browser
        print("\n→ Opening browser for authorization...")
        webbrowser.open(auth_url)
        
        print("\n" + "-" * 60)
        print("NEXT STEPS:")
        print("-" * 60)
        print("1. Complete authorization in your browser")
        print("2. You should be redirected to localhost:8000/integrations/callback/...")
        print("3. If the server is running, the token will be saved to MongoDB")
        print("\nTo verify, check MongoDB:")
        print(f'  db.user_integrations.findOne({{user_id: "{user_id}", provider: "{provider}"}})')
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test OAuth flow")
    parser.add_argument(
        "--provider", "-p",
        default="slack",
        choices=["google", "slack", "notion", "github", "calendly"],
        help="OAuth provider to test"
    )
    args = parser.parse_args()
    
    success = await test_oauth_flow(args.provider)
    
    if success:
        print("\n✓ Test initiated successfully")
    else:
        print("\n✗ Test failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
