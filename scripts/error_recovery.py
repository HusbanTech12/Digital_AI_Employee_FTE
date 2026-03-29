"""
Error Recovery and Graceful Degradation System

Gold Tier Feature: Robust error handling with automatic recovery strategies.
Provides retry logic, fallback mechanisms, and circuit breaker patterns.

Usage:
    from error_recovery import ErrorRecovery, RecoveryStrategy
    
    recovery = ErrorRecovery(vault_path)
    
    @recovery.retry(max_attempts=3, strategy=RecoveryStrategy.EXPONENTIAL_BACKOFF)
    def send_email():
        # Email sending code
        pass
"""

import time
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, List, Optional, TypeVar, ParamSpec
from functools import wraps
from enum import Enum
import logging


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types."""
    IMMEDIATE_RETRY = "immediate_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    SKIP_AND_LOG = "skip_and_log"


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


T = TypeVar('T')
P = ParamSpec('P')


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents cascading failures by stopping requests to failing services.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_requests: int = 3
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Circuit breaker name
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again
            half_open_requests: Number of test requests in half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests

        self.failure_count = 0
        self.success_count = 0
        self.state = "closed"  # closed, open, half-open
        self.last_failure_time: Optional[datetime] = None
        self.half_open_successes = 0

    def call(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpen: If circuit is open
        """
        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = "half-open"
                    self.half_open_successes = 0
                else:
                    raise CircuitBreakerOpen(
                        f"Circuit {self.name} is open. "
                        f"Retry after {self.recovery_timeout - elapsed:.0f}s"
                    )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        if self.state == "half-open":
            self.half_open_successes += 1
            if self.half_open_successes >= self.half_open_requests:
                self.state = "closed"
        self.success_count += 1

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == "half-open":
            self.state = "open"
        elif self.failure_count >= self.failure_threshold:
            self.state = "open"

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        return {
            'name': self.name,
            'state': self.state,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure': self.last_failure_time.isoformat() if self.last_failure_time else None,
        }


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""
    pass


