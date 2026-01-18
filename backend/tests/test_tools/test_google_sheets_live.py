"""Live integration test for Google Sheets tools.

Run from backend directory:
    uv run python tests/test_tools/test_google_sheets_live.py
"""
import asyncio
import random
import string
from datetime import datetime

from src.services.mcp_client import mcp_client
from src.tools.google_sheets import (
    log_partnership,
    search_partnerships,
    get_partnership_summary,
    update_partnership_status,
    get_partnership_details,
)


def generate_unique_company_name() -> str:
    """Generate a unique company name for testing."""
    suffix = ''.join(random.choices(string.ascii_uppercase, k=4))
    timestamp = datetime.now().strftime("%H%M%S")
    return f"TestCo_{suffix}_{timestamp}"


async def test_live():
    """Run live integration tests against actual Google Sheets."""
    print("=" * 50)
    print("Google Sheets Live Integration Test")
    print("=" * 50)
    
    await mcp_client.start()
    
    # Generate unique company name to avoid conflicts
    company_name = generate_unique_company_name()
    sheet_name = "Boothing Companies"
    
    print(f"\n1. Adding new partnership: {company_name}")
    result = await log_partnership.ainvoke({
        "sheet_name": sheet_name,
        "company": company_name,
        "contact_name": "Test Contact",
        "contact_email": "test@example.com",
        "position": "Engineer",
        "status": "pending",
        "role_at_company": "Sponsor",
        "notes": f"Integration test - {datetime.now().isoformat()}"
    })
    print(f"   Result: {result}")
    
    # Small delay to allow sheet to update
    await asyncio.sleep(1)
    
    print(f"\n2. Searching all partnerships in '{sheet_name}'")
    result = await search_partnerships.ainvoke({"sheet_name": sheet_name})
    print(f"   Result: {result}")
    
    print(f"\n3. Getting partnership summary for '{sheet_name}'")
    result = await get_partnership_summary.ainvoke({"sheet_name": sheet_name})
    print(f"   Result: {result}")
    
    print(f"\n4. Getting details for '{company_name}'")
    result = await get_partnership_details.ainvoke({
        "sheet_name": sheet_name,
        "company": company_name
    })
    print(f"   Result: {result}")
    
    print(f"\n5. Updating status to 'confirmed' for '{company_name}'")
    result = await update_partnership_status.ainvoke({
        "sheet_name": sheet_name,
        "company": company_name,
        "new_status": "confirmed"
    })
    print(f"   Result: {result}")
    
    # Verify the update
    await asyncio.sleep(1)
    print(f"\n6. Verifying status update for '{company_name}'")
    result = await get_partnership_details.ainvoke({
        "sheet_name": sheet_name,
        "company": company_name
    })
    print(f"   Result: {result}")
    
    await mcp_client.stop()
    
    print("\n" + "=" * 50)
    print("Test complete! Check your Google Sheet.")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_live())