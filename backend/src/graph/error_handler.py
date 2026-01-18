"""Error handling and retry logic for agent execution.

This module provides:
- Retry decorator with exponential backoff (max 2 retries)
- Fallback mechanisms to alert users on failure
- Error aggregation and reporting
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Type variable for generic async functions
T = TypeVar("T")


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""

    LOW = "low"  # Retry may succeed, non-critical
    MEDIUM = "medium"  # Retry unlikely to succeed, but not critical
    HIGH = "high"  # Critical error, user must be notified
    CRITICAL = "critical"  # System-level failure


class ErrorCategory(str, Enum):
    """Categories of errors for classification."""

    TRANSIENT = "transient"  # Network timeouts, rate limits - worth retrying
    VALIDATION = "validation"  # Bad input - don't retry
    AUTHENTICATION = "authentication"  # Auth failures - don't retry
    EXTERNAL_SERVICE = "external_service"  # Third-party API errors
    INTERNAL = "internal"  # Internal logic errors
    UNKNOWN = "unknown"


class AgentError(BaseModel):
    """Structured error from agent execution."""

    agent_name: str = Field(description="Name of the agent that failed")
    error_type: str = Field(description="Exception type name")
    message: str = Field(description="Error message")
    category: ErrorCategory = Field(default=ErrorCategory.UNKNOWN)
    severity: ErrorSeverity = Field(default=ErrorSeverity.MEDIUM)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retry_count: int = Field(default=0, description="Number of retries attempted")
    is_retryable: bool = Field(default=True, description="Whether this error can be retried")
    context: dict = Field(default_factory=dict, description="Additional context")


class FallbackAlert(BaseModel):
    """Alert sent to user when all retries fail."""

    agent_name: str = Field(description="Agent that failed")
    error_message: str = Field(description="User-friendly error message")
    original_request: str = Field(description="The original user request")
    suggestions: list[str] = Field(default_factory=list, description="Suggestions for user")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    requires_action: bool = Field(default=True, description="Whether user action needed")


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""

    max_retries: int = Field(default=2, ge=0, le=5)
    base_delay: float = Field(default=1.0, description="Base delay in seconds")
    exponential_base: float = Field(default=2.0, description="Exponential backoff base")
    max_delay: float = Field(default=10.0, description="Maximum delay between retries")
    retry_on: list[ErrorCategory] = Field(
        default_factory=lambda: [ErrorCategory.TRANSIENT, ErrorCategory.EXTERNAL_SERVICE]
    )


# Default retry configuration
DEFAULT_RETRY_CONFIG = RetryConfig()


def classify_error(exception: Exception) -> tuple[ErrorCategory, bool]:
    """Classify an exception to determine if it's retryable.

    Args:
        exception: The exception to classify

    Returns:
        Tuple of (ErrorCategory, is_retryable)
    """
    error_type = type(exception).__name__
    message = str(exception).lower()

    # Transient errors (retryable)
    if any(keyword in message for keyword in ["timeout", "rate limit", "429", "503", "504"]):
        return ErrorCategory.TRANSIENT, True

    # Authentication errors (not retryable)
    if any(keyword in message for keyword in ["auth", "401", "403", "api key", "token"]):
        return ErrorCategory.AUTHENTICATION, False

    # Validation errors (not retryable)
    if any(keyword in message for keyword in ["validation", "invalid", "missing required"]):
        return ErrorCategory.VALIDATION, False

    # Connection/network errors (retryable)
    if any(keyword in message for keyword in ["connection", "network", "reset", "refused"]):
        return ErrorCategory.TRANSIENT, True

    # External service errors (possibly retryable)
    if any(keyword in message for keyword in ["external", "service", "500", "502"]):
        return ErrorCategory.EXTERNAL_SERVICE, True

    # Default: unknown, retry once just in case
    return ErrorCategory.UNKNOWN, True


def with_retry(
    max_retries: int = 2,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
):
    """Decorator to add retry logic to async functions.

    Args:
        max_retries: Maximum number of retry attempts (default: 2)
        base_delay: Base delay between retries in seconds
        exponential_base: Base for exponential backoff
        on_retry: Optional callback called on each retry

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    category, is_retryable = classify_error(e)

                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise

                    if not is_retryable:
                        logger.warning(
                            f"{func.__name__} failed with non-retryable error: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        DEFAULT_RETRY_CONFIG.max_delay,
                    )

                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    if on_retry:
                        on_retry(attempt + 1, e)

                    await asyncio.sleep(delay)

            # Should never reach here, but just in case
            raise last_exception

        return wrapper

    return decorator


