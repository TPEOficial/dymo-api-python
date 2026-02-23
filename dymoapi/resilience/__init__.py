import time
import logging
from typing import Any, Dict, Optional, TypeVar, Callable
from requests import Session, RequestException
from .fallback import FallbackDataGenerator

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RateLimitTracker:
    def __init__(self):
        self.client_limits = {}  # client_id -> rate_limit_info

    def _parse_header_value(self, value: Any) -> Optional[int]:
        """
        Parses a header value that could be a number or "unlimited".
        Returns None if the value is "unlimited", None, or invalid.
        """
        # Handle non-string types (lists, dicts, None, etc.)
        if value is None: return None
        if isinstance(value, (list, dict)): return None

        # Convert to string and normalize
        try: str_value = str(value).strip().lower()
        except Exception: return None

        if not str_value or str_value == "unlimited": return None

        try:
            # Handle floats by converting to float first, then int
            parsed = int(float(str_value))
            # Rate limits can't be negative
            return parsed if parsed >= 0 else None
        except (ValueError, TypeError): return None

    def update_rate_limit(self, client_id: str, headers: Dict[str, str]):
        if client_id not in self.client_limits: self.client_limits[client_id] = {}

        limit_info = self.client_limits[client_id]

        # Get header values (case-insensitive lookup)
        headers_lower = {k.lower(): v for k, v in headers.items()}

        limit_requests = headers_lower.get('x-ratelimit-limit-requests')
        remaining_requests = headers_lower.get('x-ratelimit-remaining-requests')
        reset_requests = headers_lower.get('x-ratelimit-reset-requests')
        retry_after = headers_lower.get('retry-after')

        # Only update numeric values if they are valid numbers (not "unlimited")
        parsed_limit = self._parse_header_value(limit_requests)
        parsed_remaining = self._parse_header_value(remaining_requests)
        parsed_retry_after = self._parse_header_value(retry_after)

        if parsed_limit is not None: limit_info['limit'] = parsed_limit
        if parsed_remaining is not None: limit_info['remaining'] = parsed_remaining
        # Mark as unlimited if header explicitly says "unlimited"
        if remaining_requests is not None:
            try:
                if str(remaining_requests).strip().lower() == "unlimited": limit_info['is_unlimited'] = True
            except Exception: pass
        if reset_requests: limit_info['reset_time'] = reset_requests
        if parsed_retry_after is not None: limit_info['retry_after'] = parsed_retry_after

        limit_info['last_updated'] = time.time()

    def is_rate_limited(self, client_id: str) -> bool:
        if client_id not in self.client_limits: return False

        limit_info = self.client_limits[client_id]
        # If marked as unlimited, never rate limited
        if limit_info.get('is_unlimited', False): return False
        # Only consider rate limited if remaining is explicitly set and is 0 or less
        remaining = limit_info.get('remaining')
        return remaining is not None and remaining <= 0
    
    def get_retry_after(self, client_id: str) -> Optional[int]:
        if client_id not in self.client_limits: return None
        return self.client_limits[client_id].get('retry_after')

# Global rate limit tracker
_rate_tracker = RateLimitTracker()

class ResilienceConfig:
    def __init__(
        self,
        fallback_enabled: bool = False,
        retry_attempts: int = 2,
        retry_delay: int = 1000
    ):
        self.fallback_enabled = fallback_enabled
        self.retry_attempts = max(0, retry_attempts)  # Número de reintentos adicionales
        self.retry_delay = max(0, retry_delay)

class ResilienceManager:
    def __init__(self, config: Optional[ResilienceConfig] = None, client_id: str = "default"):
        self.config = config or ResilienceConfig()
        self.client_id = client_id
    
    def get_config(self) -> ResilienceConfig:
        return self.config
    
    def get_client_id(self) -> str:
        return self.client_id
    
    def execute_with_resilience(
        self,
        session: Session,
        method: str,
        url: str,
        fallback_data: Optional[T] = None,
        **kwargs
    ) -> T:
        """
        Executes HTTP request with resilience capabilities.
        
        Args:
            session: Requests session to use
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            fallback_data: Optional fallback data to return if all retries fail
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Response data or fallback data
            
        Raises:
            RequestException: If all retries fail and no fallback provided
        """
        last_error = None
        total_attempts = 1 + self.config.retry_attempts  # 1 normal + N reintentos
        
        # Check if client is currently rate limited
        if _rate_tracker.is_rate_limited(self.client_id):
            retry_after = _rate_tracker.get_retry_after(self.client_id)
            if retry_after:
                logger.warning(f"[Dymo API] Client {self.client_id} is rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
        
        for attempt in range(1, total_attempts + 1):
            try:
                response = session.request(method, url, **kwargs)
                
                # Update rate limit tracking
                _rate_tracker.update_rate_limit(self.client_id, dict(response.headers))
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = _rate_tracker.get_retry_after(self.client_id)
                    if retry_after:
                        logger.warning(f"[Dymo API] Rate limited. Waiting {retry_after} seconds (no retries)")
                        time.sleep(retry_after)
                    raise RequestException(f"Rate limited (429) - not retrying")
                
                response.raise_for_status()
                return response.json()
                
            except RequestException as e:
                last_error = e
                
                should_retry = self._should_retry(e)
                is_last_attempt = attempt == total_attempts
                
                # Don't retry on rate limiting (429)
                if hasattr(e, 'response') and e.response and e.response.status_code == 429: should_retry = False
                
                if not should_retry or is_last_attempt:
                    if self.config.fallback_enabled and fallback_data is not None:
                        logger.warning(f"[Dymo API] Request failed after {attempt} attempts. Using fallback data.")
                        return fallback_data
                    raise e
                
                delay = self.config.retry_delay * (2 ** (attempt - 1))
                logger.warning(f"[Dymo API] Attempt {attempt} failed. Retrying in {delay}ms...")
                time.sleep(delay / 1000)
        
        raise last_error
    
    def _should_retry(self, error: RequestException) -> bool:
        """
        Determines if a request should be retried based on the error.
        
        Args:
            error: The RequestException that occurred
            
        Returns:
            True if should retry, False otherwise
        """
        # Network errors (no response) - retry
        if error.response is None and not hasattr(error, 'timeout'): return True
            
        # Server errors (5xx) - retry
        if error.response is not None and 500 <= error.response.status_code < 600: return True
            
        # Rate limiting (429) - DO NOT retry (handled separately)
        if error.response is not None and error.response.status_code == 429: return False
            
        # Don't retry on client errors (4xx except 429)
        return False