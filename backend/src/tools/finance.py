"""
Finance tools for Nexus.

Provides tools for budget management, invoicing, and financial tracking.
"""

from langchain_core.tools import tool

# Mock budget data
MOCK_BUDGET = {
    "total_budget": 100000,
    "confirmed_sponsorship": 65000,
    "pending_sponsorship": 15000,
    "expenses": {
        "venue": 15000,
        "catering": 8000,
        "marketing": 5000,
        "swag": 3000,
        "prizes": 10000,
        "misc": 2000,
    },
    "remaining": 22000,
}


@tool
async def check_budget_status(category: str = "all") -> str:
    """Check the current budget status.

    Args:
        category: Specific category or 'all' for full overview

    Returns:
        Budget status summary
    """
    if category == "all":
        expenses_list = "\n".join([
            f"  - {k.title()}: ${v:,}"
            for k, v in MOCK_BUDGET["expenses"].items()
        ])
        total_expenses = sum(MOCK_BUDGET["expenses"].values())

        return f"""Budget Overview:

Income:
- Confirmed Sponsorship: ${MOCK_BUDGET['confirmed_sponsorship']:,}
- Pending Sponsorship: ${MOCK_BUDGET['pending_sponsorship']:,}
- Total Target: ${MOCK_BUDGET['total_budget']:,}

Expenses:
{expenses_list}
- Total Expenses: ${total_expenses:,}

Balance:
- Available: ${MOCK_BUDGET['confirmed_sponsorship'] - total_expenses:,}
- Pending + Available: ${MOCK_BUDGET['confirmed_sponsorship'] + MOCK_BUDGET['pending_sponsorship'] - total_expenses:,}"""
    else:
        amount = MOCK_BUDGET["expenses"].get(category.lower(), 0)
        return f"{category.title()} Budget: ${amount:,}"


@tool
async def update_budget_sheet(
    category: str,
    amount: float,
    description: str,
    transaction_type: str = "expense"
) -> str:
    """Log a budget transaction.

    Args:
        category: Budget category
        amount: Transaction amount
        description: Description of the transaction
        transaction_type: 'expense' or 'income'

    Returns:
        Confirmation of logged transaction
    """
    return f"""Budget Transaction Logged:

Type: {transaction_type.title()}
Category: {category.title()}
Amount: ${amount:,.2f}
Description: {description}

Budget sheet has been updated."""


@tool
async def draft_mou(
    sponsor_name: str,
    tier: str,
    amount: float,
    benefits: str
) -> str:
    """Draft a Memorandum of Understanding for a sponsor (requires approval).

    Args:
        sponsor_name: Name of the sponsor company
        tier: Sponsorship tier (Platinum, Gold, Silver, etc.)
        amount: Sponsorship amount
        benefits: Key benefits included

    Returns:
        Draft MOU content
    """
    return f"""[PENDING APPROVAL] Draft MOU:

MEMORANDUM OF UNDERSTANDING
Between: Blueprint Event Team and {sponsor_name}

Sponsorship Details:
- Tier: {tier}
- Amount: ${amount:,.2f}
- Event: Blueprint 2024

Benefits Included:
{benefits}

Terms:
1. Payment due within 30 days of signing
2. Logo placement on all event materials
3. Recognition in opening/closing ceremonies
4. Access to attendee resume book (with consent)

This MOU requires your approval before sending to the sponsor."""


@tool
async def generate_invoice(
    sponsor_name: str,
    contact_email: str,
    amount: float,
    tier: str,
    due_date: str
) -> str:
    """Generate an invoice for a sponsor (requires approval).

    Args:
        sponsor_name: Sponsor company name
        contact_email: Billing contact email
        amount: Invoice amount
        tier: Sponsorship tier
        due_date: Payment due date

    Returns:
        Invoice details
    """
    invoice_number = f"INV-2024-{hash(sponsor_name) % 10000:04d}"

    return f"""[PENDING APPROVAL] Invoice Generated:

Invoice #: {invoice_number}
Bill To: {sponsor_name}
Contact: {contact_email}

Description: {tier} Sponsorship - Blueprint 2024
Amount: ${amount:,.2f}
Due Date: {due_date}

Payment Methods:
- Bank Transfer (details to be provided)
- Check (payable to Blueprint Events)

This invoice requires your approval before sending."""


@tool
async def get_sponsorship_financials(tier: str = "all") -> str:
    """Get financial summary for sponsorships.

    Args:
        tier: Specific tier or 'all'

    Returns:
        Financial summary
    """
    tiers = {
        "Platinum": {"count": 1, "amount": 25000, "total": 25000},
        "Gold": {"count": 2, "amount": 15000, "total": 30000},
        "Silver": {"count": 2, "amount": 5000, "total": 10000},
    }

    if tier != "all" and tier in tiers:
        t = tiers[tier]
        return f"""{tier} Sponsorship:
- Partners: {t['count']}
- Per Partner: ${t['amount']:,}
- Total: ${t['total']:,}"""

    summary = "\n".join([
        f"- {name}: {data['count']} sponsors = ${data['total']:,}"
        for name, data in tiers.items()
    ])
    total = sum(t["total"] for t in tiers.values())

    return f"""Sponsorship Financial Summary:

{summary}

Total Confirmed: ${total:,}
Goal: $100,000
Progress: {int(total/100000*100)}%"""


FINANCE_TOOLS = [
    check_budget_status,
    update_budget_sheet,
    draft_mou,
    generate_invoice,
    get_sponsorship_financials,
]
