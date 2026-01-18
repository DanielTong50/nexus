"""Budget and financial tracking models."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import Field

from src.models.base import BaseDocument


class BudgetCategory(BaseDocument):
    """Budget category with allocated and spent amounts."""

    name: str = Field(description="Category name")
    allocated: float = Field(default=0, description="Allocated budget")
    spent: float = Field(default=0, description="Amount spent")
    committed: float = Field(default=0, description="Committed but not spent")
    notes: Optional[str] = Field(default=None, description="Category notes")

    @property
    def remaining(self) -> float:
        """Calculate remaining budget."""
        return self.allocated - self.spent - self.committed

    @property
    def utilization_percent(self) -> float:
        """Calculate utilization percentage."""
        if self.allocated == 0:
            return 0
        return ((self.spent + self.committed) / self.allocated) * 100


class BudgetTransaction(BaseDocument):
    """MongoDB document for budget transactions."""

    event_name: str = Field(description="Event this transaction belongs to")
    category: str = Field(description="Budget category")
    type: Literal["expense", "income", "commitment", "adjustment"] = Field(
        description="Transaction type"
    )
    amount: float = Field(description="Transaction amount")
    description: str = Field(description="Transaction description")
    vendor: Optional[str] = Field(default=None, description="Vendor/source name")
    reference_number: Optional[str] = Field(
        default=None, description="Invoice/receipt reference"
    )
    status: Literal["pending", "approved", "paid", "cancelled"] = Field(
        default="pending", description="Transaction status"
    )
    payment_method: Optional[str] = Field(default=None, description="Payment method")
    payment_date: Optional[datetime] = Field(default=None, description="Date of payment")
    approved_by: Optional[str] = Field(default=None, description="Approver user ID")
    approved_at: Optional[datetime] = Field(default=None, description="Approval timestamp")
    receipt_url: Optional[str] = Field(default=None, description="Receipt/document URL")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    tags: list[str] = Field(default_factory=list, description="Transaction tags")


class SponsorshipRevenue(BaseDocument):
    """MongoDB document for tracking sponsorship revenue."""

    event_name: str = Field(description="Event this revenue belongs to")
    sponsor_name: str = Field(description="Sponsor company name")
    tier: str = Field(description="Sponsorship tier")
    amount: float = Field(description="Sponsorship amount")
    status: Literal["pledged", "invoiced", "paid", "cancelled"] = Field(
        default="pledged", description="Payment status"
    )
    invoice_number: Optional[str] = Field(default=None, description="Invoice number")
    invoice_date: Optional[datetime] = Field(default=None, description="Invoice date")
    payment_date: Optional[datetime] = Field(default=None, description="Payment received date")
    payment_method: Optional[str] = Field(default=None, description="Payment method")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class BudgetConfig(BaseDocument):
    """MongoDB document for overall budget configuration."""

    event_name: str = Field(description="Event this budget belongs to")
    fiscal_year: Optional[str] = Field(default=None, description="Fiscal year")
    total_budget: float = Field(default=0, description="Total budget amount")
    currency: str = Field(default="USD", description="Currency code")

    # Category allocations
    categories: dict[str, BudgetCategory] = Field(
        default_factory=dict,
        description="Budget categories with allocations",
    )

    # Revenue targets
    sponsorship_goal: float = Field(default=0, description="Sponsorship revenue goal")
    sponsorship_confirmed: float = Field(default=0, description="Confirmed sponsorship")
    sponsorship_pending: float = Field(default=0, description="Pending sponsorship")
    other_revenue: float = Field(default=0, description="Other revenue sources")

    # Aggregated totals (updated periodically)
    total_allocated: float = Field(default=0, description="Sum of category allocations")
    total_spent: float = Field(default=0, description="Sum of all expenses")
    total_committed: float = Field(default=0, description="Sum of commitments")

    # Status
    status: Literal["draft", "approved", "active", "closed"] = Field(
        default="draft", description="Budget status"
    )
    approved_by: Optional[str] = Field(default=None, description="Budget approver")
    approved_at: Optional[datetime] = Field(default=None, description="Approval date")
    notes: Optional[str] = Field(default=None, description="Budget notes")

    @property
    def remaining_budget(self) -> float:
        """Calculate remaining budget."""
        return self.total_budget - self.total_spent - self.total_committed

    @property
    def total_revenue(self) -> float:
        """Calculate total confirmed revenue."""
        return self.sponsorship_confirmed + self.other_revenue

    @property
    def net_position(self) -> float:
        """Calculate net financial position."""
        return self.total_revenue - self.total_spent

    def update_totals(self) -> None:
        """Recalculate aggregated totals from categories."""
        self.total_allocated = sum(c.allocated for c in self.categories.values())
        self.total_spent = sum(c.spent for c in self.categories.values())
        self.total_committed = sum(c.committed for c in self.categories.values())


class BudgetSummary(BaseDocument):
    """Snapshot of budget status for reporting."""

    event_name: str = Field(description="Event name")
    snapshot_date: datetime = Field(
        default_factory=datetime.utcnow, description="When snapshot was taken"
    )
    total_budget: float = Field(default=0)
    total_allocated: float = Field(default=0)
    total_spent: float = Field(default=0)
    total_committed: float = Field(default=0)
    remaining: float = Field(default=0)
    sponsorship_confirmed: float = Field(default=0)
    sponsorship_pending: float = Field(default=0)
    category_breakdown: dict = Field(default_factory=dict)
    warnings: list[str] = Field(
        default_factory=list, description="Budget warnings/alerts"
    )