class ErrorRecovery:
    """
    Error recovery and graceful degradation system.

    Features:
    - Retry with exponential backoff
    - Circuit breaker pattern
    - Fallback functions
    - Error categorization
    - Recovery logging
    """

    def __init__(self, vault_path: str):
        """
        Initialize error recovery system.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.recovery_dir = self.logs_dir / 'Recovery'
        
        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.recovery_dir.mkdir(parents=True, exist_ok=True)

        # Circuit breakers by service name
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

        # Error statistics
        self.error_stats = {
            'total_errors': 0,
            'recovered': 0,
            'unrecoverable': 0,
            'by_type': {},
            'by_severity': {},
        }

        # Load existing stats
        self._load_stats()

        # Setup logging
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Setup recovery logging."""
        log_file = self.recovery_dir / f'recovery_{datetime.now().strftime("%Y-%m-%d")}.log'

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logger = logging.getLogger('ErrorRecovery')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _load_stats(self):
        """Load error statistics."""
        stats_file = self.recovery_dir / 'error_stats.json'
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                self.error_stats = json.load(f)

    def _save_stats(self):
        """Save error statistics."""
        stats_file = self.recovery_dir / 'error_stats.json'
        with open(stats_file, 'w') as f:
            json.dump(self.error_stats, f, indent=2)

    def _calculate_backoff(self, attempt: int, strategy: RecoveryStrategy) -> float:
        """
        Calculate backoff time for retry.

        Args:
            attempt: Current attempt number
            strategy: Recovery strategy to use

        Returns:
            Backoff time in seconds
        """
        if strategy == RecoveryStrategy.IMMEDIATE_RETRY:
            return 0
        elif strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
            # 1s, 2s, 4s, 8s, 16s, max 60s
            return min(2 ** attempt, 60) + random.uniform(0, 1)
        elif strategy == RecoveryStrategy.LINEAR_BACKOFF:
            # 1s, 2s, 3s, 4s, 5s
            return attempt + random.uniform(0, 0.5)
        else:
            return 1

    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Check if error is retryable.

        Args:
            error: Exception to check

        Returns:
            True if error is retryable
        """
        # Network errors are usually retryable
        retryable_types = (
            ConnectionError,
            TimeoutError,
            ConnectionRefusedError,
            ConnectionResetError,
        )

        # Check error message for common retryable patterns
        retryable_messages = [
            'timeout',
            'connection',
            'network',
            'temporary',
            'rate limit',
            'throttl',
        ]

        if isinstance(error, retryable_types):
            return True

        error_msg = str(error).lower()
        return any(msg in error_msg for msg in retryable_messages)

    def _categorize_error(self, error: Exception) -> ErrorSeverity:
        """
        Categorize error severity.

        Args:
            error: Exception to categorize

        Returns:
            Error severity level
        """
        # Critical errors - never retry
        critical_types = (
            PermissionError,
            FileNotFoundError,
            KeyError,
            ValueError,
        )

        if isinstance(error, critical_types):
            return ErrorSeverity.CRITICAL

        # High severity - retry with caution
        high_messages = ['authentication', 'authorization', 'quota', 'limit']
        if any(msg in str(error).lower() for msg in high_messages):
            return ErrorSeverity.HIGH

        # Medium severity - standard retry
        if self._is_retryable_error(error):
            return ErrorSeverity.MEDIUM

        # Low severity - can retry
        return ErrorSeverity.LOW

    def retry(
        self,
        max_attempts: int = 3,
        strategy: RecoveryStrategy = RecoveryStrategy.EXPONENTIAL_BACKOFF,
        fallback: Optional[Callable] = None,
        circuit_breaker_name: Optional[str] = None,
        skip_on_error: Optional[tuple] = None
    ):
        """
        Decorator for automatic retry with recovery strategies.

        Args:
            max_attempts: Maximum retry attempts
            strategy: Recovery strategy to use
            fallback: Fallback function if all retries fail
            circuit_breaker_name: Name of circuit breaker to use
            skip_on_error: Exception types to skip retry for

        Returns:
            Decorated function

        Example:
            @recovery.retry(max_attempts=3, strategy=RecoveryStrategy.EXPONENTIAL_BACKOFF)
            def send_email():
                pass
        """
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                last_error = None
                attempt = 0

                while attempt < max_attempts:
                    try:
                        # Use circuit breaker if configured
                        if circuit_breaker_name:
                            cb = self.get_circuit_breaker(circuit_breaker_name)
                            result = cb.call(func, *args, **kwargs)
                        else:
                            result = func(*args, **kwargs)

                        # Success
                        self.logger.info(f'{func.__name__} succeeded on attempt {attempt + 1}')
                        self.error_stats['recovered'] += 1
                        self._save_stats()
                        return result

                    except Exception as e:
                        last_error = e
                        attempt += 1
                        self.error_stats['total_errors'] += 1

                        # Categorize error
                        severity = self._categorize_error(e)
                        error_type = type(e).__name__

                        # Update stats
                        if error_type not in self.error_stats['by_type']:
                            self.error_stats['by_type'][error_type] = 0
                        self.error_stats['by_type'][error_type] += 1

                        severity_str = severity.value
                        if severity_str not in self.error_stats['by_severity']:
                            self.error_stats['by_severity'][severity_str] = 0
                        self.error_stats['by_severity'][severity_str] += 1

                        # Check if we should skip retry
                        if skip_on_error and isinstance(e, skip_on_error):
                            self.logger.warning(f'{func.__name__}: Skipping retry for {error_type}')
                            break

                        # Check if error is retryable
                        if not self._is_retryable_error(e):
                            self.logger.warning(f'{func.__name__}: Non-retryable error: {error_type}')
                            self.error_stats['unrecoverable'] += 1
                            break

                        # Check if we have more attempts
                        if attempt >= max_attempts:
                            self.logger.error(f'{func.__name__}: Max attempts ({max_attempts}) reached')
                            break

                        # Calculate and apply backoff
                        backoff = self._calculate_backoff(attempt, strategy)
                        self.logger.warning(
                            f'{func.__name__}: Attempt {attempt}/{max_attempts} failed. '
                            f'Retrying in {backoff:.1f}s. Error: {e}'
                        )
                        time.sleep(backoff)

                # All retries failed
                self.error_stats['unrecoverable'] += 1
                self._save_stats()

                # Try fallback if provided
                if fallback:
                    try:
                        self.logger.info(f'{func.__name__}: Executing fallback')
                        return fallback(*args, **kwargs)
                    except Exception as fallback_error:
                        self.logger.error(f'{func.__name__}: Fallback also failed: {fallback_error}')

                # Re-raise last error
                if last_error:
                    raise last_error
                raise RuntimeError(f'{func.__name__}: All attempts failed')

            return wrapper
        return decorator

    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """
        Get or create a circuit breaker.

        Args:
            name: Circuit breaker name

        Returns:
            CircuitBreaker instance
        """
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name)
        return self.circuit_breakers[name]

    def get_all_circuit_breakers_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all circuit breakers.

        Returns:
            Dictionary of circuit breaker statuses
        """
        return {
            name: cb.get_status()
            for name, cb in self.circuit_breakers.items()
        }

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get error summary report.

        Returns:
            Error summary dictionary
        """
        return {
            'total_errors': self.error_stats['total_errors'],
            'recovered': self.error_stats['recovered'],
            'unrecoverable': self.error_stats['unrecoverable'],
            'recovery_rate': (
                self.error_stats['recovered'] / 
                max(1, self.error_stats['total_errors']) * 100
            ),
            'by_type': self.error_stats['by_type'],
            'by_severity': self.error_stats['by_severity'],
            'circuit_breakers': self.get_all_circuit_breakers_status(),
        }

    def reset_circuit_breaker(self, name: str):
        """
        Reset a circuit breaker.

        Args:
            name: Circuit breaker name
        """
        if name in self.circuit_breakers:
            cb = self.circuit_breakers[name]
            cb.state = "closed"
            cb.failure_count = 0
            cb.half_open_successes = 0
            self.logger.info(f'Circuit breaker {name} reset')

    def create_recovery_report(self) -> str:
        """
        Create a recovery report.

        Returns:
            Markdown formatted report
        """
        summary = self.get_error_summary()

        report = f"""# Error Recovery Report

