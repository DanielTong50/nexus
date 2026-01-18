"""Token retrieval service for getting user OAuth tokens.

This module provides a simple way for tools and MCP servers to get
valid access tokens for a specific user and provider.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from src.services.oauth_manager import oauth_manager
from src.services.database import get_database
from src.models.integration import UserIntegration
from config.oauth_providers import get_provider_config

logger = logging.getLogger(__name__)


class TokenService:
    """Service for retrieving and managing OAuth tokens."""
    
    async def get_token(self, user_id: str, provider: str) -> Optional[str]:
        """Get a valid access token for a user and provider.
        
        Automatically refreshes expired tokens if possible.
        
        Args:
            user_id: The user's ID
            provider: Provider ID (google, slack, notion, github, calendly)
            
        Returns:
            Decrypted access token or None if not connected
        """
        db = await get_database()
        
        # Find the integration
        doc = await db.user_integrations.find_one({
            "user_id": user_id,
            "provider": provider,
        })
        
        if not doc:
            logger.warning(f"No {provider} integration found for user {user_id}")
            return None
        
        integration = UserIntegration(**doc)
        
        # Check if token needs refresh
        if self._is_expired(integration):
            config = get_provider_config(provider)
            
            if not config or not config.get("supports_refresh"):
                logger.warning(f"{provider} token expired and doesn't support refresh")
                return None
            
            if not integration.refresh_token:
                logger.warning(f"{provider} token expired but no refresh token available")
                return None
            
            # Refresh the token
            try:
                integration = await oauth_manager.refresh_token(integration)
                
                # Update in database
                await db.user_integrations.update_one(
                    {"user_id": user_id, "provider": provider},
                    {"$set": {
                        "access_token": integration.access_token,
                        "refresh_token": integration.refresh_token,
                        "token_expires_at": integration.token_expires_at,
                    }}
                )
                logger.info(f"Refreshed {provider} token for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to refresh {provider} token: {e}")
                return None
        
        # Update last_used timestamp
        await db.user_integrations.update_one(
            {"user_id": user_id, "provider": provider},
            {"$set": {"last_used_at": datetime.utcnow()}}
        )
        
        return oauth_manager.get_decrypted_token(integration)
    
    async def is_connected(self, user_id: str, provider: str) -> bool:
        """Check if a user has connected a provider."""
        db = await get_database()
        doc = await db.user_integrations.find_one({
            "user_id": user_id,
            "provider": provider,
        })
        return doc is not None
    
    async def get_all_connected_providers(self, user_id: str) -> list[str]:
        """Get list of all providers a user has connected."""
        db = await get_database()
        cursor = db.user_integrations.find(
            {"user_id": user_id},
            {"provider": 1}
        )
        docs = await cursor.to_list(length=100)
        return [doc["provider"] for doc in docs]
    
    def _is_expired(self, integration: UserIntegration) -> bool:
        """Check if token is expired (with 5 minute buffer)."""
        if not integration.token_expires_at:
            return False
        return datetime.utcnow() > (integration.token_expires_at - timedelta(minutes=5))


# Singleton instance
token_service = TokenService()
