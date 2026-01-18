"""Models module for Nexus backend."""

from src.models.base import BaseDocument, PyObjectId, TimestampMixin
from src.models.approval import ApprovalDocument, ApprovalHistoryEntry, ApprovalStats
from src.models.chat_history import (
    RequestSummary,
    ChatMessage,
    AgentExecutionLog,
    ConversationThread,
)
from src.models.user_session import UserSession, UserProfile, UserActivity
from src.models.partnership import (
    PartnershipBase,
    SponsorPartnership,
    JudgePartnership,
    MentorPartnership,
    PartnershipStats,
)
from src.models.event import (
    EventLogistics,
    RoomBooking,
    LogisticsTask,
    VenueInfo,
    CateringInfo,
    ScheduleItem,
)
from src.models.budget import (
    BudgetConfig,
    BudgetTransaction,
    SponsorshipRevenue,
    BudgetSummary,
    BudgetCategory,
)

__all__ = [
    # Base
    "BaseDocument",
    "PyObjectId",
    "TimestampMixin",
    # Approval
    "ApprovalDocument",
    "ApprovalHistoryEntry",
    "ApprovalStats",
    # Chat History
    "RequestSummary",
    "ChatMessage",
    "AgentExecutionLog",
    "ConversationThread",
    # User Session
    "UserSession",
    "UserProfile",
    "UserActivity",
    # Partnership
    "PartnershipBase",
    "SponsorPartnership",
    "JudgePartnership",
    "MentorPartnership",
    "PartnershipStats",
    # Event
    "EventLogistics",
    "RoomBooking",
    "LogisticsTask",
    "VenueInfo",
    "CateringInfo",
    "ScheduleItem",
    # Budget
    "BudgetConfig",
    "BudgetTransaction",
    "SponsorshipRevenue",
    "BudgetSummary",
    "BudgetCategory",
]
