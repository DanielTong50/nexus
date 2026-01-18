# Privacy Policy

**Last Updated:** January 2025

## Overview

Nexus ("we", "our", or "the application") is an AI-native event production platform that connects to external services on your behalf. This policy explains how we handle your data.

## Data We Collect

When you connect external services (Google, Slack, Notion, GitHub, Calendly), we store:
- OAuth access tokens (encrypted)
- Your user ID from each connected service
- Workspace/organization names for display purposes

## How We Use Your Data

- **Service Access**: Tokens are used solely to perform actions you request (e.g., updating a Google Sheet, posting to Slack)
- **No Selling**: We do not sell your data to third parties
- **No Advertising**: We do not use your data for advertising purposes

## Data Security

- All OAuth tokens are encrypted at rest using industry-standard encryption (Fernet/AES)
- We use HTTPS for all data transmission
- Access tokens are only decrypted when needed to make API calls on your behalf

## Data Retention

- Your connected service data is retained until you disconnect the integration
- When you disconnect a service, the associated tokens are permanently deleted

## Your Rights

You can:
- **View** which services are connected via the integrations dashboard
- **Disconnect** any service at any time, which deletes stored tokens
- **Request deletion** of all your data by contacting us

## Third-Party Services

Nexus integrates with:
- Google (Sheets, Docs, Calendar)
- Slack
- Notion
- GitHub
- Calendly

Each service has its own privacy policy. By connecting these services, you also agree to their respective policies.

## Contact

For privacy-related questions, please open an issue on our GitHub repository or contact the development team.

---

*This is a simplified privacy policy for a development/hackathon project. For production use, consult with a legal professional.*
