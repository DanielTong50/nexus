"""Tests for error handling and retry logic.

Tests verify:
- Retry decorator with max 2 retries
- Exponential backoff delay calculation
- Error classification (retryable vs non-retryable)
- Fallback alerts for users
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import time

from src.graph.error_handler import (
    with_retry,
    execute_with_retry,
    classify_error,
    create_fallback_alert,
    handle_agent_error,
    ErrorHandler,
    AgentError,
    FallbackAlert,
    RetryConfig,
    ErrorCategory,
    ErrorSeverity,
    DEFAULT_RETRY_CONFIG,
)


class TestClassifyError:
    """Tests for error classification."""

    def test_timeout_is_transient_retryable(self):
        """Timeout errors are classified as transient and retryable."""
        error = Exception("Connection timeout occurred")
        category, is_retryable = classify_error(error)

        assert category == ErrorCategory.TRANSIENT
        assert is_retryable is True

    def test_rate_limit_is_transient_retryable(self):
        """Rate limit errors are classified as transient and retryable."""
        error = Exception("Rate limit exceeded: 429 Too Many Requests")
        category, is_retryable = classify_error(error)

        assert category == ErrorCategory.TRANSIENT
        assert is_retryable is True

    def test_auth_error_not_retryable(self):
        """Authentication errors are not retryable."""
        error = Exception("401 Unauthorized: Invalid API key")
        category, is_retryable = classify_error(error)

        assert category == ErrorCategory.AUTHENTICATION
        assert is_retryable is False

    def test_validation_error_not_retryable(self):
        """Validation errors are not retryable."""
        error = Exception("Validation error: Missing required field 'name'")
        category, is_retryable = classify_error(error)

        assert category == ErrorCategory.VALIDATION
        assert is_retryable is False

    def test_connection_error_is_retryable(self):
        """Connection errors are retryable."""
        error = Exception("Connection refused by server")
        category, is_retryable = classify_error(error)

        assert category == ErrorCategory.TRANSIENT
        assert is_retryable is True

    def test_503_is_external_service_retryable(self):
        """503 errors are classified as transient."""
        error = Exception("503 Service Unavailable")
        category, is_retryable = classify_error(error)

        assert category == ErrorCategory.TRANSIENT
        assert is_retryable is True

    def test_unknown_error_defaults_to_retryable(self):
        """Unknown errors default to retryable."""
        error = Exception("Something weird happened")
        category, is_retryable = classify_error(error)

        assert category == ErrorCategory.UNKNOWN
        assert is_retryable is True


class TestWithRetryDecorator:
    """Tests for the retry decorator."""

    @pytest.mark.asyncio
    async def test_succeeds_without_retry(self):
        """Function succeeds on first attempt without retry."""
        call_count = 0

        @with_retry(max_retries=2)
        async def succeeding_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await succeeding_func()

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retries_on_transient_error(self):
        """Retries on transient error and eventually succeeds."""
        call_count = 0

        @with_retry(max_retries=2, base_delay=0.01)
        async def failing_then_succeeding():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Timeout error")
            return "success"

        result = await failing_then_succeeding()

        assert result == "success"
        assert call_count == 3  # 1 initial + 2 retries

    @pytest.mark.asyncio
    async def test_max_2_retries(self):
        """Stops after 2 retries (3 total attempts)."""
        call_count = 0

        @with_retry(max_retries=2, base_delay=0.01)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise Exception("Timeout error")

        with pytest.raises(Exception) as exc_info:
            await always_fails()

        assert "Timeout" in str(exc_info.value)
        assert call_count == 3  # 1 initial + 2 retries = 3 total

    @pytest.mark.asyncio
    async def test_no_retry_on_auth_error(self):
        """Does not retry on authentication errors."""
        call_count = 0

        @with_retry(max_retries=2, base_delay=0.01)
        async def auth_failure():
            nonlocal call_count
            call_count += 1
            raise Exception("401 Unauthorized")

        with pytest.raises(Exception):
            await auth_failure()

        assert call_count == 1  # No retries for auth errors

    @pytest.mark.asyncio
    async def test_no_retry_on_validation_error(self):
        """Does not retry on validation errors."""
        call_count = 0

        @with_retry(max_retries=2, base_delay=0.01)
        async def validation_failure():
            nonlocal call_count
            call_count += 1
            raise Exception("Validation error: invalid input")

        with pytest.raises(Exception):
            await validation_failure()

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_calls_on_retry_callback(self):
        """Calls on_retry callback on each retry."""
        retry_calls = []

        def on_retry_callback(attempt, error):
            retry_calls.append((attempt, str(error)))

        @with_retry(max_retries=2, base_delay=0.01, on_retry=on_retry_callback)
        async def failing_func():
            raise Exception("Timeout error")

        with pytest.raises(Exception):
            await failing_func()

        assert len(retry_calls) == 2
        assert retry_calls[0][0] == 1  # First retry
        assert retry_calls[1][0] == 2  # Second retry


class TestExecuteWithRetry:
    """Tests for execute_with_retry function."""

    @pytest.mark.asyncio
    async def test_returns_result_on_success(self):
        """Returns result and None error on success."""
        async def success_func():
            return "result"

        result, error = await execute_with_retry(success_func, agent_name="test")

        assert result == "result"
        assert error is None

    @pytest.mark.asyncio
    async def test_returns_error_on_failure(self):
        """Returns None result and error on failure."""
        async def fail_func():
            raise Exception("Timeout error")

        config = RetryConfig(max_retries=1, base_delay=0.01)
        result, error = await execute_with_retry(
            fail_func,
            config=config,
            agent_name="test_agent"
        )

        assert result is None
        assert error is not None
        assert isinstance(error, AgentError)
        assert error.agent_name == "test_agent"

    @pytest.mark.asyncio
    async def test_error_contains_retry_count(self):
        """Error contains the number of retries attempted."""
        async def fail_func():
            raise Exception("Connection error")

        config = RetryConfig(max_retries=2, base_delay=0.01)
        result, error = await execute_with_retry(
            fail_func,
            config=config,
            agent_name="test"
        )

        assert error.retry_count == 2  # Last retry attempt


class TestCreateFallbackAlert:
    """Tests for fallback alert creation."""

    def test_creates_alert_for_transient_error(self):
        """Creates appropriate alert for transient errors."""
        error = AgentError(
            agent_name="partnerships",
            error_type="TimeoutError",
            message="Connection timed out",
            category=ErrorCategory.TRANSIENT,
            retry_count=2,
        )

        alert = create_fallback_alert("partnerships", error, "Update sponsor status")

        assert isinstance(alert, FallbackAlert)
        assert alert.agent_name == "partnerships"
        assert "temporary" in alert.error_message.lower()
        assert len(alert.suggestions) > 0

    def test_creates_alert_for_auth_error(self):
        """Creates appropriate alert for auth errors."""
        error = AgentError(
            agent_name="finance",
            error_type="AuthError",
            message="Invalid API key",
            category=ErrorCategory.AUTHENTICATION,
        )

        alert = create_fallback_alert("finance", error, "Check budget")

        assert "authenticate" in alert.error_message.lower()
        assert any("credentials" in s.lower() for s in alert.suggestions)

    def test_alert_requires_action_for_high_severity(self):
        """Alert requires action for high severity errors."""
        error = AgentError(
            agent_name="events",
            error_type="CriticalError",
            message="Critical failure",
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.HIGH,
        )

        alert = create_fallback_alert("events", error, "Book venue")

        assert alert.requires_action is True

    def test_truncates_long_requests(self):
        """Truncates long original requests."""
        error = AgentError(
            agent_name="marketing",
            error_type="Error",
            message="Failed",
            category=ErrorCategory.UNKNOWN,
        )
        long_request = "A" * 500

        alert = create_fallback_alert("marketing", error, long_request)

        assert len(alert.original_request) <= 200


class TestHandleAgentError:
    """Tests for handle_agent_error function."""

    @pytest.mark.asyncio
    async def test_returns_error_dict(self):
        """Returns dict with error info."""
        result = await handle_agent_error(
            agent_name="partnerships",
            error=Exception("Timeout error"),
            user_message="Update sponsor",
            retry_count=2,
        )

        assert "errors" in result
        assert len(result["errors"]) == 1
        assert result["errors"][0]["agent"] == "partnerships"

    @pytest.mark.asyncio
    async def test_includes_fallback_alert(self):
        """Includes fallback alert in result."""
        result = await handle_agent_error(
            agent_name="finance",
            error=Exception("Connection refused"),
            user_message="Check budget",
            retry_count=1,
        )

        assert "fallback_alert" in result["errors"][0]
        assert result["errors"][0]["fallback_alert"]["agent_name"] == "finance"


class TestErrorHandler:
    """Tests for ErrorHandler class."""

    @pytest.mark.asyncio
    async def test_execute_with_fallback_success(self):
        """execute_with_fallback returns result on success."""
        handler = ErrorHandler()

        async def success_func():
            return "result"

        result, fallback = await handler.execute_with_fallback(
            success_func,
            agent_name="test",
            user_message="test request",
        )

        assert result == "result"
        assert fallback is None
        assert len(handler.errors) == 0

    @pytest.mark.asyncio
    async def test_execute_with_fallback_creates_alert(self):
        """execute_with_fallback creates fallback on failure."""
        config = RetryConfig(max_retries=1, base_delay=0.01)
        handler = ErrorHandler(config)

        async def fail_func():
            raise Exception("Timeout")

        result, fallback = await handler.execute_with_fallback(
            fail_func,
            agent_name="test_agent",
            user_message="original request",
        )

        assert result is None
        assert fallback is not None
        assert fallback.agent_name == "test_agent"
        assert len(handler.errors) == 1
        assert len(handler.fallback_alerts) == 1

    def test_get_all_errors(self):
        """get_all_errors returns list of error dicts."""
        handler = ErrorHandler()
        handler.errors.append(AgentError(
            agent_name="test",
            error_type="Error",
            message="Test error",
        ))

        errors = handler.get_all_errors()

        assert len(errors) == 1
        assert errors[0]["agent_name"] == "test"

    def test_clear_resets_state(self):
        """clear removes all errors and alerts."""
        handler = ErrorHandler()
        handler.errors.append(AgentError(
            agent_name="test",
            error_type="Error",
            message="Test",
        ))
        handler.fallback_alerts.append(FallbackAlert(
            agent_name="test",
            error_message="Test",
            original_request="test",
        ))

        handler.clear()

        assert len(handler.errors) == 0
        assert len(handler.fallback_alerts) == 0


class TestRetryTiming:
    """Tests for retry timing and backoff."""

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Verifies exponential backoff increases delay."""
        delays_experienced = []
        last_time = [time.time()]

        @with_retry(max_retries=2, base_delay=0.05, exponential_base=2.0)
        async def track_delays():
            now = time.time()
            if last_time[0] is not None:
                delays_experienced.append(now - last_time[0])
            last_time[0] = now
            raise Exception("Timeout")

        with pytest.raises(Exception):
            await track_delays()

        # Should have 2 delays (between 3 attempts)
        assert len(delays_experienced) == 3  # Initial + 2 retries
        
        # Second delay should be roughly 2x the first (exponential backoff)
        # delays_experienced[0] is ~0 (initial call)
        # delays_experienced[1] is first retry delay (~0.05s)
        # delays_experienced[2] is second retry delay (~0.1s)
        if len(delays_experienced) >= 3:
            first_retry_delay = delays_experienced[1]
            second_retry_delay = delays_experienced[2]
            # Allow some tolerance for timing
            assert second_retry_delay > first_retry_delay * 1.5
