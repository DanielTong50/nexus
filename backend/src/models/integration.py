"""User integration models for OAuth tokens storage."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserIntegration(BaseModel):
    """Represents a user's connection to an external service.
    
    Stored in MongoDB collection: user_integrations
    Index: (user_id, provider) for fast lookup
    """
    
    user_id: str = Field(..., description="Internal user identifier")
    provider: str = Field(..., description="Provider ID (google, slack, etc.)")
    
    # OAuth tokens (encrypted at rest)
    access_token: str = Field(..., description="Encrypted access token")
    refresh_token: Optional[str] = Field(None, description="Encrypted refresh token")
    token_expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    
    # Provider-specific info
    scopes: list[str] = Field(default_factory=list, description="Granted OAuth scopes")
    provider_user_id: Optional[str] = Field(None, description="User ID from provider")
    provider_user_name: Optional[str] = Field(None, description="Username/email from provider")
    provider_workspace_id: Optional[str] = Field(None, description="Workspace/team ID (for Slack, Notion)")
    provider_workspace_name: Optional[str] = Field(None, description="Workspace name")
    
    # Metadata
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = Field(None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "provider": "slack",
                "access_token": "encrypted_token_here",
                "refresh_token": None,
                "token_expires_at": None,
                "scopes": ["chat:write", "channels:read"],
                "provider_user_id": "U123ABC",
                "provider_user_name": "john.doe",
                "provider_workspace_id": "T456DEF",
                "provider_workspace_name": "My Workspace",
                "connected_at": "2024-01-17T12:00:00Z",
            }
        }


class IntegrationStatus(BaseModel):
    """Response model for integration status check."""
    
    provider: str
    connected: bool
    provider_user_name: Optional[str] = None
    provider_workspace_name: Optional[str] = None
    connected_at: Optional[datetime] = None
    scopes: list[str] = Field(default_factory=list)


class ProviderInfo(BaseModel):
    """Response model for available provider info."""
    
    id: str
    name: str
    description: str
