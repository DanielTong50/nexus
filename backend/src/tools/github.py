"""
GitHub tools for Nexus.

Provides issue tracking and repository monitoring via MCP.
"""

from typing import Optional

from langchain_core.tools import tool

from src.services.mcp_client import mcp_client


# =============================================================================
# GITHUB CONFIGURATION
# TODO: Can be replaced with database lookup for user-specific repos
# =============================================================================
DEFAULT_REPOS = [
    "jimmysamportfolio/nexus",
    # Add more repos as needed
]


def get_default_repo() -> str:
    """Get the default repository for operations."""
    return DEFAULT_REPOS[0] if DEFAULT_REPOS else ""


@tool
async def create_github_issue(
    repo: str,
    title: str,
    description: str,
    labels: list[str] = [],
    user_id: Optional[str] = None
) -> str:
    """Create a new GitHub issue.
    
    Args:
        repo: Repository name (e.g., 'owner/repo')
        title: Issue title
        description: Issue description in markdown
        labels: List of labels to apply
        user_id: Optional user ID for per-user OAuth token
        
    Returns:
        Issue URL or error message
    """
    try:
        result = await mcp_client.call_github_tool(
            "create_issue",
            {
                "repo": repo or get_default_repo(),
                "title": title,
                "body": description,
                "labels": labels
            },
            user_id=user_id
        )
        
        if isinstance(result, dict) and result.get("success"):
            return f"Created issue #{result['issue_number']}: {result['url']}"
        elif isinstance(result, dict) and result.get("error"):
            return f"Failed to create issue: {result['error']}"
        return f"Created issue in {repo}"
    except Exception as e:
        return f"Failed to create issue: {str(e)}"


@tool
async def check_pr_status(
    repo: str = "",
    user_id: Optional[str] = None
) -> str:
    """Summarize open pull requests.
    
    Args:
        repo: Repository name (optional, uses default if not provided)
        user_id: Optional user ID for per-user OAuth token
        
    Returns:
        Summary of open PRs with status
    """
    try:
        result = await mcp_client.call_github_tool(
            "get_pr_summary",
            {"repo": repo or get_default_repo()},
            user_id=user_id
        )
        
        if isinstance(result, dict):
            if result.get("error"):
                return f"Failed to get PR status: {result['error']}"
            
            total = result.get("total_open", 0)
            needs_review = result.get("needs_review", 0)
            prs = result.get("pull_requests", [])
            
            if total == 0:
                return f"No open PRs in {repo or get_default_repo()}"
            
            lines = [f"Open PRs in {repo or get_default_repo()}: {total} total, {needs_review} need review"]
            for pr in prs[:5]:  # Show top 5
                status = " (draft)" if pr.get("draft") else ""
                lines.append(f"  - #{pr['number']}: {pr['title']} by @{pr['author']}{status}")
            
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Failed to get PR status: {str(e)}"


@tool
async def get_repo_updates(
    repo: str = "", 
    days: int = 7,
    user_id: Optional[str] = None
) -> str:
    """Get a list of open issues for a repository.
    
    Args:
        repo: Repository name (optional, uses default)
        days: Not used currently, for future filtering
        user_id: Optional user ID for per-user OAuth token
        
    Returns:
        Summary of open issues
    """
    try:
        result = await mcp_client.call_github_tool(
            "list_issues",
            {"repo": repo or get_default_repo(), "limit": 10},
            user_id=user_id
        )
        
        if isinstance(result, dict):
            if result.get("error"):
                return f"Failed to get issues: {result['error']}"
            
            issues = result.get("issues", [])
            count = result.get("count", 0)
            
            if count == 0:
                return f"No open issues in {repo or get_default_repo()}"
            
            lines = [f"Open issues in {repo or get_default_repo()}: {count}"]
            for issue in issues:
                labels = ", ".join(issue.get("labels", [])) or "no labels"
                lines.append(f"  - #{issue['number']}: {issue['title']} [{labels}]")
            
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Failed to get issues: {str(e)}"


@tool
async def assign_issue(repo: str, issue_number: int, assignee: str) -> str:
    """Assign a team member to an issue.
    
    Args:
        repo: Repository name
        issue_number: Issue number to assign
        assignee: GitHub username to assign
        
    Returns:
        Confirmation or error
    """
    # Note: This would need additional MCP tool implementation
    # For now, return a placeholder
    return f"[Not implemented] Would assign #{issue_number} in {repo} to @{assignee}"


# Export all tools for agent binding
GITHUB_TOOLS = [
    create_github_issue,
    check_pr_status,
    get_repo_updates,
    assign_issue,
]
