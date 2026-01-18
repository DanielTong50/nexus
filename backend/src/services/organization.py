"""Organization configuration service.

Manages loading, caching, and updating organization configurations
from MongoDB. Provides the context needed for agents to work with
organization-specific settings.
"""

import logging
from datetime import datetime
from typing import Optional

from src.models.organization import (
    OrganizationConfig,
    create_default_config,
    SlackChannelMapping,
    DataSourceMapping,
    EventConfig,
)
from src.services.database import db_service

logger = logging.getLogger(__name__)

# In-memory cache for org configs (simple caching)
_org_cache: dict[str, OrganizationConfig] = {}

# Default org ID when none specified
DEFAULT_ORG_ID = "default"


class OrganizationService:
    """Service for managing organization configurations."""
    
    def __init__(self):
        self.collection_name = "organization_configs"
    
    @property
    def collection(self):
        """Get the MongoDB collection."""
        return db_service.db[self.collection_name]
    
    async def get_config(self, org_id: str = DEFAULT_ORG_ID) -> OrganizationConfig:
        """Get organization configuration.
        
        Loads from cache if available, otherwise from MongoDB.
        Creates a default config if none exists.
        
        Args:
            org_id: Organization identifier
            
        Returns:
            OrganizationConfig for the organization
        """
        # Check cache first
        if org_id in _org_cache:
            return _org_cache[org_id]
        
        # Load from MongoDB
        try:
            doc = await self.collection.find_one({"org_id": org_id})
            
            if doc:
                # Remove MongoDB _id field
                doc.pop("_id", None)
                config = OrganizationConfig(**doc)
            else:
                # Create default config
                logger.info(f"Creating default config for org: {org_id}")
                config = create_default_config(
                    org_id=org_id,
                    org_name="Organization",
                    event_name="Event"
                )
                # Save to MongoDB
                await self.save_config(config)
            
            # Cache it
            _org_cache[org_id] = config
            return config
            
        except Exception as e:
            logger.error(f"Error loading org config: {e}")
            # Return default config on error
            return create_default_config(org_id, "Organization")
    
    async def save_config(self, config: OrganizationConfig) -> bool:
        """Save organization configuration to MongoDB.
        
        Args:
            config: Configuration to save
            
        Returns:
            True if saved successfully
        """
        try:
            config.updated_at = datetime.utcnow()
            
            await self.collection.update_one(
                {"org_id": config.org_id},
                {"$set": config.model_dump()},
                upsert=True
            )
            
            # Update cache
            _org_cache[config.org_id] = config
            
            logger.info(f"Saved config for org: {config.org_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving org config: {e}")
            return False
    
    async def update_config(
        self,
        org_id: str,
        updates: dict,
    ) -> Optional[OrganizationConfig]:
        """Update specific fields in organization configuration.
        
        Args:
            org_id: Organization identifier
            updates: Dictionary of fields to update
            
        Returns:
            Updated config or None on error
        """
        try:
            updates["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"org_id": org_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                # Clear cache to force reload
                _org_cache.pop(org_id, None)
                return await self.get_config(org_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating org config: {e}")
            return None
    
    async def delete_config(self, org_id: str) -> bool:
        """Delete organization configuration.
        
        Args:
            org_id: Organization identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            result = await self.collection.delete_one({"org_id": org_id})
            _org_cache.pop(org_id, None)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting org config: {e}")
            return False
    
    async def list_configs(self) -> list[OrganizationConfig]:
        """List all organization configurations.
        
        Returns:
            List of all org configs
        """
        try:
            cursor = self.collection.find({"is_active": True})
            configs = []
            async for doc in cursor:
                doc.pop("_id", None)
                configs.append(OrganizationConfig(**doc))
            return configs
        except Exception as e:
            logger.error(f"Error listing org configs: {e}")
            return []
    
    def clear_cache(self, org_id: Optional[str] = None) -> None:
        """Clear organization config cache.
        
        Args:
            org_id: Specific org to clear, or None for all
        """
        if org_id:
            _org_cache.pop(org_id, None)
        else:
            _org_cache.clear()
    
    # Convenience methods for resolving references
    
    async def resolve_channel(
        self,
        reference: str,
        org_id: str = DEFAULT_ORG_ID
    ) -> str:
        """Resolve a channel reference to actual Slack channel.
        
        Args:
            reference: User's channel reference
            org_id: Organization identifier
            
        Returns:
            Actual Slack channel name
        """
        config = await self.get_config(org_id)
        return config.slack_channels.resolve(reference)
    
    async def resolve_data_source(
        self,
        reference: str,
        org_id: str = DEFAULT_ORG_ID
    ) -> str:
        """Resolve a data source reference to actual name.
        
        Args:
            reference: User's data source reference
            org_id: Organization identifier
            
        Returns:
            Actual data source name
        """
        config = await self.get_config(org_id)
        return config.data_sources.resolve(reference)
    
    async def get_prompt_context(
        self,
        org_id: str = DEFAULT_ORG_ID
    ) -> dict:
        """Get organization context for prompt injection.
        
        Args:
            org_id: Organization identifier
            
        Returns:
            Dictionary with org context for prompts
        """
        config = await self.get_config(org_id)
        return config.get_context_for_prompts()


# Global service instance
org_service = OrganizationService()


# Helper function to set up a new organization
async def setup_organization(
    org_id: str,
    org_name: str,
    event_name: str,
    slack_channels: Optional[dict] = None,
    data_sources: Optional[dict] = None,
    sponsorship_tiers: Optional[dict[str, float]] = None,
    sponsorship_goal: float = 100000,
) -> OrganizationConfig:
    """Set up a new organization with custom configuration.
    
    Args:
        org_id: Unique organization identifier
        org_name: Organization display name
        event_name: Primary event name
        slack_channels: Custom Slack channel mappings
        data_sources: Custom data source mappings
        sponsorship_tiers: Custom sponsorship tier amounts
        sponsorship_goal: Fundraising goal
        
    Returns:
        Created OrganizationConfig
    """
    # Build channel mapping
    channels = SlackChannelMapping()
    if slack_channels:
        for key, value in slack_channels.items():
            if hasattr(channels, key):
                setattr(channels, key, value)
            else:
                channels.aliases[key] = value
    
    # Build data source mapping
    sources = DataSourceMapping()
    if data_sources:
        for key, value in data_sources.items():
            if hasattr(sources, key):
                setattr(sources, key, value)
            else:
                sources.aliases[key] = value
    
    # Build event config
    event = EventConfig(
        name=event_name,
        sponsorship_goal=sponsorship_goal,
    )
    if sponsorship_tiers:
        event.sponsorship_tiers = sponsorship_tiers
    
    # Create config
    config = OrganizationConfig(
        org_id=org_id,
        org_name=org_name,
        slack_channels=channels,
        data_sources=sources,
        event=event,
    )
    
    # Save to database
    await org_service.save_config(config)
    
    return config
