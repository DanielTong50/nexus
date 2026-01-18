"""Organization configuration models.

These models define organization-specific settings that customize
the Nexus platform for different organizations. All configuration
is stored in MongoDB - nothing is hardcoded.

Example usage:
    org_config = await org_service.get_config("org_123")
    channel = org_config.resolve_channel("partnerships")  # Returns "#biz-partnerships"
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SlackChannelMapping(BaseModel):
    """Maps logical channel names to actual Slack channels."""
    
    # Core team channels
    partnerships: str = Field(default="#partnerships", description="Channel for partnership updates")
    marketing: str = Field(default="#marketing", description="Channel for marketing team")
    finance: str = Field(default="#finance", description="Channel for finance updates")
    events: str = Field(default="#events", description="Channel for event logistics")
    developers: str = Field(default="#developers", description="Channel for dev team")
    general: str = Field(default="#general", description="General announcements channel")
    
    # Additional mappings for natural language references
    # These map to attribute names (not channel names) so they pick up custom values
    aliases: dict[str, str] = Field(
        default_factory=lambda: {
            "partnerships channel": "partnerships",
            "marketing channel": "marketing",
            "event logistics": "events",
            "event logistics channel": "events",
            "finance channel": "finance",
            "dev channel": "developers",
        },
        description="Natural language aliases to attribute names"
    )
    
    def resolve(self, reference: str) -> str:
        """Resolve a channel reference to actual Slack channel.
        
        Args:
            reference: User's channel reference (e.g., "partnerships channel")
            
        Returns:
            Actual Slack channel name (e.g., "#partnerships")
        """
        normalized = reference.lower().strip()
        
        # Check aliases - aliases map to attribute names, then get the attribute value
        if normalized in self.aliases:
            alias_target = self.aliases[normalized]
            # If alias maps to an attribute name (without #), get the attribute value
            attr_name = alias_target.lstrip("#")
            if hasattr(self, attr_name) and attr_name not in ['aliases', 'resolve']:
                return getattr(self, attr_name)
            # Otherwise return the alias value directly
            return alias_target
        
        # Check direct attribute match
        if hasattr(self, normalized) and normalized not in ['aliases', 'resolve']:
            return getattr(self, normalized)
        
        # Return as-is with # prefix if not found
        return reference if reference.startswith("#") else f"#{reference}"


class DataSourceMapping(BaseModel):
    """Maps logical data source names to actual sheet/database names."""
    
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
    
    # Aliases for natural language references
    aliases: dict[str, str] = Field(
        default_factory=lambda: {
            "boothing partnerships compendium": "boothing_partnerships",
            "boothing partnerships": "boothing_partnerships",
            "event partnerships compendium": "event_partnerships",
            "event partnerships": "event_partnerships",
            "partnership compendium": "boothing_partnerships",
        },
        description="Natural language aliases to data source mappings"
    )
    
    def resolve(self, reference: str) -> str:
        """Resolve a data source reference to actual name.
        
        Args:
            reference: User's data source reference
            
        Returns:
            Actual data source name (sheet name, collection name, etc.)
        """
        normalized = reference.lower().strip()
        
        # Check aliases first
        if normalized in self.aliases:
            attr_name = self.aliases[normalized]
            if hasattr(self, attr_name):
                return getattr(self, attr_name)
        
        # Check direct attribute match
        attr_name = normalized.replace(" ", "_")
        if hasattr(self, attr_name) and attr_name not in ['aliases', 'resolve']:
            return getattr(self, attr_name)
        
        # Return as-is if not found
        return reference


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
            "channels": {
                "partnerships": self.slack_channels.partnerships,
                "marketing": self.slack_channels.marketing,
                "finance": self.slack_channels.finance,
                "events": self.slack_channels.events,
                "developers": self.slack_channels.developers,
            },
            "data_sources": {
                "boothing": self.data_sources.boothing_partnerships,
                "sponsors": self.data_sources.event_partnerships,
                "judges": self.data_sources.judges,
                "mentors": self.data_sources.mentors,
            },
        }


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
