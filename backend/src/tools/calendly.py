"""
Calendly tools for Nexus.

Provides meeting link generation.
"""

from langchain_core.tools import tool


@tool
async def prepare_calendly_link(assignee: str, meeting_type: str) -> str:
    """Generate Calendly link for a team member.
    
    Args:
        assignee: Team member to assign meeting to
        meeting_type: Type of meeting (e.g., 'sponsor_call', 'mentor_intro')
        
    Returns:
        Calendly scheduling link
    """
    # TODO: Implement Calendly API or lookup from settings
    # Different team members may have different Calendly links
    return f"https://calendly.com/{assignee}/{meeting_type}"
