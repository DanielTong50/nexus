"""
Social media and outreach tools for Nexus.

Provides tools for drafting LinkedIn messages, emails, and social media posts.
"""

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings


def get_llm():
    """Get the LLM instance for content generation."""
    return ChatGoogleGenerativeAI(
        model=settings.agent_model,
        google_api_key=settings.google_api_key,
        temperature=0.7,
    )


@tool
async def draft_linkedin_outreach(
    company_name: str,
    contact_name: str,
    role: str,
    event_name: str = "Blueprint",
    partnership_type: str = "sponsor"
) -> str:
    """Draft a LinkedIn outreach message for a potential partner.

    Args:
        company_name: Name of the company
        contact_name: Name of the contact person
        role: Their role at the company
        event_name: Name of your event
        partnership_type: Type of partnership (sponsor, speaker, mentor, etc.)

    Returns:
        Draft LinkedIn message
    """
    prompt = f"""Draft a professional but friendly LinkedIn outreach message for:
- Contact: {contact_name}, {role} at {company_name}
- Event: {event_name}
- Partnership type: {partnership_type}

Keep it concise (under 300 characters for LinkedIn), professional, and personalized.
Focus on value proposition for them. End with a clear call to action.
Return only the message text, no explanations."""

    try:
        llm = get_llm()
        response = await llm.ainvoke(prompt)
        return f"LinkedIn Draft for {contact_name}:\n\n{response.content}"
    except Exception as e:
        # Fallback to template
        return f"""LinkedIn Draft for {contact_name}:

Hi {contact_name}! I'm reaching out from {event_name}. We're looking for {partnership_type}s and {company_name}'s work in this space caught our attention. Would love to explore a potential collaboration. Open to a quick chat?"""


@tool
async def draft_email_outreach(
    company_name: str,
    contact_name: str,
    contact_email: str,
    role: str,
    event_name: str = "Blueprint",
    partnership_type: str = "sponsor",
    event_date: str = "TBD",
    expected_attendees: int = 500
) -> str:
    """Draft an email for partner outreach.

    Args:
        company_name: Name of the company
        contact_name: Name of the contact person
        contact_email: Email address
        role: Their role at the company
        event_name: Name of your event
        partnership_type: Type of partnership
        event_date: Date of the event
        expected_attendees: Expected number of attendees

    Returns:
        Draft email with subject line
    """
    prompt = f"""Draft a professional sponsorship/partnership outreach email:

To: {contact_name}, {role} at {company_name}
Event: {event_name}
Partnership type: {partnership_type}
Event date: {event_date}
Expected attendees: {expected_attendees}

Include:
1. Clear subject line
2. Brief intro about the event
3. Value proposition for them
4. Specific partnership benefits
5. Clear call to action

Format as:
Subject: [subject line]

[email body]"""

    try:
        llm = get_llm()
        response = await llm.ainvoke(prompt)
        return f"Email Draft:\n\n{response.content}"
    except Exception as e:
        # Fallback to template
        return f"""Email Draft:

Subject: Partnership Opportunity - {event_name}

Dear {contact_name},

I hope this email finds you well. My name is [Your Name], and I'm reaching out on behalf of {event_name}, taking place on {event_date}.

We're expecting {expected_attendees}+ attendees and are looking for {partnership_type}s like {company_name} to help make this event a success.

As a {partnership_type}, you would receive:
- Brand visibility to {expected_attendees}+ attendees
- Speaking/workshop opportunities
- Direct access to talented students and professionals

Would you be open to a brief call to discuss how we might work together?

Best regards,
[Your Name]"""


@tool
async def draft_social_post(
    platform: str,
    content_type: str,
    topic: str,
    event_name: str = "Blueprint",
    tone: str = "professional but engaging"
) -> str:
    """Draft a social media post for the event.

    Args:
        platform: Social media platform (instagram, linkedin, twitter)
        content_type: Type of content (announcement, sponsor_shoutout, countdown, recap)
        topic: What the post is about
        event_name: Name of the event
        tone: Desired tone

    Returns:
        Draft social media post
    """
    char_limits = {
        "instagram": 2200,
        "linkedin": 3000,
        "twitter": 280,
    }
    limit = char_limits.get(platform.lower(), 1000)

    prompt = f"""Draft a {platform} post for {event_name}:

Content type: {content_type}
Topic: {topic}
Tone: {tone}
Character limit: {limit}

Include relevant emojis and hashtags. Make it engaging and shareable.
Return only the post text."""

    try:
        llm = get_llm()
        response = await llm.ainvoke(prompt)
        return f"{platform.title()} Post Draft:\n\n{response.content}"
    except Exception as e:
        return f"""{platform.title()} Post Draft:

{topic}

Join us at {event_name}!

#tech #hackathon #innovation"""


