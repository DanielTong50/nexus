"""
Google Sheets tools for Nexus.

Provides read/write access to partnership tracking sheets.
Uses Google Sheets API directly with MongoDB as cache/backup.
"""

from langchain_core.tools import tool
from typing import Optional
import logging
import json

from config.settings import settings
from src.services.database import db_service

logger = logging.getLogger(__name__)

# Google Sheets client (initialized lazily)
_sheets_service = None

# Sheet name to range mapping
SHEET_RANGES = {
    "Boothing Companies": "Boothing Companies!A:G",
    "Judges": "Judges!A:G",
    "Mentors": "Mentors!A:G",
    "Student Mentors": "Student Mentors!A:G",
}

# Expected column headers
COLUMN_HEADERS = ["Company", "Contact Name", "Contact Email", "Position", "Status", "Role", "Notes"]


def _get_sheets_service():
    """Initialize and return Google Sheets API client."""
    global _sheets_service

    if _sheets_service is not None:
        return _sheets_service

    creds_json = settings.google_service_account_json
    spreadsheet_id = settings.google_sheets_spreadsheet_id

    if not creds_json or not spreadsheet_id:
        logger.warning("Google Sheets credentials not configured")
        return None

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds_data = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_data,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )

        _sheets_service = build("sheets", "v4", credentials=credentials)
        logger.info("Google Sheets API client initialized")
        return _sheets_service
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets client: {e}")
        return None


async def _get_data_from_sheets(sheet_name: str) -> list:
    """Fetch data from Google Sheets directly.

    Args:
        sheet_name: Name of the sheet to read

    Returns:
        List of rows from the sheet
    """
    service = _get_sheets_service()
    if not service:
        raise RuntimeError("Google Sheets not configured")

    range_notation = SHEET_RANGES.get(sheet_name, f"{sheet_name}!A:G")
    spreadsheet_id = settings.google_sheets_spreadsheet_id

    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_notation
        ).execute()

        values = result.get("values", [])
        return values
    except Exception as e:
        logger.error(f"Failed to read from Google Sheets: {e}")
        raise


async def _write_to_sheets(sheet_name: str, range_notation: str, values: list) -> bool:
    """Write data to Google Sheets.

    Args:
        sheet_name: Name of the sheet
        range_notation: A1 notation range
        values: 2D array of values

    Returns:
        Success status
    """
    service = _get_sheets_service()
    if not service:
        raise RuntimeError("Google Sheets not configured")

    spreadsheet_id = settings.google_sheets_spreadsheet_id

    try:
        body = {"values": values}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_notation,
            valueInputOption="RAW",
            body=body
        ).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to write to Google Sheets: {e}")
        raise


async def _append_to_sheets(sheet_name: str, values: list) -> bool:
    """Append data to Google Sheets.

    Args:
        sheet_name: Name of the sheet
        values: 2D array of values to append

    Returns:
        Success status
    """
    service = _get_sheets_service()
    if not service:
        raise RuntimeError("Google Sheets not configured")

    range_notation = SHEET_RANGES.get(sheet_name, f"{sheet_name}!A:G")
    spreadsheet_id = settings.google_sheets_spreadsheet_id

    try:
        body = {"values": values}
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_notation,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to append to Google Sheets: {e}")
        raise


async def _get_data_from_mongodb(sheet_name: str) -> list:
    """Fetch data from MongoDB cache.

    Args:
        sheet_name: Name of the sheet/collection

    Returns:
        List of partnership records
    """
    try:
        collection_name = sheet_name.lower().replace(" ", "_")
        collection = db_service.db[f"partnerships_{collection_name}"]

        cursor = collection.find({}, {"_id": 0})
        records = await cursor.to_list(length=1000)

        if not records:
            return []

        # Convert to sheet format (list of lists)
        result = [COLUMN_HEADERS]
        for record in records:
            row = [
                record.get("company", ""),
                record.get("contact_name", ""),
                record.get("contact_email", ""),
                record.get("position", ""),
                record.get("status", ""),
                record.get("role", ""),
                record.get("notes", ""),
            ]
            result.append(row)

        return result
    except Exception as e:
        logger.error(f"Failed to read from MongoDB: {e}")
        return []


