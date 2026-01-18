"""GitHub MCP Server using Python.

This is a local MCP server that exposes GitHub operations
as MCP tools. Uses PyGithub for API access.

Run with: uv run python -m src.mcp_servers.github_server
"""

import asyncio
import json
import os
from typing import Any

from github import Github, GithubException, Auth
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP Server
server = Server("github-server")

# GitHub client (initialized on startup)
github_client: Github | None = None
DEFAULT_OWNER: str = ""


def get_github_client() -> Github:
    """Initialize GitHub client."""
    global github_client, DEFAULT_OWNER
    
    token = os.environ.get("GITHUB_TOKEN", "")
    DEFAULT_OWNER = os.environ.get("GITHUB_DEFAULT_OWNER", "")
    
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    
    auth = Auth.Token(token)
    github_client = Github(auth=auth)
    return github_client


def get_repo(repo_name: str):
    """Get repository object. Handles owner/repo or just repo formats."""
    global github_client, DEFAULT_OWNER
    
    if "/" in repo_name:
        return github_client.get_repo(repo_name)
    elif DEFAULT_OWNER:
        return github_client.get_repo(f"{DEFAULT_OWNER}/{repo_name}")
    else:
        raise ValueError(f"Repository '{repo_name}' needs owner. Use 'owner/repo' format or set GITHUB_DEFAULT_OWNER")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available GitHub tools."""
    return [
        Tool(
            name="create_issue",
            description="Create a new GitHub issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository name (e.g., 'owner/repo' or 'repo' if default owner set)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Issue description in markdown"
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Labels to apply",
                        "default": []
                    }
                },
                "required": ["repo", "title", "body"]
            }
        ),
        Tool(
            name="list_issues",
            description="List open issues for a repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["open", "closed", "all"],
                        "default": "open"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max issues to return",
                        "default": 10
                    }
                },
                "required": ["repo"]
            }
        ),
        Tool(
            name="get_pr_summary",
            description="Get summary of open pull requests",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository name"
                    }
                },
                "required": ["repo"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a GitHub tool."""
    global github_client
    
    if github_client is None:
        get_github_client()
    
    try:
        if name == "create_issue":
            repo = get_repo(arguments["repo"])
            labels = arguments.get("labels", [])
            
            issue = repo.create_issue(
                title=arguments["title"],
                body=arguments["body"],
                labels=labels
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "issue_number": issue.number,
                    "url": issue.html_url,
                    "message": f"Created issue #{issue.number}"
                })
            )]
        
        elif name == "list_issues":
            repo = get_repo(arguments["repo"])
            state = arguments.get("state", "open")
            limit = arguments.get("limit", 10)
            
            # Manually iterate to avoid PyGithub slicing bug on empty results
            issues_iter = repo.get_issues(state=state)
            issue_list = []
            
            count = 0
            for i in issues_iter:
                if count >= limit:
                    break
                
                if i.pull_request:
                    continue
                    
                issue_list.append({
                    "number": i.number,
                    "title": i.title,
                    "state": i.state,
                    "url": i.html_url,
                    "labels": [l.name for l in i.labels]
                })
                count += 1
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "issues": issue_list, 
                    "count": len(issue_list),
                    "debug_repo": repo.full_name,
                    "debug_private": repo.private,
                    "debug_open_issues_count": repo.open_issues_count
                })
            )]
        
        elif name == "get_pr_summary":
            repo = get_repo(arguments["repo"])
            pulls_iter = repo.get_pulls(state="open")
            
            pr_list = []
            count = 0
            for pr in pulls_iter:
                if count >= 20: 
                    break

                reviewers = [r.login for r in pr.get_review_requests()[0]]
                pr_list.append({
                    "number": pr.number,
                    "title": pr.title,
                    "author": pr.user.login,
                    "url": pr.html_url,
                    "reviewers": reviewers,
                    "draft": pr.draft
                })
                count += 1
            
            summary = {
                "total_open": pulls_iter.totalCount,
                "pull_requests": pr_list,
                "needs_review": len([p for p in pr_list if not p["reviewers"]])
            }
            
            return [TextContent(type="text", text=json.dumps(summary))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except GithubException as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e.data), "status": e.status})
        )]
    except Exception as e:
        import traceback
        return [TextContent(type="text", text=json.dumps({
            "error": f"{type(e).__name__}: {str(e)}",
            "traceback": traceback.format_exc()
        }))]


async def main():
    """Run the MCP server."""
    get_github_client()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
