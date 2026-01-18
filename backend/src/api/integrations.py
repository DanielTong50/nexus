"""API routes for OAuth integrations.

Provides endpoints for connecting, disconnecting, and managing
external service integrations.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from config.oauth_providers import list_providers, get_provider_config
from src.models.integration import ProviderInfo, IntegrationStatus, UserIntegration
from src.services.oauth_manager import oauth_manager
from src.services.database import get_database


router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/list", response_model=list[ProviderInfo])
async def list_available_providers():
    """List all available OAuth providers."""
    providers = list_providers()
    return [ProviderInfo(**p) for p in providers]


@router.get("/connect/{provider}")
async def connect_provider(
    provider: str,
    user_id: str = Query(..., description="User ID to associate with integration"),
    redirect_url: Optional[str] = Query(None, description="URL to redirect after success"),
):
    """Initiate OAuth flow for a provider.
    
    Redirects the user to the provider's authorization page.
    """
    config = get_provider_config(provider)
    if not config:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")
    
    try:
        auth_url = await oauth_manager.get_authorization_url(provider, user_id)
        return RedirectResponse(url=auth_url, status_code=307)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="State token for CSRF verification"),
    error: Optional[str] = Query(None, description="Error from OAuth provider"),
    error_description: Optional[str] = Query(None),
):
    """Handle OAuth callback from provider.
    
    Exchanges the authorization code for tokens and stores the integration.
    """
    if error:
        raise HTTPException(
            status_code=400, 
            detail=f"OAuth error: {error} - {error_description or ''}"
        )
    
    try:
        # Exchange code for tokens
        integration = await oauth_manager.handle_callback(provider, code, state)
        
        # Store in MongoDB
        db = await get_database()
        
        # Upsert - update if exists, insert if new
        await db.user_integrations.update_one(
            {"user_id": integration.user_id, "provider": provider},
            {"$set": integration.model_dump()},
            upsert=True,
        )
        
        # Return success page (or redirect to frontend)
        return {
            "success": True,
            "provider": provider,
            "user": integration.provider_user_name,
            "workspace": integration.provider_workspace_name,
            "message": f"Successfully connected to {config['name']}!",
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete OAuth: {str(e)}")


@router.get("/status")
async def get_integration_status(
    user_id: str = Query(..., description="User ID to check"),
) -> dict[str, IntegrationStatus]:
    """Get status of all integrations for a user.
    
    Returns a dict mapping provider ID to integration status.
    """
    db = await get_database()
    
    # Find all integrations for this user
    cursor = db.user_integrations.find({"user_id": user_id})
    integrations = await cursor.to_list(length=100)
    
    result = {}
    for integration in integrations:
        result[integration["provider"]] = IntegrationStatus(
            provider=integration["provider"],
            connected=True,
            provider_user_name=integration.get("provider_user_name"),
            provider_workspace_name=integration.get("provider_workspace_name"),
            connected_at=integration.get("connected_at"),
            scopes=integration.get("scopes", []),
        )
    
    return result


@router.delete("/disconnect/{provider}")
async def disconnect_provider(
    provider: str,
    user_id: str = Query(..., description="User ID"),
):
    """Disconnect an integration.
    
    Removes the stored tokens for this provider.
    """
    config = get_provider_config(provider)
    if not config:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")
    
    db = await get_database()
    
    # Delete the integration
    result = await db.user_integrations.delete_one({
        "user_id": user_id,
        "provider": provider,
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return {
        "success": True,
        "message": f"Disconnected from {config['name']}",
    }


@router.get("/{provider}/token")
async def get_valid_token(
    provider: str,
    user_id: str = Query(..., description="User ID"),
) -> dict:
    """Get a valid access token for a provider.
    
    Returns a decrypted, valid access token. Automatically refreshes if expired.
    This endpoint is for internal use by agents/tools.
    """
    config = get_provider_config(provider)
    if not config:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")
    
    db = await get_database()
    
    # Find the integration
    doc = await db.user_integrations.find_one({
        "user_id": user_id,
        "provider": provider,
    })
    
    if not doc:
        raise HTTPException(
            status_code=404, 
            detail=f"No {provider} integration found. Please connect first."
        )
    
    integration = UserIntegration(**doc)
    
    # Check if token needs refresh
    if oauth_manager.is_token_expired(integration):
        if not config["supports_refresh"] or not integration.refresh_token:
            raise HTTPException(
                status_code=401,
                detail=f"{provider} token expired. Please reconnect."
            )
        
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
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token refresh failed: {e}")
    
    # Return decrypted token
    return {
        "access_token": oauth_manager.get_decrypted_token(integration),
        "expires_at": integration.token_expires_at.isoformat() if integration.token_expires_at else None,
    }