async def _save_to_mongodb(sheet_name: str, data: list) -> bool:
    """Save sheet data to MongoDB.

    Args:
        sheet_name: Name of the sheet/collection
        data: List of rows (including header)

    Returns:
        Success status
    """
    try:
        if not data or len(data) <= 1:
            return False

        collection_name = sheet_name.lower().replace(" ", "_")
        collection = db_service.db[f"partnerships_{collection_name}"]

        # Clear existing data and insert fresh
        await collection.delete_many({})

        # Convert rows to documents
        documents = []

        for row in data[1:]:  # Skip header
            if len(row) >= 5:
                doc = {
                    "company": row[0] if len(row) > 0 else "",
                    "contact_name": row[1] if len(row) > 1 else "",
                    "contact_email": row[2] if len(row) > 2 else "",
                    "position": row[3] if len(row) > 3 else "",
                    "status": row[4] if len(row) > 4 else "",
                    "role": row[5] if len(row) > 5 else "",
                    "notes": row[6] if len(row) > 6 else "",
                }
                documents.append(doc)

        if documents:
            await collection.insert_many(documents)
            logger.info(f"Synced {len(documents)} records to MongoDB for {sheet_name}")

        return True
    except Exception as e:
        logger.error(f"Failed to save to MongoDB: {e}")
        return False


async def _get_sheet_data(sheet_name: str) -> list:
    """Get data from Google Sheets, falling back to MongoDB if unavailable.

    This is the main data retrieval function that:
    1. Tries to get fresh data from Google Sheets
    2. Syncs successful data to MongoDB cache
    3. Falls back to MongoDB if Sheets fails

    Args:
        sheet_name: Name of the sheet to read

    Returns:
        List of rows including header
    """
    # Check if credentials are available
    has_credentials = bool(settings.google_service_account_json and settings.google_sheets_spreadsheet_id)

    if has_credentials:
        try:
            # Try Google Sheets first
            data = await _get_data_from_sheets(sheet_name)
            if data:
                # Sync to MongoDB for caching
                await _save_to_mongodb(sheet_name, data)
                return data
        except Exception as e:
            logger.warning(f"Google Sheets unavailable, falling back to MongoDB: {e}")

    # Fall back to MongoDB
    data = await _get_data_from_mongodb(sheet_name)
    if data:
        return data

    # Return empty with headers if nothing found
    return [COLUMN_HEADERS]


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
    try:
        data = await _get_sheet_data(sheet_name)
    except Exception as e:
        return f"Error accessing partnership data: {str(e)}"

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
    try:
        data = await _get_sheet_data(sheet_name)
    except Exception as e:
        return f"Error accessing partnership data: {str(e)}"

    # Find the row to update
    for i, row in enumerate(data):
        if i == 0:  # Skip header
            continue
        if len(row) > 0 and row[0].lower() == company.lower():
            # Found the company - update in Google Sheets
            row_number = i + 1  # 1-indexed for Sheets

            # Update status and notes
            new_row = list(row)
            while len(new_row) < 7:
                new_row.append("")
            new_row[4] = new_status
            if notes:
                new_row[6] = notes

            has_credentials = bool(settings.google_service_account_json and settings.google_sheets_spreadsheet_id)

            if has_credentials:
                try:
                    range_notation = f"{sheet_name}!A{row_number}:G{row_number}"
                    await _write_to_sheets(sheet_name, range_notation, [new_row])

                    # Also update MongoDB
                    collection_name = sheet_name.lower().replace(" ", "_")
                    collection = db_service.db[f"partnerships_{collection_name}"]
                    await collection.update_one(
                        {"company": {"$regex": f"^{company}$", "$options": "i"}},
                        {"$set": {"status": new_status, "notes": notes or row[6] if len(row) > 6 else ""}}
                    )

                    return f"Updated {company} status to: {new_status}. Notes: {notes or 'N/A'}"
                except Exception as e:
                    logger.error(f"Failed to update Google Sheets: {e}")
                    return f"Error updating status: {str(e)}"
            else:
                # Update MongoDB only
                collection_name = sheet_name.lower().replace(" ", "_")
                collection = db_service.db[f"partnerships_{collection_name}"]
                result = await collection.update_one(
                    {"company": {"$regex": f"^{company}$", "$options": "i"}},
                    {"$set": {"status": new_status, "notes": notes}}
                )
                if result.modified_count > 0:
                    return f"Updated {company} status to: {new_status}. Notes: {notes or 'N/A'}"
                return f"Company '{company}' not found in database"

    return f"Company '{company}' not found in {sheet_name}. Would you like to add them as a new entry?"


