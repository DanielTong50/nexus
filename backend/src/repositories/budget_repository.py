"""Repository for budget and financial tracking."""

from datetime import datetime
from typing import Literal, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.models.budget import (
    BudgetConfig,
    BudgetTransaction,
    SponsorshipRevenue,
    BudgetSummary,
    BudgetCategory,
)
from src.repositories.base import BaseRepository
from src.services.database import Collections


class BudgetConfigRepository(BaseRepository[BudgetConfig]):
    """Repository for budget configuration."""

    def __init__(self, db: AsyncIOMotorDatabase):
        # Using "budget" collection for compatibility with existing code
        super().__init__(db, "budget", BudgetConfig)

    async def create_indexes(self) -> None:
        """Create indexes for budget config collection."""
        await self.collection.create_index([("event_name", ASCENDING)], unique=True)
        await self.collection.create_index([("status", ASCENDING)])

    async def find_by_event(self, event_name: str) -> Optional[BudgetConfig]:
        """Find budget config for an event."""
        return await self.find_one({"event_name": event_name})

    async def update_category(
        self,
        event_name: str,
        category_name: str,
        allocated: Optional[float] = None,
        spent: Optional[float] = None,
        committed: Optional[float] = None,
    ) -> Optional[BudgetConfig]:
        """Update a budget category."""
        update_data = {}
        if allocated is not None:
            update_data[f"categories.{category_name}.allocated"] = allocated
        if spent is not None:
            update_data[f"categories.{category_name}.spent"] = spent
        if committed is not None:
            update_data[f"categories.{category_name}.committed"] = committed

        if not update_data:
            return None

        return await self.update_one({"event_name": event_name}, update_data)

    async def update_sponsorship_totals(
        self,
        event_name: str,
        confirmed: float,
        pending: float,
    ) -> Optional[BudgetConfig]:
        """Update sponsorship revenue totals."""
        return await self.update_one(
            {"event_name": event_name},
            {
                "sponsorship_confirmed": confirmed,
                "sponsorship_pending": pending,
            },
        )

    async def recalculate_totals(self, event_name: str) -> Optional[BudgetConfig]:
        """Recalculate aggregated totals from categories and transactions."""
        config = await self.find_by_event(event_name)
        if not config:
            return None

        total_allocated = 0
        total_spent = 0
        total_committed = 0

        for category in config.categories.values():
            total_allocated += category.allocated
            total_spent += category.spent
            total_committed += category.committed

        return await self.update_one(
            {"event_name": event_name},
            {
                "total_allocated": total_allocated,
                "total_spent": total_spent,
                "total_committed": total_committed,
            },
        )


