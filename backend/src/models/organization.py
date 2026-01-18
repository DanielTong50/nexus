"""Organization configuration models.

These models define organization-specific settings that customize
the Nexus platform for different organizations. All configuration
is stored in MongoDB - nothing is hardcoded.

The LLM is given the available options via get_context_for_prompts() and
outputs exact values directly - no resolution/aliasing needed in Python.

Example usage:
    org_config = await org_service.get_config("org_123")
    context = org_config.get_context_for_prompts()
    # Inject context into LLM prompt, LLM outputs exact channel names
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SlackChannelMapping(BaseModel):
    """Maps logical channel names to actual Slack channels.
    
    The LLM receives all available channels and outputs exact names directly.
    """
    
    # Core team channels
    partnerships: str = Field(default="#partnerships", description="Channel for partnership updates")
    marketing: str = Field(default="#marketing", description="Channel for marketing team")
    finance: str = Field(default="#finance", description="Channel for finance updates")
    events: str = Field(default="#events", description="Channel for event logistics")
    developers: str = Field(default="#developers", description="Channel for dev team")
    general: str = Field(default="#general", description="General announcements channel")
    
    def to_prompt_list(self) -> str:
        """Get formatted list of channels for LLM prompts."""
        return "\n".join([
            f"  - {self.partnerships} (partnerships team)",
            f"  - {self.marketing} (marketing team)",
            f"  - {self.finance} (finance team)",
            f"  - {self.events} (events/logistics team)",
            f"  - {self.developers} (developers team)",
            f"  - {self.general} (general announcements)",
        ])
    
    def as_dict(self) -> dict[str, str]:
        """Get channels as dictionary for structured context."""
        return {
            "partnerships": self.partnerships,
            "marketing": self.marketing,
            "finance": self.finance,
            "events": self.events,
            "developers": self.developers,
            "general": self.general,
        }


class DataSourceMapping(BaseModel):
    """Maps logical data source names to actual sheet/database names.
    
    The LLM receives all available data sources and outputs exact names directly.
    """
    
    # Partnership compendiums (Google Sheets)
    boothing_partnerships: str = Field(
        default="Boothing Companies",
        description="Sheet for sponsors with booth presence"
    )
    event_partnerships: str = Field(
        default="Event Sponsors",
        description="Sheet for general event sponsors"
    )
    judges: str = Field(default="Judges", description="Sheet for hackathon judges")
    mentors: str = Field(default="Mentors", description="Sheet for industry mentors")
    student_mentors: str = Field(default="Student Mentors", description="Sheet for student mentors")
    
    # Notion databases
    marketing_timeline: str = Field(
        default="",
        description="Notion database ID for marketing timeline"
    )
    tasks_database: str = Field(
        default="",
        description="Notion database ID for task tracking"
    )
    
    # MongoDB collections
    delegates_collection: str = Field(default="delegates", description="Collection for delegate data")
    registrations_collection: str = Field(default="registrations", description="Collection for registrations")
    
    def to_prompt_list(self) -> str:
        """Get formatted list of data sources for LLM prompts."""
        lines = [
            "  Google Sheets:",
            f"    - \"{self.boothing_partnerships}\" (boothing/booth sponsors)",
            f"    - \"{self.event_partnerships}\" (event sponsors)",
            f"    - \"{self.judges}\" (hackathon judges)",
            f"    - \"{self.mentors}\" (industry mentors)",
            f"    - \"{self.student_mentors}\" (student mentors)",
            "  MongoDB Collections:",
            f"    - \"{self.delegates_collection}\" (event delegates)",
            f"    - \"{self.registrations_collection}\" (registrations)",
        ]
        if self.marketing_timeline:
            lines.insert(6, "  Notion Databases:")
            lines.insert(7, f"    - marketing_timeline (marketing schedule)")
        return "\n".join(lines)
    
    def as_dict(self) -> dict[str, str]:
        """Get data sources as dictionary for structured context."""
        return {
            "sheets": {
                "boothing_partnerships": self.boothing_partnerships,
                "event_partnerships": self.event_partnerships,
                "judges": self.judges,
                "mentors": self.mentors,
                "student_mentors": self.student_mentors,
            },
            "notion": {
                "marketing_timeline": self.marketing_timeline,
                "tasks_database": self.tasks_database,
            },
            "mongodb": {
                "delegates": self.delegates_collection,
                "registrations": self.registrations_collection,
            },
        }


class EventConfig(BaseModel):
    """Configuration for the organization's primary event."""
    
    name: str = Field(default="Event", description="Event name (e.g., 'Blueprint', 'HackMIT')")
    year: int = Field(default=2026, description="Event year")
    sponsorship_goal: float = Field(default=100000, description="Sponsorship fundraising goal")
    
    # Sponsorship tiers and amounts
    sponsorship_tiers: dict[str, float] = Field(
        default_factory=lambda: {
            "Platinum Sponsor": 25000,
            "Gold Sponsor": 15000,
            "Silver Sponsor": 5000,
            "Bronze Sponsor": 2500,
            "Booth Sponsor": 1500,
        },
        description="Sponsorship tier names and amounts"
    )
    
    # Document templates folder (Google Drive)
    templates_folder_id: str = Field(default="", description="Google Drive folder for MOU/invoice templates")
    mou_template_id: str = Field(default="", description="Google Doc template for MOUs")
    invoice_template_id: str = Field(default="", description="Google Doc template for invoices")