async def execute_with_retry(
    func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    agent_name: str = "unknown",
    **kwargs,
) -> tuple[Optional[T], Optional[AgentError]]:
    """Execute a function with retry logic and error handling.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        config: Retry configuration (uses default if not provided)
        agent_name: Name of the agent for error reporting
        **kwargs: Keyword arguments for func

    Returns:
        Tuple of (result, error) - one will be None
    """
    config = config or DEFAULT_RETRY_CONFIG
    last_error = None

    for attempt in range(config.max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            return result, None

        except Exception as e:
            category, is_retryable = classify_error(e)

            last_error = AgentError(
                agent_name=agent_name,
                error_type=type(e).__name__,
                message=str(e),
                category=category,
                severity=ErrorSeverity.MEDIUM if is_retryable else ErrorSeverity.HIGH,
                retry_count=attempt,
                is_retryable=is_retryable,
                context={"attempt": attempt + 1, "max_retries": config.max_retries},
            )

            if attempt == config.max_retries:
                logger.error(f"Agent {agent_name} failed after all retries: {e}")
                break

            if not is_retryable:
                logger.warning(f"Agent {agent_name} failed with non-retryable error: {e}")
                break

            # Calculate delay
            delay = min(
                config.base_delay * (config.exponential_base ** attempt),
                config.max_delay,
            )

            logger.warning(
                f"Agent {agent_name} attempt {attempt + 1} failed: {e}. "
                f"Retrying in {delay:.1f}s..."
            )

            await asyncio.sleep(delay)

    return None, last_error


def create_fallback_alert(
    agent_name: str,
    error: AgentError,
    original_request: str,
) -> FallbackAlert:
    """Create a fallback alert for the user when all retries fail.

    Args:
        agent_name: Name of the failed agent
        error: The final error that occurred
        original_request: The original user request

    Returns:
        FallbackAlert with user-friendly message and suggestions
    """
    # Generate user-friendly message based on error category
    if error.category == ErrorCategory.TRANSIENT:
        message = f"The {agent_name} agent couldn't complete due to a temporary issue. Please try again in a moment."
        suggestions = [
            "Wait a few seconds and try again",
            "Check if external services are available",
        ]
    elif error.category == ErrorCategory.AUTHENTICATION:
        message = f"The {agent_name} agent couldn't authenticate with an external service."
        suggestions = [
            "Check if API credentials are configured correctly",
            "Contact an administrator to verify service connections",
        ]
    elif error.category == ErrorCategory.VALIDATION:
        message = f"The {agent_name} agent couldn't process your request due to invalid input."
        suggestions = [
            "Check if your request is complete and correctly formatted",
            "Try rephrasing your request",
        ]
    elif error.category == ErrorCategory.EXTERNAL_SERVICE:
        message = f"The {agent_name} agent couldn't reach an external service."
        suggestions = [
            "The external service may be temporarily unavailable",
            "Try again later or check service status",
        ]
    else:
        message = f"The {agent_name} agent encountered an unexpected error."
        suggestions = [
            "Try your request again",
            "If the problem persists, contact support",
        ]

    return FallbackAlert(
        agent_name=agent_name,
        error_message=message,
        original_request=original_request[:200],  # Truncate for safety
        suggestions=suggestions,
        requires_action=error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL],
    )


async def handle_agent_error(
    agent_name: str,
    error: Exception,
    user_message: str,
    retry_count: int = 0,
) -> dict:
    """Handle an agent error with proper categorization and fallback.

    Args:
        agent_name: Name of the agent that failed
        error: The exception that occurred
        user_message: The original user message
        retry_count: Number of retries already attempted

    Returns:
        Dict with error info and fallback alert for state update
    """
    category, is_retryable = classify_error(error)

    agent_error = AgentError(
        agent_name=agent_name,
        error_type=type(error).__name__,
        message=str(error),
        category=category,
        severity=ErrorSeverity.HIGH if retry_count >= 2 else ErrorSeverity.MEDIUM,
        retry_count=retry_count,
        is_retryable=is_retryable and retry_count < 2,
    )

    # Create fallback alert for user
    fallback = create_fallback_alert(agent_name, agent_error, user_message)

    logger.error(
        f"Agent {agent_name} error handled: {error} "
        f"(category={category}, retries={retry_count}, fallback_created=True)"
    )

    return {
        "errors": [{
            "agent": agent_name,
            "error": agent_error.model_dump(),
            "fallback_alert": fallback.model_dump(),
        }],
    }


class ErrorHandler:
    """Centralized error handler for the workflow."""

    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize error handler.

        Args:
            config: Retry configuration to use
        """
        self.config = config or DEFAULT_RETRY_CONFIG
        self.errors: list[AgentError] = []
        self.fallback_alerts: list[FallbackAlert] = []

    async def execute_with_fallback(
        self,
        func: Callable[..., T],
        *args,
        agent_name: str,
        user_message: str,
        **kwargs,
    ) -> tuple[Optional[T], Optional[FallbackAlert]]:
        """Execute a function with retry and fallback on failure.

        Args:
            func: Async function to execute
            *args: Positional arguments
            agent_name: Name of the agent
            user_message: Original user message for fallback context
            **kwargs: Keyword arguments

        Returns:
            Tuple of (result, fallback_alert) - fallback is None on success
        """
        result, error = await execute_with_retry(
            func,
            *args,
            config=self.config,
            agent_name=agent_name,
            **kwargs,
        )

        if error:
            self.errors.append(error)
            fallback = create_fallback_alert(agent_name, error, user_message)
            self.fallback_alerts.append(fallback)
            return None, fallback

        return result, None

    def get_all_errors(self) -> list[dict]:
        """Get all errors as dicts."""
        return [e.model_dump() for e in self.errors]

    def get_all_alerts(self) -> list[dict]:
        """Get all fallback alerts as dicts."""
        return [a.model_dump() for a in self.fallback_alerts]

    def clear(self):
        """Clear all errors and alerts."""
        self.errors.clear()
        self.fallback_alerts.clear()
