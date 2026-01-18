"""
Google Sheets tools for Nexus.

Provides read/write access to partnership tracking sheets.
Uses mock data when MCP client is not available.
"""

from langchain_core.tools import tool
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Mock data for development/testing
MOCK_PARTNERSHIPS = {
    "Boothing Companies": [
        ["Company", "Contact Name", "Contact Email", "Position", "Status", "Role", "Notes"],
        ["Google", "Sarah Chen", "sarah@google.com", "Developer Relations", "Confirmed", "Platinum Sponsor", "Very enthusiastic"],
        ["Microsoft", "Mike Ross", "mike@microsoft.com", "University Programs", "Confirmed", "Gold Sponsor", ""],
        ["Stripe", "Alex Kumar", "alex@stripe.com", "Partnerships", "Pending", "Gold Sponsor", "Follow up next week"],
        ["Vercel", "Lee Robinson", "lee@vercel.com", "DevRel Lead", "In Discussion", "Silver Sponsor", ""],
        ["MongoDB", "Dev Ittycheria", "dev@mongodb.com", "CEO", "Confirmed", "Silver Sponsor", ""],
    ],
    "Judges": [
        ["Company", "Contact Name", "Contact Email", "Position", "Status", "Role", "Notes"],
        ["OpenAI", "John Smith", "john@openai.com", "Research Lead", "Confirmed", "Judge", ""],
        ["Anthropic", "Jane Doe", "jane@anthropic.com", "Engineer", "Pending", "Judge", ""],
    ],
    "Mentors": [
        ["Company", "Contact Name", "Contact Email", "Position", "Status", "Role", "Notes"],
        ["Netflix", "Bob Wilson", "bob@netflix.com", "Senior Engineer", "Confirmed", "Mentor", ""],
        ["Meta", "Alice Brown", "alice@meta.com", "Tech Lead", "Confirmed", "Mentor", ""],
    ],
}


def _get_mock_data(sheet_name: str) -> list:
    """Get mock data for a sheet."""
    return MOCK_PARTNERSHIPS.get(sheet_name, [])


@tool
async def search_partnership_sheet(
    sheet_name: str,
    status_filter: str = ""
) -> str:
    """Search partnerships in a sheet, optionally filtered by status.

    Args:
        sheet_name: Name of the sheet (e.g., 'Boothing Companies', 'Judges', 'Mentors')
        status_filter: Optional status to filter by (Confirmed, Pending, In Discussion)

    Returns:
        Formatted list of partnerships
    """
    data = _get_mock_data(sheet_name)

    if not data or len(data) <= 1:
        return f"No partnerships found in {sheet_name}"

    results = []
    for i, row in enumerate(data):
        if i == 0:  # Skip header
            continue
        if len(row) < 5:
            continue

        company = row[0] if len(row) > 0 else ""
        contact = row[1] if len(row) > 1 else ""
        status = row[4] if len(row) > 4 else ""
        role = row[5] if len(row) > 5 else ""

        # Apply status filter if provided
        if status_filter and status.lower() != status_filter.lower():
            continue

        results.append(f"- {company}: {contact} ({status}) - {role}")

    if not results:
        return f"No partnerships found matching filter: {status_filter}"

    return f"Partnerships in {sheet_name}:\n" + "\n".join(results)


@tool
async def log_partnership_status(
    sheet_name: str,
    company: str,
    new_status: str,
    notes: str = ""
) -> str:
    """Update the status of an existing partnership.

    Args:
        sheet_name: Name of the sheet
        company: Company name to update
        new_status: New status value (Confirmed, Pending, In Discussion, Rejected)
        notes: Optional notes to add

    Returns:
        Confirmation message
    """
    # In production, this would update Google Sheets via MCP
    # For now, simulate the update
    data = _get_mock_data(sheet_name)

    for row in data[1:]:  # Skip header
        if row[0].lower() == company.lower():
            return f"Updated {company} status to: {new_status}. Notes: {notes or 'N/A'}"

    return f"Company '{company}' not found in {sheet_name}. Would you like to add them as a new entry?"


@tool
async def get_partnership_summary(sheet_name: str = "Boothing Companies") -> str:
    """Get a summary of partnership statuses for a sheet.

    Args:
        sheet_name: Name of the sheet (default: Boothing Companies)

    Returns:
        Summary with counts by status and total raised
    """
    data = _get_mock_data(sheet_name)

    if not data or len(data) <= 1:
        return f"No partnerships found in {sheet_name}"

    status_counts: dict[str, int] = {}
    total = 0

    # Mock amounts for sponsors
    tier_amounts = {
        "Platinum Sponsor": 25000,
        "Gold Sponsor": 15000,
        "Silver Sponsor": 5000,
        "Bronze Sponsor": 2500,
    }

    total_raised = 0
    confirmed_raised = 0

    for i, row in enumerate(data):
        if i == 0:
            continue
        if len(row) >= 5:
            status = row[4]
            role = row[5] if len(row) > 5 else ""
            status_counts[status] = status_counts.get(status, 0) + 1
            total += 1

            amount = tier_amounts.get(role, 0)
            total_raised += amount
            if status == "Confirmed":
                confirmed_raised += amount

    summary_parts = [f"{status}: {count}" for status, count in status_counts.items()]
    status_summary = ", ".join(summary_parts)

    return f"""{sheet_name} Summary:
- Total partners: {total}
- Status breakdown: {status_summary}
- Confirmed funding: ${confirmed_raised:,}
- Pipeline total: ${total_raised:,}
- Goal progress: {int(confirmed_raised / 100000 * 100)}% of $100k target"""


@tool
async def add_partnership(
    sheet_name: str,
    company: str,
    contact_name: str,
    contact_email: str,
    position: str,
    role: str,
    status: str = "Pending"
) -> str:
    """Add a new partnership entry to a sheet.

    Args:
        sheet_name: Name of the sheet
        company: Company name
        contact_name: Primary contact name
        contact_email: Contact email
        position: Contact's position
        role: Partnership role/tier
        status: Initial status (default: Pending)

    Returns:
        Confirmation message
    """
    # In production, this would append to Google Sheets via MCP
    return f"""Added new partnership:
- Company: {company}
- Contact: {contact_name} ({position})
- Email: {contact_email}
- Role: {role}
- Status: {status}

Entry logged to {sheet_name}."""


@tool
async def get_partnership_details(
    company: str,
    sheet_name: str = "Boothing Companies"
) -> str:
    """Get detailed information about a specific partnership.

    Args:
        company: Company name to look up
        sheet_name: Name of the sheet (default: Boothing Companies)

    Returns:
        Partnership details
    """
    data = _get_mock_data(sheet_name)

    for row in data[1:]:  # Skip header
        if row[0].lower() == company.lower():
            return f"""Partnership Details - {row[0]}:
- Contact: {row[1]}
- Email: {row[2]}
- Position: {row[3]}
- Status: {row[4]}
- Role: {row[5]}
- Notes: {row[6] if len(row) > 6 else 'N/A'}"""

    return f"Company '{company}' not found in {sheet_name}"


@tool
async def list_available_sheets() -> str:
    """List all available partnership sheet types.

    Returns:
        List of available sheet names
    """
    sheets = list(MOCK_PARTNERSHIPS.keys())
    return "Available partnership sheets:\n" + "\n".join(f"- {s}" for s in sheets)


# Export tools for agent binding
GOOGLE_SHEETS_TOOLS = [
    search_partnership_sheet,
    log_partnership_status,
    get_partnership_summary,
    add_partnership,
    get_partnership_details,
    list_available_sheets,
]
