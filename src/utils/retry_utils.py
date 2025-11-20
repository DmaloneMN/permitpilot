"""
Retry utilities with exponential backoff and jitter.
- retry_with_backoff: decorator for automatic retries
- RetryConfig: configuration for retry behavior
"""
import time
import random
from typing import Callable, Type, Tuple, Optional
from functools import wraps


class RetryConfig:
    """Configuration for retry behavior."""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorator that retries a function with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to avoid thundering herd
        retryable_exceptions: Tuple of exception types to retry on
    
    Returns:
        Decorated function that retries on failure
    
    Example:
        @retry_with_backoff(max_attempts=3, base_delay=2.0)
        def call_api():
            return requests.get("https://api.example.com/data")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt, raise the exception
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Add jitter if enabled (±25% of delay)
                    if jitter:
                        jitter_range = delay * 0.25
                        delay = delay + random.uniform(-jitter_range, jitter_range)
                    
                    # Ensure delay is non-negative
                    delay = max(0, delay)
                    
                    print(f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                          f"Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            
            # Should not reach here, but raise last exception if it does
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def retry_with_config(config: RetryConfig) -> Callable:
    """
    Decorator that retries a function using a RetryConfig object.
    
    Args:
        config: RetryConfig object with retry parameters
    
    Returns:
        Decorated function that retries on failure
    
    Example:
        config = RetryConfig(max_attempts=3, base_delay=2.0)
        
        @retry_with_config(config)
        def call_api():
            return requests.get("https://api.example.com/data")
    """
    return retry_with_backoff(
        max_attempts=config.max_attempts,
        base_delay=config.base_delay,
        max_delay=config.max_delay,
        exponential_base=config.exponential_base,
        jitter=config.jitter,
        retryable_exceptions=config.retryable_exceptions
    )


if __name__ == "__main__":
    # Example usage
    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    def flaky_function(fail_count: int = 0):
        """Simulates a flaky function that fails a few times."""
        if hasattr(flaky_function, 'calls'):
            flaky_function.calls += 1
        else:
            flaky_function.calls = 1
        
        if flaky_function.calls <= fail_count:
            raise ValueError(f"Simulated failure (attempt {flaky_function.calls})")
        
        return f"Success after {flaky_function.calls} attempts"
    
    try:
        result = flaky_function(fail_count=2)
        print(result)
    except Exception as e:
        print(f"Failed after all retries: {e}")
