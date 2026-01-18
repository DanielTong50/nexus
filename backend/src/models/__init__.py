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
from src.models.organization import (
    OrganizationConfig,
    SlackChannelMapping,
    DataSourceMapping,
    EventConfig,
    create_default_config,
)
from src.models.task_plan import (
    Task,
    TaskPlan,
    QuestionPlan,
    ExtractedEntity,
    TaskStatus,
    RequestType,
    ExecutionStrategy,
    create_task_plan,
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
    # Organization Config
    "OrganizationConfig",
    "SlackChannelMapping",
    "DataSourceMapping",
    "EventConfig",
    "create_default_config",
    # Task Plan
    "Task",
    "TaskPlan",
    "QuestionPlan",
    "ExtractedEntity",
    "TaskStatus",
    "RequestType",
    "ExecutionStrategy",
    "create_task_plan",
]