## Summary
- **Total Errors:** {summary['total_errors']}
- **Recovered:** {summary['recovered']}
- **Unrecoverable:** {summary['unrecoverable']}
- **Recovery Rate:** {summary['recovery_rate']:.1f}%

## Errors by Type
"""

        for error_type, count in sorted(
            summary['by_type'].items(),
            key=lambda x: -x[1]
        )[:10]:
            report += f"- {error_type}: {count}\n"

        report += f"""
## Errors by Severity
"""

        for severity, count in summary['by_severity'].items():
            report += f"- {severity}: {count}\n"

        report += f"""
## Circuit Breakers
"""

        for name, status in summary['circuit_breakers'].items():
            state_color = "🟢" if status['state'] == 'closed' else "🔴" if status['state'] == 'open' else "🟡"
            report += f"- {state_color} {name}: {status['state']} "
            report += f"(failures: {status['failure_count']})\n"

        return report


# Global recovery instance
_recovery: Optional[ErrorRecovery] = None


def get_error_recovery(vault_path: str) -> ErrorRecovery:
    """Get or create the global error recovery instance."""
    global _recovery
    if _recovery is None or _recovery.vault_path != Path(vault_path):
        _recovery = ErrorRecovery(vault_path)
    return _recovery


if __name__ == '__main__':
    import sys

    vault_path = r'C:\Project\Hackathon_0\Digital_AI_Employee_FTE\AI_Employee_Vault'
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    recovery = ErrorRecovery(vault_path)

    # Demo: Test retry with failing function
    attempt_count = 0

    @recovery.retry(max_attempts=3, strategy=RecoveryStrategy.EXPONENTIAL_BACKOFF)
    def failing_function():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("Network error")
        return "Success!"

    try:
        result = failing_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed: {e}")

    # Print summary
    summary = recovery.get_error_summary()
    print(f"\nError Summary:")
    print(f"  Total errors: {summary['total_errors']}")
    print(f"  Recovered: {summary['recovered']}")
    print(f"  Recovery rate: {summary['recovery_rate']:.1f}%")
