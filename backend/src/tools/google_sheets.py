"""
Google Sheets tools for Nexus.

Provides read/write access to partnership tracking sheets via MCP client.
"""

from langchain_core.tools import tool

from src.services.mcp_client import mcp_client


# Define sheet types for partnership tracking
SHEET_TYPES = [
    "Coffee Chat Delegates",
    "Boothing Companies",
    "Judges",
    "Mentors",
    "Student Mentors",
    "Workshop Hosts",
]

# Standard columns for partnership sheets
COLUMNS = [
    "Company",
    "Contact Name",
    "Contact Email",
    "Position",
    "Status",
    "Role at Company",
    "Notes",
]


@tool
async def log_partnership(
    sheet_name: str,
    company: str,
    contact_name: str,
    contact_email: str,
    position: str,
    status: str,
    role_at_company: str,
    notes: str = "",
) -> str:
    """Add a new partnership entry to a Google Sheet.
    
    Args:
        sheet_name: Name of the sheet (e.g., 'Boothing Companies')
        company: Company name
        contact_name: Name of the primary contact
        contact_email: Contact's email address
        position: Contact's position at the company
        status: Current status (pending, confirmed, rejected)
        role_at_company: Role/category at the event
        notes: Optional additional notes
        
    Returns:
        Confirmation message or error
    """
    try:
        row = [[company, contact_name, contact_email, position, status, role_at_company, notes]]
        await mcp_client.call_google_sheets_tool(
            "append_row",
            {"range": f"{sheet_name}!A:G", "values": row}
        )
        return f"Added {company} to {sheet_name} with status: {status}"
    except Exception as e:
        return f"Failed to add partnership: {str(e)}"


@tool
async def update_partnership_status(
    sheet_name: str,
    company: str,
    new_status: str
) -> str:
    """Update the status of an existing partnership.
    
    Args:
        sheet_name: Name of the sheet
        company: Company name to update
        new_status: New status value
        
    Returns:
        Confirmation message or error
    """
    try:
        # Read all data from sheet
        data = await mcp_client.call_google_sheets_tool(
            "read_range",
            {"range": f"{sheet_name}!A:G"}
        )
        
        # Find the company row (skip header)
        for i, row in enumerate(data):
            if i == 0:  # Skip header
                continue
            if len(row) > 0 and row[0].lower() == company.lower():
                # Status is column E (index 4), row is i+1 in 1-indexed sheets
                row_num = i + 1
                await mcp_client.call_google_sheets_tool(
                    "update_range",
                    {"range": f"{sheet_name}!E{row_num}", "values": [[new_status]]}
                )
                return f"Updated {company} status to: {new_status}"
        
        return f"Company '{company}' not found in {sheet_name}"
    except Exception as e:
        return f"Failed to update partnership: {str(e)}"


@tool
async def search_partnerships(
    sheet_name: str,
    status_filter: str = ""
) -> str:
    """Search partnerships in a sheet, optionally filtered by status.
    
    Args:
        sheet_name: Name of the sheet to search
        status_filter: Optional status to filter by
        
    Returns:
        Formatted list of partnerships
    """
    try:
        data = await mcp_client.call_google_sheets_tool(
            "read_range",
            {"range": f"{sheet_name}!A:G"}
        )
        
        if not data or len(data) <= 1:
            return f"No partnerships found in {sheet_name}"
        
        results = []
        for i, row in enumerate(data):
            if i == 0:  # Skip header
                continue
            if len(row) < 5:
                continue
            
            company = row[0] if len(row) > 0 else ""
            status = row[4] if len(row) > 4 else ""
            
            # Apply status filter if provided
            if status_filter and status.lower() != status_filter.lower():
                continue
                
            results.append(f"- {company} ({status})")
        
        if not results:
            return f"No partnerships found matching filter: {status_filter}"
        
        return f"Partnerships in {sheet_name}:\n" + "\n".join(results)
    except Exception as e:
        return f"Failed to search partnerships: {str(e)}"


@tool
async def get_partnership_summary(sheet_name: str) -> str:
    """Get a summary of partnership statuses.
    
    Args:
        sheet_name: Name of the sheet
        
    Returns:
        Summary with counts by status
    """
    try:
        data = await mcp_client.call_google_sheets_tool(
            "read_range",
            {"range": f"{sheet_name}!A:G"}
        )
        
        if not data or len(data) <= 1:
            return f"No partnerships found in {sheet_name}"
        
        # Count by status (skip header)
        status_counts: dict[str, int] = {}
        total = 0
        for i, row in enumerate(data):
            if i == 0:
                continue
            if len(row) >= 5:
                status = row[4]
                status_counts[status] = status_counts.get(status, 0) + 1
                total += 1
        
        summary_parts = [f"{status}: {count}" for status, count in status_counts.items()]
        return f"{sheet_name} summary ({total} total): " + ", ".join(summary_parts)
    except Exception as e:
        return f"Failed to get summary: {str(e)}"


@tool
async def list_all_sheets() -> str:
    """List all available partnership sheet types.
    
    Returns:
        List of available sheet names
    """
    return "Available sheets:\n" + "\n".join(f"- {s}" for s in SHEET_TYPES)


@tool
async def get_partnership_details(
    sheet_name: str,
    company: str
) -> str:
    """Get detailed information about a specific partnership.
    
    Args:
        sheet_name: Name of the sheet
        company: Company name to look up
        
    Returns:
        Partnership details or not found message
    """
    try:
        data = await mcp_client.call_google_sheets_tool(
            "read_range",
            {"range": f"{sheet_name}!A:G"}
        )
        
        if not data or len(data) <= 1:
            return f"No data found in {sheet_name}"
        
        headers = data[0] if len(data) > 0 else COLUMNS
        
        for i, row in enumerate(data):
            if i == 0:
                continue
            if len(row) > 0 and row[0].lower() == company.lower():
                details = []
                for j, col in enumerate(headers):
                    val = row[j] if j < len(row) else ""
                    details.append(f"{col}: {val}")
                return f"Partnership details for {company}:\n" + "\n".join(details)
        
        return f"Company '{company}' not found in {sheet_name}"
    except Exception as e:
        return f"Failed to get partnership details: {str(e)}"


@tool
async def add_note_to_partnership(
    sheet_name: str,
    company: str,
    note: str
) -> str:
    """Add a note to an existing partnership.
    
    Args:
        sheet_name: Name of the sheet
        company: Company name
        note: Note to append
        
    Returns:
        Confirmation message or error
    """
    try:
        data = await mcp_client.call_google_sheets_tool(
            "read_range",
            {"range": f"{sheet_name}!A:G"}
        )
        
        for i, row in enumerate(data):
            if i == 0:
                continue
            if len(row) > 0 and row[0].lower() == company.lower():
                row_num = i + 1
                existing_notes = row[6] if len(row) > 6 else ""
                new_notes = f"{existing_notes}; {note}" if existing_notes else note
                
                await mcp_client.call_google_sheets_tool(
                    "update_range",
                    {"range": f"{sheet_name}!G{row_num}", "values": [[new_notes]]}
                )
                return f"Added note to {company}"
        
        return f"Company '{company}' not found in {sheet_name}"
    except Exception as e:
        return f"Failed to add note: {str(e)}"


# Export all tools for agent binding
GOOGLE_SHEETS_TOOLS = [
    log_partnership,
    update_partnership_status,
    search_partnerships,
    get_partnership_summary,
    list_all_sheets,
    get_partnership_details,
    add_note_to_partnership,
]
