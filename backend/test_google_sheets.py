"""Integration test for Google Sheets MCP tools.

Run with: 
  uv run python test_google_sheets.py              # Test all sheets
  uv run python test_google_sheets.py "Workshops"  # Test specific sheet
"""

import asyncio
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# All sheets in your Blueprint Partnership Logs spreadsheet
ALL_SHEETS = [
    "Coffee Chat Delegates",
    "Boothing Companies",
    "Keynote Speaker",
    "Workshops",
]


async def get_session():
    """Create MCP session parameters."""
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.mcp_servers.google_sheets_server"],
        env={
            "GOOGLE_SERVICE_ACCOUNT_JSON": os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", ""),
            "GOOGLE_SHEETS_SPREADSHEET_ID": os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID", ""),
        },
    )


async def test_sheet(sheet_name: str):
    """Test append and read for a specific sheet."""
    print(f"\n{'='*50}")
    print(f"Testing: {sheet_name}")
    print('='*50)
    
    async with stdio_client(await get_session()) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            
            # 1. Append test row
            test_row = [
                f"Test-{sheet_name[:10]}",  # Company (unique per sheet)
                "MCP Agent",                 # Contact Name
                "mcp@test.ai",              # Contact Email
                "Test Position",            # Position
                "pending",                  # Status
                "Test Role",                # Role at Company
                f"Test for {sheet_name}"    # Notes
            ]
            
            print(f"[1] Appending row to '{sheet_name}'...")
            result = await s.call_tool("append_row", {
                "range": f"'{sheet_name}'!A:G",
                "values": [test_row]
            })
            data = json.loads(result.content[0].text)
            print(f"    Result: {data}")
            
            # 2. Read back
            print(f"[2] Reading from '{sheet_name}'...")
            result = await s.call_tool("read_range", {
                "range": f"'{sheet_name}'!A:G"
            })
            rows = json.loads(result.content[0].text)
            print(f"    Found {len(rows)} rows")
            
            # Show last row (should be our test row)
            if rows:
                print(f"    Last row: {rows[-1]}")
            
            print(f"[OK] {sheet_name} working!")
            return True


async def test_all_sheets():
    """Test all sheets."""
    print("\n" + "="*60)
    print("GOOGLE SHEETS MCP - FULL TEST")
    print("="*60)
    print(f"Spreadsheet: {os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID', 'NOT SET')[:30]}...")
    
    results = {}
    
    for sheet in ALL_SHEETS:
        try:
            await test_sheet(sheet)
            results[sheet] = "PASS"
        except Exception as e:
            print(f"[ERROR] {sheet}: {e}")
            results[sheet] = f"FAIL: {e}"
    
    # Summary
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    for sheet, status in results.items():
        icon = "[OK]" if status == "PASS" else "[X]"
        print(f"  {icon} {sheet}: {status}")
    
    passed = sum(1 for s in results.values() if s == "PASS")
    print(f"\n{passed}/{len(ALL_SHEETS)} sheets passed")
    
    if passed == len(ALL_SHEETS):
        print("\nAll tests passed! Check your Google Sheet for new rows.")
    else:
        print("\nSome tests failed. Check error messages above.")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):
        print("[ERROR] GOOGLE_SERVICE_ACCOUNT_JSON not set in .env")
        sys.exit(1)
    
    if not os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID"):
        print("[ERROR] GOOGLE_SHEETS_SPREADSHEET_ID not set in .env")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        # Test specific sheet
        asyncio.run(test_sheet(sys.argv[1]))
    else:
        # Test all sheets
        asyncio.run(test_all_sheets())
