
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

try:
    import mcp
    print(f"✅ 'mcp' module found: {mcp.__file__}")
except ImportError:
    print("❌ 'mcp' module NOT found!")
except Exception as e:
    print(f"❌ Error importing mcp: {e}")

def get_slack_client():
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        print("❌ SLACK_BOT_TOKEN not found in environment")
        return None
    return WebClient(token=token)

async def test_slack_connection():
    try:
        print("Initializing Slack client...")
        client = get_slack_client()
        if not client:
            return
        
        # 1. Test Auth
        print("\n1. Testing Auth...")
        try:
            auth_test = client.auth_test()
            print(f"✅ Authenticated as: {auth_test['user']} (Team: {auth_test['team']})")
        except SlackApiError as e:
            print(f"❌ Auth failed: {e.response['error']}")
            return
        
        # 2. List Channels
        print("\n2. Listing Channels (public & private)...")
        try:
            response = client.conversations_list(types="public_channel,private_channel")
            channels = response["channels"]
            print(f"Found {len(channels)} channels.")
            
            partnerships_found = False
            for ch in channels:
                name = ch['name']
                is_member = ch['is_member']
                print(f" - #{name} (ID: {ch['id']}) [Member: {is_member}]")
                
                if name == "partnerships":
                    partnerships_found = True
                    if not is_member:
                        print(f"❌ WARNING: Bot is NOT a member of #partnerships!")
                    else:
                        print(f"✅ Bot is a member of #partnerships.")
            
            if not partnerships_found:
                 print(f"❌ WARNING: #partnerships channel NOT found in list!")
                 
        except SlackApiError as e:
            print(f"❌ Failed to list channels: {e.response['error']}")
            if e.response['error'] == 'missing_scope':
                print("   -> Missing scope! Need 'channels:read', 'groups:read', or 'mpim:read'")

        # 3. Test Message Post to #partnerships
        print("\n3. Attempting to post to #partnerships...")
        try:
            client.chat_postMessage(channel="#partnerships", text="Test message from Nexus debugging script.")
            print("✅ Successfully posted to #partnerships")
        except SlackApiError as e:
            print(f"❌ Failed to post: {e.response['error']}")
            if e.response['error'] == 'channel_not_found':
                 print("   -> Channel not found! Bot might not be in the channel or it's private.")
            elif e.response['error'] == 'not_in_channel':
                 print("   -> Bot is not in the channel! Invite it with /invite @botname")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_slack_connection())
