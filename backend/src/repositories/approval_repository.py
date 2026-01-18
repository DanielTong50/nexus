"""Repository for approval workflow persistence."""

from datetime import datetime
from typing import Literal, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from src.models.approval import ApprovalDocument, ApprovalHistoryEntry, ApprovalStats
from src.repositories.base import BaseRepository
from src.services.database import Collections


class ApprovalRepository(BaseRepository[ApprovalDocument]):
    """Repository for managing approval documents."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, Collections.APPROVALS, ApprovalDocument)
        self._history_collection_name = Collections.APPROVAL_HISTORY

    @property
    def history_collection(self):
        """Get the approval history collection."""
        return self._db[self._history_collection_name]

    async def create_indexes(self) -> None:
        """Create indexes for approvals collection."""
        await self.collection.create_index([("approval_id", ASCENDING)], unique=True)
        await self.collection.create_index([("status", ASCENDING), ("created_at", DESCENDING)])
        await self.collection.create_index([("expires_at", ASCENDING)])
        await self.collection.create_index([("request_id", ASCENDING)])

        await self.history_collection.create_index(
            [("approval_id", ASCENDING), ("created_at", DESCENDING)]
        )

    async def find_by_approval_id(self, approval_id: str) -> Optional[ApprovalDocument]:
        """
        Find an approval by its approval_id.

        Args:
            approval_id: The unique approval identifier

        Returns:
            The approval document or None
        """
        return await self.find_one({"approval_id": approval_id})

    async def find_pending(
        self,
        request_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        limit: int = 100,
    ) -> list[ApprovalDocument]:
        """
        Find all pending approvals with optional filters.

        Args:
            request_id: Filter by request ID
            agent_name: Filter by agent name
            limit: Maximum number of results

        Returns:
            List of pending approval documents
        """
        query = {"status": "pending"}
        if request_id:
            query["request_id"] = request_id
        if agent_name:
            query["agent_name"] = agent_name

        return await self.find_many(
            query,
            sort=[("created_at", DESCENDING)],
            limit=limit,
        )

    async def find_by_request_id(self, request_id: str) -> list[ApprovalDocument]:
        """
        Find all approvals for a specific request.

        Args:
            request_id: The request ID

        Returns:
            List of approval documents
        """
        return await self.find_many(
            {"request_id": request_id},
            sort=[("created_at", DESCENDING)],
        )

    async def update_status(
        self,
        approval_id: str,
        new_status: Literal["approved", "rejected", "expired", "executed", "failed"],
        changed_by: Optional[str] = None,
        reason: Optional[str] = None,
        edits: Optional[dict] = None,
        execution_result: Optional[dict] = None,
    ) -> Optional[ApprovalDocument]:
        """
        Update the status of an approval and create audit log entry.

        Args:
            approval_id: The approval to update
            new_status: The new status
            changed_by: User or system making the change
            reason: Reason for the status change
            edits: User edits if action was 'edit'
            execution_result: Result of action execution

        Returns:
            The updated approval document or None
        """
        # Get current document for history
        current = await self.find_by_approval_id(approval_id)
        if current is None:
            return None

        previous_status = current.status

        # Prepare update data
        update_data = {
            "status": new_status,
            "updated_at": datetime.utcnow(),
        }

        if new_status in ("approved", "rejected"):
            update_data["approved_by"] = changed_by
            update_data["approved_at"] = datetime.utcnow()

        if reason:
            update_data["rejection_reason"] = reason

        if edits:
            update_data["edits"] = edits

        if execution_result:
            update_data["execution_result"] = execution_result

        # Update the document
        updated = await self.update_one({"approval_id": approval_id}, update_data)

        # Create history entry
        if updated:
            history_entry = ApprovalHistoryEntry(
                approval_id=approval_id,
                previous_status=previous_status,
                new_status=new_status,
                changed_by=changed_by,
                reason=reason,
                metadata={
                    "edits": edits,
                    "execution_result": execution_result,
                },
            )
            await self.history_collection.insert_one(history_entry.to_mongo())

        return updated

    async def expire_old_approvals(self) -> int:
        """
        Expire all approvals past their expiry time.

        Returns:
            Number of approvals expired
        """
        now = datetime.utcnow()

        # Find all pending approvals that have expired
        expired_approvals = await self.find_many(
            {
                "status": "pending",
                "expires_at": {"$lt": now, "$ne": None},
            }
        )

        count = 0
        for approval in expired_approvals:
            await self.update_status(
                approval.approval_id,
                new_status="expired",
                changed_by="system",
                reason="Approval expired due to timeout",
            )
            count += 1

        return count

    async def get_history(self, approval_id: str) -> list[ApprovalHistoryEntry]:
        """
        Get the audit history for an approval.

        Args:
            approval_id: The approval ID

        Returns:
            List of history entries sorted by creation time
        """
        cursor = self.history_collection.find({"approval_id": approval_id}).sort(
            "created_at", DESCENDING
        )
        history = []
        async for entry in cursor:
            history.append(ApprovalHistoryEntry.from_mongo(entry))
        return history

    async def get_stats(self) -> ApprovalStats:
        """
        Get statistics about approvals.

        Returns:
            ApprovalStats with counts by status
        """
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]

        stats = ApprovalStats()
        cursor = self.collection.aggregate(pipeline)
        async for doc in cursor:
            status = doc["_id"]
            count = doc["count"]
            if status == "pending":
                stats.total_pending = count
            elif status == "approved":
                stats.total_approved = count
            elif status == "rejected":
                stats.total_rejected = count
            elif status == "expired":
                stats.total_expired = count
            elif status == "executed":
                stats.total_executed = count
            elif status == "failed":
                stats.total_failed = count

        return stats

    async def cleanup_expired(self, older_than_days: int = 30) -> int:
        """
        Delete expired approvals older than specified days.

        Args:
            older_than_days: Delete approvals expired more than this many days ago

        Returns:
            Number of approvals deleted
        """
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        return await self.delete_many(
            {
                "status": {"$in": ["expired", "executed", "failed"]},
                "updated_at": {"$lt": cutoff},
            }
        )