@tool
async def draft_thank_you_message(
    company_name: str,
    contact_name: str,
    partnership_type: str,
    contribution: str = ""
) -> str:
    """Draft a thank you message for a confirmed partner.

    Args:
        company_name: Name of the company
        contact_name: Name of the contact
        partnership_type: Type of partnership
        contribution: What they contributed (optional)

    Returns:
        Thank you message draft
    """
    prompt = f"""Draft a warm thank you message for:
- Company: {company_name}
- Contact: {contact_name}
- Partnership type: {partnership_type}
- Contribution: {contribution if contribution else 'their support'}

Keep it genuine and professional. Express excitement about the partnership."""

    try:
        llm = get_llm()
        response = await llm.ainvoke(prompt)
        return f"Thank You Message:\n\n{response.content}"
    except Exception as e:
        return f"""Thank You Message:

Dear {contact_name},

Thank you so much for confirming {company_name}'s {partnership_type} partnership! We're thrilled to have you on board.

Your support means a lot to our team and will help make this event truly special. We'll be in touch soon with next steps.

Best regards,
The Event Team"""


@tool
async def generate_campaign_ideas(
    event_name: str,
    target_audience: str,
    num_ideas: int = 3
) -> str:
    """Generate marketing campaign ideas for the event.

    Args:
        event_name: Name of the event
        target_audience: Who we're targeting
        num_ideas: Number of ideas to generate

    Returns:
        List of campaign ideas
    """
    prompt = f"""Generate {num_ideas} creative marketing campaign ideas for:

Event: {event_name}
Target audience: {target_audience}

For each idea include:
1. Campaign name
2. Brief description (2-3 sentences)
3. Key channels to use
4. Expected impact

Be creative and actionable."""

    try:
        llm = get_llm()
        response = await llm.ainvoke(prompt)
        return f"Campaign Ideas:\n\n{response.content}"
    except Exception as e:
        return f"""Campaign Ideas:

1. **Early Bird Buzz**
   Launch early registration with exclusive perks. Use Instagram countdown stickers and email drips.

2. **Speaker Spotlight Series**
   Weekly social posts featuring confirmed speakers. Great for LinkedIn and Twitter engagement.

3. **Student Ambassador Program**
   Recruit campus ambassadors for word-of-mouth marketing. Incentivize with event perks."""


@tool
async def create_content_timeline(
    event_name: str,
    event_date: str,
    content_types: str = "social, email, blog"
) -> str:
    """Create a content marketing timeline for an event.

    Args:
        event_name: Name of the event
        event_date: Date of the event
        content_types: Types of content to plan

    Returns:
        Content timeline
    """
    return f"""Content Timeline for {event_name}:

4 weeks before ({event_date}):
- Announcement post (all platforms)
- Speaker/sponsor reveal thread
- Early bird email blast

2 weeks before:
- Behind-the-scenes content
- FAQ post
- Reminder email

1 week before:
- Final countdown posts
- Last chance registration email
- Agenda reveal

Day of:
- Live updates
- Story/reel content
- Real-time engagement

Post-event:
- Thank you posts
- Recap blog
- Feedback survey"""


@tool
async def schedule_instagram_post(
    content: str,
    scheduled_time: str,
    image_description: str = ""
) -> str:
    """Schedule an Instagram post (requires HITL approval).

    Args:
        content: Post caption
        scheduled_time: When to post
        image_description: Description of the image to use

    Returns:
        Confirmation of scheduled post
    """
    return f"""[PENDING APPROVAL] Instagram Post Scheduled:

Time: {scheduled_time}
Caption: {content[:100]}...
Image: {image_description or 'To be added'}

This post requires your approval before publishing."""


@tool
async def schedule_linkedin_post(
    content: str,
    scheduled_time: str
) -> str:
    """Schedule a LinkedIn post (requires HITL approval).

    Args:
        content: Post content
        scheduled_time: When to post

    Returns:
        Confirmation of scheduled post
    """
    return f"""[PENDING APPROVAL] LinkedIn Post Scheduled:

Time: {scheduled_time}
Content Preview:
{content[:200]}...

This post requires your approval before publishing."""


@tool
async def update_sponsor_in_content(
    sponsor_name: str,
    content_type: str,
    update_action: str
) -> str:
    """Update sponsor mentions in marketing content.

    Args:
        sponsor_name: Name of the sponsor
        content_type: Type of content to update
        update_action: What to update (add, remove, update tier)

    Returns:
        Confirmation of update
    """
    return f"""Sponsor Content Update:

Sponsor: {sponsor_name}
Content Type: {content_type}
Action: {update_action}

All {content_type} content has been updated to reflect the change."""


# Export tools for agent binding
SOCIAL_TOOLS = [
    draft_linkedin_outreach,
    draft_email_outreach,
    draft_social_post,
    draft_thank_you_message,
    generate_campaign_ideas,
    create_content_timeline,
    schedule_instagram_post,
    schedule_linkedin_post,
    update_sponsor_in_content,
]