@tool
async def get_partnership_summary(sheet_name: str = "Boothing Companies") -> str:
    """Get a summary of partnership statuses for a sheet.

    Args:
        sheet_name: Name of the sheet (default: Boothing Companies)

    Returns:
        Summary with counts by status and total raised
    """
    try:
        data = await _get_sheet_data(sheet_name)
    except Exception as e:
        return f"Error accessing partnership data: {str(e)}"

    if not data or len(data) <= 1:
        return f"No partnerships found in {sheet_name}"

    status_counts: dict[str, int] = {}
    total = 0

    # Tier amounts for sponsors
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

    goal = 100000
    progress = int(confirmed_raised / goal * 100) if goal > 0 else 0

    return f"""{sheet_name} Summary:
- Total partners: {total}
- Status breakdown: {status_summary}
- Confirmed funding: ${confirmed_raised:,}
- Pipeline total: ${total_raised:,}
- Goal progress: {progress}% of ${goal:,} target"""


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
    new_row = [company, contact_name, contact_email, position, status, role, ""]

    has_credentials = bool(settings.google_service_account_json and settings.google_sheets_spreadsheet_id)

    if has_credentials:
        try:
            await _append_to_sheets(sheet_name, [new_row])
        except Exception as e:
            logger.error(f"Failed to append to Google Sheets: {e}")
            # Continue to add to MongoDB

    # Also add to MongoDB
    try:
        collection_name = sheet_name.lower().replace(" ", "_")
        collection = db_service.db[f"partnerships_{collection_name}"]

        doc = {
            "company": company,
            "contact_name": contact_name,
            "contact_email": contact_email,
            "position": position,
            "status": status,
            "role": role,
            "notes": "",
        }
        await collection.insert_one(doc)
    except Exception as e:
        logger.error(f"Failed to add to MongoDB: {e}")

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
    try:
        data = await _get_sheet_data(sheet_name)
    except Exception as e:
        return f"Error accessing partnership data: {str(e)}"

    for row in data[1:]:  # Skip header
        if len(row) > 0 and row[0].lower() == company.lower():
            return f"""Partnership Details - {row[0]}:
- Contact: {row[1] if len(row) > 1 else 'N/A'}
- Email: {row[2] if len(row) > 2 else 'N/A'}
- Position: {row[3] if len(row) > 3 else 'N/A'}
- Status: {row[4] if len(row) > 4 else 'N/A'}
- Role: {row[5] if len(row) > 5 else 'N/A'}
- Notes: {row[6] if len(row) > 6 else 'N/A'}"""

    return f"Company '{company}' not found in {sheet_name}"


@tool
async def list_available_sheets() -> str:
    """List all available partnership sheet types.

    Returns:
        List of available sheet names
    """
    sheets = list(SHEET_RANGES.keys())
    return "Available partnership sheets:\n" + "\n".join(f"- {s}" for s in sheets)


@tool
async def sync_sheets_to_mongodb(sheet_name: str = "all") -> str:
    """Sync data from Google Sheets to MongoDB.

    Args:
        sheet_name: Specific sheet or 'all' to sync all sheets

    Returns:
        Sync status message
    """
    sheets_to_sync = list(SHEET_RANGES.keys()) if sheet_name == "all" else [sheet_name]
    results = []

    for sheet in sheets_to_sync:
        try:
            data = await _get_data_from_sheets(sheet)
            if data:
                success = await _save_to_mongodb(sheet, data)
                if success:
                    results.append(f"- {sheet}: Synced {len(data) - 1} records")
                else:
                    results.append(f"- {sheet}: No data to sync")
            else:
                results.append(f"- {sheet}: No data found in Google Sheets")
        except Exception as e:
            results.append(f"- {sheet}: Error - {str(e)}")

    return "Sync Results:\n" + "\n".join(results)


# Export tools for agent binding
GOOGLE_SHEETS_TOOLS = [
    search_partnership_sheet,
    log_partnership_status,
    get_partnership_summary,
    add_partnership,
    get_partnership_details,
    list_available_sheets,
    sync_sheets_to_mongodb,
]
