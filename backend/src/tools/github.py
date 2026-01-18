"""
GitHub tools for Nexus.

Provides tools for GitHub issue and PR management.
Works without MCP by using mock data.
"""

from langchain_core.tools import tool


DEFAULT_REPO = "jimmysamportfolio/nexus"


@tool
async def create_github_issue(
    title: str,
    description: str,
    repo: str = "",
    labels: str = ""
) -> str:
    """Create a new GitHub issue.

    Args:
        title: Issue title
        description: Issue description in markdown
        repo: Repository name (e.g., 'owner/repo')
        labels: Comma-separated labels

    Returns:
        Issue confirmation with link
    """
    repo = repo or DEFAULT_REPO
    issue_number = abs(hash(title)) % 1000 + 100

    labels_list = [l.strip() for l in labels.split(",")] if labels else []
    labels_str = ", ".join(labels_list) if labels_list else "None"

    return f"""GitHub Issue Created:

Repository: {repo}
Issue #: {issue_number}
Title: {title}
Labels: {labels_str}

Description:
{description[:300]}...

Link: https://github.com/{repo}/issues/{issue_number}"""


@tool
async def check_pr_status(repo: str = "", pr_number: int = 0) -> str:
    """Check the status of pull requests.

    Args:
        repo: Repository name (optional)
        pr_number: Specific PR number (0 for all open PRs)

    Returns:
        PR status summary
    """
    repo = repo or DEFAULT_REPO

    if pr_number > 0:
        return f"""Pull Request #{pr_number} Status:

Repository: {repo}
Title: Feature implementation
Author: @developer
Status: Open
Reviews: 1 approved, 1 pending
Checks: All passing

Files: 5 changed (+234, -12)
Last Updated: 2 hours ago

Link: https://github.com/{repo}/pull/{pr_number}"""

    return f"""Open PRs in {repo}:

#42 - Add authentication system
  Author: @dev1 | Status: Ready for review | Checks: Passing

#41 - Fix API rate limiting
  Author: @dev2 | Status: Changes requested | Checks: Passing

#40 - Update documentation
  Author: @dev3 | Status: Draft | Checks: Pending

Total: 3 open PRs, 1 needs review"""


@tool
async def get_repo_updates(repo: str = "", days: int = 7) -> str:
    """Get recent repository activity.

    Args:
        repo: Repository name (optional)
        days: Number of days to look back

    Returns:
        Activity summary
    """
    repo = repo or DEFAULT_REPO

    return f"""Repository Activity - {repo} (last {days} days):

Recent Commits:
- feat: Add user authentication (3 days ago)
- fix: Resolve API rate limiting (2 days ago)
- docs: Update README (1 day ago)
- refactor: Clean up API routes (today)

Pull Requests:
- 2 merged, 3 open, 1 closed without merge

Issues:
- 5 opened, 3 closed, 2 in progress

Contributors: 5 active this week
Branches: 8 total, 3 active"""


@tool
async def assign_issue(
    issue_number: int,
    assignee: str,
    repo: str = ""
) -> str:
    """Assign a team member to an issue.

    Args:
        issue_number: Issue number to assign
        assignee: GitHub username to assign
        repo: Repository name (optional)

    Returns:
        Confirmation
    """
    repo = repo or DEFAULT_REPO

    return f"""Issue Assignment Updated:

Repository: {repo}
Issue #: {issue_number}
Assigned to: @{assignee}

The assignee has been notified via GitHub notification."""


@tool
async def list_open_issues(repo: str = "", labels: str = "") -> str:
    """List open issues in a repository.

    Args:
        repo: Repository name (optional)
        labels: Filter by labels (comma-separated)

    Returns:
        List of open issues
    """
    repo = repo or DEFAULT_REPO
    label_filter = f" with labels [{labels}]" if labels else ""

    return f"""Open Issues in {repo}{label_filter}:

#55 - Login bug on mobile
  Labels: bug, high-priority
  Assigned: @dev1
  Created: 2 days ago

#54 - Feature request: Dark mode
  Labels: enhancement
  Assigned: @dev2
  Created: 5 days ago

#52 - Improve error messages
  Labels: enhancement, good-first-issue
  Assigned: Unassigned
  Created: 1 week ago

Total: 3 open issues"""


# Export all tools for agent binding
GITHUB_TOOLS = [
    create_github_issue,
    check_pr_status,
    get_repo_updates,
    assign_issue,
    list_open_issues,
]