class OrganizationConfig(BaseModel):
    """Complete organization configuration.
    
    This model stores all organization-specific settings in MongoDB,
    making the platform fully customizable without code changes.
    """
    
    # Organization identity
    org_id: str = Field(..., description="Unique organization identifier")
    org_name: str = Field(..., description="Organization display name")
    
    # Configuration sections
    slack_channels: SlackChannelMapping = Field(default_factory=SlackChannelMapping)
    data_sources: DataSourceMapping = Field(default_factory=DataSourceMapping)
    event: EventConfig = Field(default_factory=EventConfig)
    
    # Google integrations
    google_sheets_id: str = Field(default="", description="Primary Google Sheets spreadsheet ID")
    google_drive_folder_id: str = Field(default="", description="Root Google Drive folder ID")
    
    # Custom agent instructions (optional overrides)
    custom_instructions: dict[str, str] = Field(
        default_factory=dict,
        description="Per-agent custom instructions to append to system prompts"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    def get_context_for_prompts(self) -> dict:
        """Get context dictionary for injecting into LLM prompts.
        
        Returns:
            Dict with organization context for prompt templates
        """
        return {
            "org_name": self.org_name,
            "event_name": self.event.name,
            "event_year": self.event.year,
            "sponsorship_goal": self.event.sponsorship_goal,
            "sponsorship_tiers": self.event.sponsorship_tiers,
            "channels": self.slack_channels.as_dict(),
            "data_sources": self.data_sources.as_dict(),
        }
    
    def get_prompt_context_string(self) -> str:
        """Get formatted context string for LLM prompts.
        
        This provides a human-readable format that the LLM can easily parse
        and use when generating structured output with exact values.
        
        Returns:
            Formatted string with all available options
        """
        tiers_str = "\n".join([
            f"    - {name}: ${amount:,.0f}"
            for name, amount in self.event.sponsorship_tiers.items()
        ])
        
        return f"""Organization: {self.org_name}
Event: {self.event.name} {self.event.year}
Sponsorship Goal: ${self.event.sponsorship_goal:,.0f}

Available Slack Channels (use EXACT names including #):
{self.slack_channels.to_prompt_list()}

Available Data Sources (use EXACT names):
{self.data_sources.to_prompt_list()}

Sponsorship Tiers:
{tiers_str}"""


# Default configuration for new organizations
def create_default_config(org_id: str, org_name: str, event_name: str = "Event") -> OrganizationConfig:
    """Create a default organization configuration.
    
    Args:
        org_id: Unique organization identifier
        org_name: Organization display name
        event_name: Primary event name
        
    Returns:
        OrganizationConfig with sensible defaults
    """
    return OrganizationConfig(
        org_id=org_id,
        org_name=org_name,
        event=EventConfig(name=event_name),
    )
