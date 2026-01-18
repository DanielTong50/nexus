"""OAuth provider configurations for Nexus integrations.

Each provider defines the OAuth endpoints, scopes, and metadata needed
for the authorization flow.
"""

from typing import TypedDict


class OAuthProviderConfig(TypedDict):
    """Configuration for an OAuth provider."""
    name: str
    description: str
    authorize_url: str
    token_url: str
    scopes: list[str]
    # Optional fields
    revoke_url: str | None
    user_info_url: str | None
    supports_refresh: bool


OAUTH_PROVIDERS: dict[str, OAuthProviderConfig] = {
    "google": {
        "name": "Google",
        "description": "Connect Google Sheets, Docs, and Calendar",
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/documents.readonly",
            "https://www.googleapis.com/auth/calendar.readonly",
            "openid",
            "email",
            "profile",
        ],
        "revoke_url": "https://oauth2.googleapis.com/revoke",
        "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "supports_refresh": True,
    },
    "slack": {
        "name": "Slack",
        "description": "Post messages and read channel history",
        "authorize_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "scopes": [
            "chat:write",
            "channels:read",
            "channels:history",
            "channels:join",
        ],
        "revoke_url": "https://slack.com/api/auth.revoke",
        "user_info_url": "https://slack.com/api/auth.test",
        "supports_refresh": False,  # Slack tokens don't expire
    },
    "notion": {
        "name": "Notion",
        "description": "Access Notion databases and pages",
        "authorize_url": "https://api.notion.com/v1/oauth/authorize",
        "token_url": "https://api.notion.com/v1/oauth/token",
        "scopes": [],  # Notion uses workspace-level access, not granular scopes
        "revoke_url": None,  # Notion doesn't have a revoke endpoint
        "user_info_url": None,  # User info comes with token response
        "supports_refresh": False,  # Notion tokens don't expire
    },
    "github": {
        "name": "GitHub",
        "description": "Access repositories, issues, and pull requests",
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scopes": [
            "repo",
            "read:org",
        ],
        "revoke_url": None,  # GitHub uses API to revoke
        "user_info_url": "https://api.github.com/user",
        "supports_refresh": False,  # GitHub OAuth tokens don't expire
    },
    "calendly": {
        "name": "Calendly",
        "description": "Access scheduling links and events",
        "authorize_url": "https://auth.calendly.com/oauth/authorize",
        "token_url": "https://auth.calendly.com/oauth/token",
        "scopes": ["default"],
        "revoke_url": "https://auth.calendly.com/oauth/revoke",
        "user_info_url": "https://api.calendly.com/users/me",
        "supports_refresh": True,
    },
}


def get_provider_config(provider: str) -> OAuthProviderConfig | None:
    """Get configuration for a specific provider."""
    return OAUTH_PROVIDERS.get(provider)


def list_providers() -> list[dict]:
    """List all available providers with basic info."""
    return [
        {
            "id": provider_id,
            "name": config["name"],
            "description": config["description"],
        }
        for provider_id, config in OAUTH_PROVIDERS.items()
    ]
