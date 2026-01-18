"""Unit tests for Google Sheets tools.

These tests mock the MCP client to verify tool behavior without real API calls.
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.tools.google_sheets import (
    log_partnership,
    update_partnership_status,
    search_partnerships,
    get_partnership_summary,
    list_all_sheets,
    get_partnership_details,
    add_note_to_partnership,
    GOOGLE_SHEETS_TOOLS,
    COLUMNS,
    SHEET_TYPES,
)


@pytest.fixture
def mock_mcp_client():
    """Mock the MCP client for testing."""
    with patch("src.tools.google_sheets.mcp_client") as mock:
        mock.call_google_sheets_tool = AsyncMock()
        yield mock


class TestLogPartnership:
    """Tests for log_partnership tool."""

    @pytest.mark.asyncio
    async def test_logs_partnership_successfully(self, mock_mcp_client):
        """Should return confirmation on successful add."""
        mock_mcp_client.call_google_sheets_tool.return_value = {"updatedCells": 7}
        
        result = await log_partnership.ainvoke({
            "sheet_name": "Boothing Companies",
            "company": "Google",
            "contact_name": "John Doe",
            "contact_email": "john@google.com",
            "position": "Developer Relations",
            "status": "pending",
            "role_at_company": "Booth Sponsor",
            "notes": "Met at conference"
        })
        
        assert "Added" in result
        assert "Google" in result
        assert "pending" in result

    @pytest.mark.asyncio
    async def test_handles_error(self, mock_mcp_client):
        """Should return error message on failure."""
        mock_mcp_client.call_google_sheets_tool.side_effect = Exception("API error")
        
        result = await log_partnership.ainvoke({
            "sheet_name": "Boothing Companies",
            "company": "Test",
            "contact_name": "Test",
            "contact_email": "test@test.com",
            "position": "Test",
            "status": "pending",
            "role_at_company": "Test"
        })
        
        assert "Failed" in result


class TestUpdatePartnershipStatus:
    """Tests for update_partnership_status tool."""

    @pytest.mark.asyncio
    async def test_updates_existing_company(self, mock_mcp_client):
        """Should update status for existing company."""
        mock_mcp_client.call_google_sheets_tool.side_effect = [
            # First call: read_range
            [
                ["Company", "Contact", "Email", "Position", "Status", "Role", "Notes"],
                ["Google", "John", "john@google.com", "Dev Rel", "pending", "Booth", ""],
            ],
            # Second call: update_range
            {"updatedCells": 1}
        ]
        
        result = await update_partnership_status.ainvoke({
            "sheet_name": "Boothing Companies",
            "company": "Google",
            "new_status": "confirmed"
        })
        
        assert "Updated" in result
        assert "confirmed" in result

    @pytest.mark.asyncio
    async def test_company_not_found(self, mock_mcp_client):
        """Should return not found message."""
        mock_mcp_client.call_google_sheets_tool.return_value = [
            ["Company", "Contact", "Email", "Position", "Status", "Role", "Notes"],
        ]
        
        result = await update_partnership_status.ainvoke({
            "sheet_name": "Boothing Companies",
            "company": "NonExistent",
            "new_status": "confirmed"
        })
        
        assert "not found" in result


class TestSearchPartnerships:
    """Tests for search_partnerships tool."""

    @pytest.mark.asyncio
    async def test_returns_all_partnerships(self, mock_mcp_client):
        """Should return all partnerships."""
        mock_mcp_client.call_google_sheets_tool.return_value = [
            ["Company", "Contact", "Email", "Position", "Status", "Role", "Notes"],
            ["Google", "John", "john@google.com", "Dev", "pending", "Booth", ""],
            ["Microsoft", "Jane", "jane@ms.com", "PM", "confirmed", "Booth", ""],
        ]
        
        result = await search_partnerships.ainvoke({
            "sheet_name": "Boothing Companies"
        })
        
        assert "Google" in result
        assert "Microsoft" in result

    @pytest.mark.asyncio
    async def test_filters_by_status(self, mock_mcp_client):
        """Should filter by status."""
        mock_mcp_client.call_google_sheets_tool.return_value = [
            ["Company", "Contact", "Email", "Position", "Status", "Role", "Notes"],
            ["Google", "John", "john@google.com", "Dev", "pending", "Booth", ""],
            ["Microsoft", "Jane", "jane@ms.com", "PM", "confirmed", "Booth", ""],
        ]
        
        result = await search_partnerships.ainvoke({
            "sheet_name": "Boothing Companies",
            "status_filter": "confirmed"
        })
        
        assert "Microsoft" in result
        assert "Google" not in result


class TestGetPartnershipSummary:
    """Tests for get_partnership_summary tool."""

    @pytest.mark.asyncio
    async def test_counts_by_status(self, mock_mcp_client):
        """Should count partnerships by status."""
        mock_mcp_client.call_google_sheets_tool.return_value = [
            ["Company", "Contact", "Email", "Position", "Status", "Role", "Notes"],
            ["Co1", "A", "a@a.com", "X", "pending", "Y", ""],
            ["Co2", "B", "b@b.com", "X", "pending", "Y", ""],
            ["Co3", "C", "c@c.com", "X", "confirmed", "Y", ""],
        ]
        
        result = await get_partnership_summary.ainvoke({
            "sheet_name": "Boothing Companies"
        })
        
        assert "pending" in result
        assert "confirmed" in result
        assert "3 total" in result


class TestListAllSheets:
    """Tests for list_all_sheets tool."""

    @pytest.mark.asyncio
    async def test_lists_sheet_types(self, mock_mcp_client):
        """Should list available sheet types."""
        result = await list_all_sheets.ainvoke({})
        
        assert "Coffee Chat Delegates" in result
        assert "Boothing Companies" in result


class TestToolsExport:
    """Tests for tools configuration."""

    def test_all_tools_exported(self):
        """Should export all 7 tools."""
        assert len(GOOGLE_SHEETS_TOOLS) == 7

    def test_columns_defined(self):
        """Should have 7 columns defined."""
        assert len(COLUMNS) == 7
        assert "Company" in COLUMNS
        assert "Role at Company" in COLUMNS

    def test_sheet_types_defined(self):
        """Should have sheet types defined."""
        assert len(SHEET_TYPES) >= 4
