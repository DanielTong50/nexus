"""
Tool Requirements Registry

Defines required and optional fields for each tool that may need clarification.
Used by the orchestration layer to check if all required info is present
before routing to agents.
"""

from typing import TypedDict, Optional, Union


class ToolRequirement(TypedDict):
    """Schema for tool requirements."""
    required: list[str]
    optional: list[str]
    questions: dict[str, str]


# Registry of tool requirements
# Keys are tool names that may need clarification
TOOL_REQUIREMENTS: dict[str, ToolRequirement] = {
    "generate_mou_invoice": {
        "required": ["sponsor_company_name", "tier", "contact_name", "contact_email"],
        "optional": ["amount", "attendance_role", "event_name"],
        "questions": {
            "sponsor_company_name": "What is the sponsor company name?",
            "tier": "What sponsorship tier? (Platinum/Gold/Silver/Bronze/Booth/In-Kind)",
            "contact_name": "What is the contact name at the company?",
            "contact_email": "What is the contact's email address?",
            "amount": "What is the sponsorship amount? (Leave blank to use tier default)",
            "attendance_role": "What is their event attendance role? (booth/mentor/judge/networking delegate)",
        }
    },
    "generate_invoice": {
        "required": ["company_name", "amount", "description"],
        "optional": ["due_date"],
        "questions": {
            "company_name": "What is the company name?",
            "amount": "What is the invoice amount?",
            "description": "What is the invoice for?",
            "due_date": "When is the payment due?",
        }
    },
    "log_partnership": {
        "required": ["company_name", "tier", "status"],
        "optional": ["contact_name", "contact_email", "notes"],
        "questions": {
            "company_name": "What is the company name?",
            "tier": "What sponsorship tier?",
            "status": "What is the partnership status? (pending/confirmed/declined)",
        }
    },
}


# Action-to-tool mapping
# Maps high-level actions inferred from classification to specific tools
ACTION_TO_TOOL: dict[str, str] = {
    "generate_mou": "generate_mou_invoice",
    "create_mou": "generate_mou_invoice",
    "draft_mou": "generate_mou_invoice",
    "mou_invoice": "generate_mou_invoice",
    "create_invoice": "generate_invoice",
    "generate_invoice": "generate_invoice",
    "log_partnership": "log_partnership",
    "add_sponsor": "log_partnership",
}


def get_tool_requirements(tool_name: str) -> Optional[ToolRequirement]:
    """Get requirements for a specific tool."""
    return TOOL_REQUIREMENTS.get(tool_name)


def get_missing_fields(
    tool_name: str,
    extracted_entities: dict[str, Optional[str]]
) -> list[str]:
    """
    Check which required fields are missing for a tool.
    
    Args:
        tool_name: Name of the tool
        extracted_entities: Dict of extracted field values
        
    Returns:
        List of missing required field names
    """
    requirements = TOOL_REQUIREMENTS.get(tool_name)
    if not requirements:
        return []
    
    missing = []
    for field in requirements["required"]:
        value = extracted_entities.get(field)
        if not value or value.strip() == "":
            missing.append(field)
    
    return missing


def get_clarification_questions(
    tool_name: str,
    missing_fields: list[str]
) -> list[str]:
    """
    Get clarification questions for missing fields.
    
    Args:
        tool_name: Name of the tool
        missing_fields: List of missing field names
        
    Returns:
        List of question strings to ask the user
    """
    requirements = TOOL_REQUIREMENTS.get(tool_name)
    if not requirements:
        return []
    
    questions = []
    for field in missing_fields:
        question = requirements["questions"].get(field)
        if question:
            questions.append(question)
    
    return questions
