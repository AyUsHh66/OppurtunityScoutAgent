"""
Production-grade error handling and retry logic
Includes circuit breaker pattern, exponential backoff, and error categorization
"""

import time
from functools import wraps
from typing import Callable, Any, Optional, Type, Tuple, List
from datetime import datetime, timedelta
from enum import Enum

from core_engine.logging_config import get_logger

logger = get_logger(__name__)


class ErrorCategory(str, Enum):
    """Error categorization"""
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        
        self.logger = get_logger(__name__)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.logger.info(f"Circuit breaker half-open for {func.__name__}")
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN for {func.__name__}. "
                    f"Retry after {self.recovery_timeout} seconds."
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not self.last_failure_time:
            return True
        
        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure >= timedelta(seconds=self.recovery_timeout)
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.logger.info("Circuit breaker CLOSED (recovered)")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.logger.warning(f"Circuit breaker OPEN (still failing)")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.error(f"Circuit breaker OPEN after {self.failure_count} failures")


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        logger.info(f"Retry {attempt}/{max_retries} for {func.__name__} "
                                   f"(waiting {delay:.1f}s)")
                        time.sleep(delay)
                    
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = min(delay * backoff_factor, max_delay)
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def categorize_error(exception: Exception) -> ErrorCategory:
        """Categorize an exception"""
        error_str = str(exception).lower()
        error_type = type(exception).__name__
        
        if 'rate limit' in error_str or 'too many requests' in error_str:
            return ErrorCategory.RATE_LIMIT
        elif 'timeout' in error_str:
            return ErrorCategory.TIMEOUT
        elif 'connection' in error_str or 'resolve' in error_str:
            return ErrorCategory.CONNECTION
        elif 'unauthorized' in error_str or 'authentication' in error_str:
            return ErrorCategory.AUTHENTICATION
        elif 'not found' in error_str or 'does not exist' in error_str:
            return ErrorCategory.NOT_FOUND
        elif 'validation' in error_str or 'invalid' in error_str:
            return ErrorCategory.VALIDATION
        else:
            return ErrorCategory.UNKNOWN
    
    @staticmethod
    def is_retryable(exception: Exception) -> bool:
        """Check if error is retryable"""
        category = ErrorHandler.categorize_error(exception)
        
        retryable_categories = [
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.TIMEOUT,
            ErrorCategory.CONNECTION,
        ]
        
        return category in retryable_categories
    
    @staticmethod
    def get_retry_delay(exception: Exception, attempt: int) -> float:
        """Get recommended retry delay for exception"""
        category = ErrorHandler.categorize_error(exception)
        
        # Rate limit errors: exponential backoff
        if category == ErrorCategory.RATE_LIMIT:
            return min(2 ** attempt, 60)
        
        # Timeout: linear backoff
        if category == ErrorCategory.TIMEOUT:
            return min(attempt * 2, 30)
        
        # Connection: exponential backoff
        if category == ErrorCategory.CONNECTION:
            return min(2 ** attempt, 60)
        
        # Default: 1 second
        return 1.0


class ErrorContext:
    """Context for error handling with recovery information"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.errors: List[Tuple[datetime, Exception]] = []
        self.start_time = datetime.now()
    
    def add_error(self, exception: Exception):
        """Record an error"""
        self.errors.append((datetime.now(), exception))
    
    def get_error_summary(self) -> str:
        """Get summary of errors"""
        if not self.errors:
            return "No errors"
        
        duration = datetime.now() - self.start_time
        summary = f"Operation '{self.operation_name}' failed after {duration.total_seconds():.2f}s\n"
        summary += f"Total errors: {len(self.errors)}\n\n"
        
        for i, (timestamp, error) in enumerate(self.errors, 1):
            category = ErrorHandler.categorize_error(error)
            summary += f"{i}. [{category.value}] {error}\n"
        
        return summary
    
    def should_continue(self, max_errors: int = 3) -> bool:
        """Check if should continue based on error count"""
        return len(self.errors) < max_errors


def safe_call(
    func: Callable,
    *args,
    operation_name: str = "Operation",
    max_retries: int = 3,
    logger_instance = None,
    **kwargs
) -> Optional[Any]:
    """
    Safely call a function with error handling and retries
    
    Args:
        func: Function to call
        operation_name: Name of operation for logging
        max_retries: Maximum number of retries
        logger_instance: Logger to use
    
    Returns:
        Function result or None if failed
    """
    if logger_instance is None:
        logger_instance = logger
    
    error_context = ErrorContext(operation_name)
    
    for attempt in range(max_retries + 1):
        try:
            logger_instance.debug(f"Executing {operation_name} (attempt {attempt + 1}/{max_retries + 1})")
            return func(*args, **kwargs)
        
        except Exception as e:
            error_context.add_error(e)
            
            if not ErrorHandler.is_retryable(e) or attempt >= max_retries:
                logger_instance.error(error_context.get_error_summary())
                return None
            
            delay = ErrorHandler.get_retry_delay(e, attempt)
            logger_instance.warning(f"{operation_name} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
    
    return None


def handle_api_error(func: Callable) -> Callable:
    """Decorator for handling API errors"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Optional[Any]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            category = ErrorHandler.categorize_error(e)
            logger.error(f"API Error in {func.__name__}: [{category.value}] {e}")
            return None
    
    return wrapper


# Example usage:
# @retry_with_backoff(max_retries=3)
# def my_api_call():
#     ...
#
# Or use safe_call:
# result = safe_call(my_function, arg1, arg2, operation_name="My Operation")