class BudgetTransactionRepository(BaseRepository[BudgetTransaction]):
    """Repository for budget transactions."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.BUDGET_TRANSACTIONS, BudgetTransaction)

    async def create_indexes(self) -> None:
        """Create indexes for transactions collection."""
        await self.collection.create_index(
            [("event_name", ASCENDING), ("created_at", DESCENDING)]
        )
        await self.collection.create_index([("category", ASCENDING)])
        await self.collection.create_index([("type", ASCENDING)])
        await self.collection.create_index([("status", ASCENDING)])

    async def find_by_event(
        self,
        event_name: str,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> list[BudgetTransaction]:
        """Find transactions for an event with optional filters."""
        query = {"event_name": event_name}
        if category:
            query["category"] = category
        if transaction_type:
            query["type"] = transaction_type
        if status:
            query["status"] = status

        return await self.find_many(
            query,
            sort=[("created_at", DESCENDING)],
            limit=limit,
        )

    async def get_category_totals(self, event_name: str) -> dict:
        """Get spending totals by category."""
        pipeline = [
            {"$match": {"event_name": event_name, "status": {"$ne": "cancelled"}}},
            {
                "$group": {
                    "_id": {"category": "$category", "type": "$type"},
                    "total": {"$sum": "$amount"},
                }
            },
        ]

        totals = {}
        cursor = self.collection.aggregate(pipeline)
        async for doc in cursor:
            category = doc["_id"]["category"]
            tx_type = doc["_id"]["type"]
            if category not in totals:
                totals[category] = {"expense": 0, "income": 0, "commitment": 0}
            totals[category][tx_type] = doc["total"]

        return totals

    async def add_expense(
        self,
        event_name: str,
        category: str,
        amount: float,
        description: str,
        vendor: Optional[str] = None,
        reference_number: Optional[str] = None,
    ) -> BudgetTransaction:
        """Add an expense transaction."""
        transaction = BudgetTransaction(
            event_name=event_name,
            category=category,
            type="expense",
            amount=amount,
            description=description,
            vendor=vendor,
            reference_number=reference_number,
            status="pending",
        )
        return await self.create(transaction)

    async def add_income(
        self,
        event_name: str,
        category: str,
        amount: float,
        description: str,
        vendor: Optional[str] = None,
    ) -> BudgetTransaction:
        """Add an income transaction."""
        transaction = BudgetTransaction(
            event_name=event_name,
            category=category,
            type="income",
            amount=amount,
            description=description,
            vendor=vendor,
            status="approved",
        )
        return await self.create(transaction)

    async def approve_transaction(
        self,
        transaction_id: str,
        approved_by: str,
    ) -> Optional[BudgetTransaction]:
        """Approve a transaction."""
        return await self.update_by_id(
            transaction_id,
            {
                "status": "approved",
                "approved_by": approved_by,
                "approved_at": datetime.utcnow(),
            },
        )

    async def mark_paid(
        self,
        transaction_id: str,
        payment_method: Optional[str] = None,
    ) -> Optional[BudgetTransaction]:
        """Mark a transaction as paid."""
        update_data = {
            "status": "paid",
            "payment_date": datetime.utcnow(),
        }
        if payment_method:
            update_data["payment_method"] = payment_method
        return await self.update_by_id(transaction_id, update_data)


class SponsorshipRevenueRepository(BaseRepository[SponsorshipRevenue]):
    """Repository for sponsorship revenue tracking."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "sponsorship_revenue", SponsorshipRevenue)

    async def create_indexes(self) -> None:
        """Create indexes for sponsorship revenue collection."""
        await self.collection.create_index([("event_name", ASCENDING)])
        await self.collection.create_index([("sponsor_name", ASCENDING)])
        await self.collection.create_index([("status", ASCENDING)])

    async def find_by_event(
        self,
        event_name: str,
        status: Optional[str] = None,
    ) -> list[SponsorshipRevenue]:
        """Find sponsorship revenue for an event."""
        query = {"event_name": event_name}
        if status:
            query["status"] = status
        return await self.find_many(query, sort=[("amount", DESCENDING)])

    async def get_totals_by_status(self, event_name: str) -> dict:
        """Get sponsorship totals by status."""
        pipeline = [
            {"$match": {"event_name": event_name}},
            {"$group": {"_id": "$status", "total": {"$sum": "$amount"}}},
        ]

        totals = {}
        cursor = self.collection.aggregate(pipeline)
        async for doc in cursor:
            totals[doc["_id"]] = doc["total"]

        return totals

    async def record_payment(
        self,
        event_name: str,
        sponsor_name: str,
        payment_date: Optional[datetime] = None,
        payment_method: Optional[str] = None,
    ) -> Optional[SponsorshipRevenue]:
        """Record a sponsorship payment."""
        return await self.update_one(
            {"event_name": event_name, "sponsor_name": sponsor_name},
            {
                "status": "paid",
                "payment_date": payment_date or datetime.utcnow(),
                "payment_method": payment_method,
            },
        )


class BudgetRepository:
    """Facade for all budget operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.config = BudgetConfigRepository(db)
        self.transactions = BudgetTransactionRepository(db)
        self.sponsorship = SponsorshipRevenueRepository(db)

    async def create_indexes(self) -> None:
        """Create all indexes for budget collections."""
        await self.config.create_indexes()
        await self.transactions.create_indexes()
        await self.sponsorship.create_indexes()

    async def get_summary(self, event_name: str) -> dict:
        """Get complete budget summary for an event."""
        config = await self.config.find_by_event(event_name)
        transactions = await self.transactions.find_by_event(event_name)
        category_totals = await self.transactions.get_category_totals(event_name)
        sponsorship_totals = await self.sponsorship.get_totals_by_status(event_name)

        # Calculate derived values
        total_expenses = sum(
            totals.get("expense", 0) for totals in category_totals.values()
        )
        total_income = sum(
            totals.get("income", 0) for totals in category_totals.values()
        )
        total_commitments = sum(
            totals.get("commitment", 0) for totals in category_totals.values()
        )

        confirmed_sponsorship = sponsorship_totals.get("paid", 0) + sponsorship_totals.get(
            "invoiced", 0
        )
        pending_sponsorship = sponsorship_totals.get("pledged", 0)

        return {
            "config": config.model_dump() if config else None,
            "totals": {
                "expenses": total_expenses,
                "income": total_income,
                "commitments": total_commitments,
                "sponsorship_confirmed": confirmed_sponsorship,
                "sponsorship_pending": pending_sponsorship,
                "net_position": total_income + confirmed_sponsorship - total_expenses,
            },
            "by_category": category_totals,
            "recent_transactions": [t.model_dump() for t in transactions[:20]],
        }

    async def add_expense(
        self,
        event_name: str,
        category: str,
        amount: float,
        description: str,
        vendor: Optional[str] = None,
    ) -> BudgetTransaction:
        """Add an expense and update category totals."""
        transaction = await self.transactions.add_expense(
            event_name, category, amount, description, vendor
        )

        # Update category spent amount
        await self.config.update_category(event_name, category, spent=amount)
        await self.config.recalculate_totals(event_name)

        return transaction
