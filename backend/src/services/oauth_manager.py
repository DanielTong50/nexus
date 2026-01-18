"""OAuth Manager for handling multi-provider OAuth flows.

Manages authorization URLs, token exchange, storage, and refresh.
Uses Authlib for OAuth 2.0 implementation.
"""

import os
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client
from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer

from config.oauth_providers import get_provider_config, OAUTH_PROVIDERS
from src.models.integration import UserIntegration


class OAuthManager:
    """Manages OAuth 2.0 flows for all providers."""
    
    def __init__(self):
        self._encryption_key = os.environ.get("TOKEN_ENCRYPTION_KEY", "")
        self._redirect_base = os.environ.get("OAUTH_REDIRECT_BASE_URL", "http://localhost:8000")
        self._state_secret = os.environ.get("OAUTH_STATE_SECRET", secrets.token_hex(32))
        
        # Initialize Fernet for token encryption
        if self._encryption_key:
            self._fernet = Fernet(self._encryption_key.encode())
        else:
            self._fernet = None
            
        # State serializer for CSRF protection
        self._state_serializer = URLSafeTimedSerializer(self._state_secret)
    
    def _get_client_credentials(self, provider: str) -> tuple[str, str]:
        """Get OAuth client ID and secret from environment."""
        client_id = os.environ.get(f"{provider.upper()}_OAUTH_CLIENT_ID", "")
        client_secret = os.environ.get(f"{provider.upper()}_OAUTH_CLIENT_SECRET", "")
        
        if not client_id or not client_secret:
            raise ValueError(f"Missing OAuth credentials for {provider}. "
                           f"Set {provider.upper()}_OAUTH_CLIENT_ID and {provider.upper()}_OAUTH_CLIENT_SECRET")
        
        return client_id, client_secret
    
    def _encrypt_token(self, token: str) -> str:
        """Encrypt a token for storage."""
        if not self._fernet:
            # If no encryption key, return as-is (dev mode only!)
            return token
        return self._fernet.encrypt(token.encode()).decode()
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a stored token."""
        if not self._fernet:
            return encrypted_token
        return self._fernet.decrypt(encrypted_token.encode()).decode()
    
    def _generate_state(self, user_id: str, provider: str) -> str:
        """Generate a secure state token for CSRF protection."""
        data = {"user_id": user_id, "provider": provider}
        return self._state_serializer.dumps(data)
    
    def _verify_state(self, state: str, max_age: int = 600) -> dict:
        """Verify and decode a state token. Raises if invalid or expired."""
        return self._state_serializer.loads(state, max_age=max_age)
    
    def get_redirect_uri(self, provider: str) -> str:
        """Get the OAuth callback URI for a provider."""
        return f"{self._redirect_base}/integrations/callback/{provider}"
    
    async def get_authorization_url(self, provider: str, user_id: str) -> str:
        """Generate the OAuth authorization URL for a provider.
        
        Args:
            provider: Provider ID (google, slack, etc.)
            user_id: Internal user ID to associate with the integration
            
        Returns:
            Full authorization URL to redirect user to
        """
        config = get_provider_config(provider)
        if not config:
            raise ValueError(f"Unknown provider: {provider}")
        
        client_id, _ = self._get_client_credentials(provider)
        state = self._generate_state(user_id, provider)
        
        # Build authorization URL
        params = {
            "client_id": client_id,
            "redirect_uri": self.get_redirect_uri(provider),
            "state": state,
            "response_type": "code",
        }
        
        # Add scopes (provider-specific formatting)
        if config["scopes"]:
            if provider == "slack":
                params["scope"] = ",".join(config["scopes"])
            else:
                params["scope"] = " ".join(config["scopes"])
        
        # Provider-specific params
        if provider == "google":
            params["access_type"] = "offline"  # Get refresh token
            params["prompt"] = "consent"  # Always show consent to get refresh token
        elif provider == "notion":
            params["owner"] = "user"
        
        return f"{config['authorize_url']}?{urlencode(params)}"
    
    async def handle_callback(
        self, 
        provider: str, 
        code: str, 
        state: str
    ) -> UserIntegration:
        """Exchange authorization code for tokens and create integration.
        
        Args:
            provider: Provider ID
            code: Authorization code from OAuth callback
            state: State token for CSRF verification
            
        Returns:
            UserIntegration object ready for MongoDB storage
        """
        # Verify state and extract user_id
        try:
            state_data = self._verify_state(state)
            user_id = state_data["user_id"]
            if state_data["provider"] != provider:
                raise ValueError("Provider mismatch in state")
        except Exception as e:
            raise ValueError(f"Invalid or expired state token: {e}")
        
        config = get_provider_config(provider)
        if not config:
            raise ValueError(f"Unknown provider: {provider}")
        
        client_id, client_secret = self._get_client_credentials(provider)
        
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            # Prepare token request
            token_data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.get_redirect_uri(provider),
                "client_id": client_id,
                "client_secret": client_secret,
            }
            
            headers = {"Accept": "application/json"}
            
            # Provider-specific token request handling
            if provider == "notion":
                # Notion requires Basic auth
                import base64
                credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
                headers["Authorization"] = f"Basic {credentials}"
                del token_data["client_id"]
                del token_data["client_secret"]
            
            response = await client.post(
                config["token_url"],
                data=token_data,
                headers=headers,
            )
            
            if response.status_code != 200:
                raise ValueError(f"Token exchange failed: {response.text}")
            
            token_response = response.json()
        
        # Extract tokens (provider-specific response formats)
        access_token = token_response.get("access_token")
        if provider == "slack":
            access_token = token_response.get("access_token")
        
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response.get("expires_in")
        
        # Calculate expiration time
        token_expires_at = None
        if expires_in:
            token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Extract user/workspace info
        provider_user_id = None
        provider_user_name = None
        provider_workspace_id = None
        provider_workspace_name = None
        scopes = []
        
        if provider == "slack":
            provider_user_id = token_response.get("authed_user", {}).get("id")
            provider_workspace_id = token_response.get("team", {}).get("id")
            provider_workspace_name = token_response.get("team", {}).get("name")
            scopes = token_response.get("scope", "").split(",")
        elif provider == "notion":
            provider_workspace_id = token_response.get("workspace_id")
            provider_workspace_name = token_response.get("workspace_name")
            owner = token_response.get("owner", {})
            if owner.get("type") == "user":
                provider_user_id = owner.get("user", {}).get("id")
                provider_user_name = owner.get("user", {}).get("name")
        elif provider == "google":
            scopes = token_response.get("scope", "").split(" ")
            # Fetch user info
            if config["user_info_url"]:
                async with httpx.AsyncClient() as client:
                    user_response = await client.get(
                        config["user_info_url"],
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    if user_response.status_code == 200:
                        user_info = user_response.json()
                        provider_user_id = user_info.get("id")
                        provider_user_name = user_info.get("email")
        elif provider == "github":
            scopes = token_response.get("scope", "").split(",")
            # Fetch user info
            if config["user_info_url"]:
                async with httpx.AsyncClient() as client:
                    user_response = await client.get(
                        config["user_info_url"],
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/json"
                        }
                    )
                    if user_response.status_code == 200:
                        user_info = user_response.json()
                        provider_user_id = str(user_info.get("id"))
                        provider_user_name = user_info.get("login")
        elif provider == "calendly":
            scopes = config["scopes"]
            # Fetch user info
            if config["user_info_url"]:
                async with httpx.AsyncClient() as client:
                    user_response = await client.get(
                        config["user_info_url"],
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    if user_response.status_code == 200:
                        user_info = user_response.json().get("resource", {})
                        provider_user_id = user_info.get("uri", "").split("/")[-1]
                        provider_user_name = user_info.get("email")
        
        # Create integration object
        integration = UserIntegration(
            user_id=user_id,
            provider=provider,
            access_token=self._encrypt_token(access_token),
            refresh_token=self._encrypt_token(refresh_token) if refresh_token else None,
            token_expires_at=token_expires_at,
            scopes=scopes,
            provider_user_id=provider_user_id,
            provider_user_name=provider_user_name,
            provider_workspace_id=provider_workspace_id,
            provider_workspace_name=provider_workspace_name,
            connected_at=datetime.utcnow(),
        )
        
        return integration
    
    async def refresh_token(self, integration: UserIntegration) -> UserIntegration:
        """Refresh an expired access token.
        
        Args:
            integration: Existing integration with refresh token
            
        Returns:
            Updated integration with new access token
        """
        config = get_provider_config(integration.provider)
        if not config or not config["supports_refresh"]:
            raise ValueError(f"Provider {integration.provider} doesn't support token refresh")
        
        if not integration.refresh_token:
            raise ValueError("No refresh token available")
        
        client_id, client_secret = self._get_client_credentials(integration.provider)
        refresh_token = self._decrypt_token(integration.refresh_token)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                headers={"Accept": "application/json"},
            )
            
            if response.status_code != 200:
                raise ValueError(f"Token refresh failed: {response.text}")
            
            token_response = response.json()
        
        # Update integration with new tokens
        integration.access_token = self._encrypt_token(token_response["access_token"])
        
        if token_response.get("refresh_token"):
            integration.refresh_token = self._encrypt_token(token_response["refresh_token"])
        
        if token_response.get("expires_in"):
            integration.token_expires_at = datetime.utcnow() + timedelta(
                seconds=token_response["expires_in"]
            )
        
        return integration
    
    def get_decrypted_token(self, integration: UserIntegration) -> str:
        """Get the decrypted access token for API calls."""
        return self._decrypt_token(integration.access_token)
    
    def is_token_expired(self, integration: UserIntegration) -> bool:
        """Check if an integration's token is expired."""
        if not integration.token_expires_at:
            return False  # No expiration means it doesn't expire
        
        # Add 5 minute buffer
        return datetime.utcnow() > (integration.token_expires_at - timedelta(minutes=5))


# Singleton instance
oauth_manager = OAuthManager()
