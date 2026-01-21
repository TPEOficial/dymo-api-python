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
    
    def update_rate_limit(self, client_id: str, headers: Dict[str, str]):
        if client_id not in self.client_limits:
            self.client_limits[client_id] = {}
        
        limit_info = self.client_limits[client_id]
        
        # Update rate limit headers
        if 'X-Ratelimit-Limit-Requests' in headers:
            limit_info['limit'] = int(headers['X-Ratelimit-Limit-Requests'])
        if 'X-Ratelimit-Remaining-Requests' in headers:
            limit_info['remaining'] = int(headers['X-Ratelimit-Remaining-Requests'])
        if 'X-Ratelimit-Reset-Requests' in headers:
            limit_info['reset_time'] = headers['X-Ratelimit-Reset-Requests']
        if 'retry-after' in headers:
            limit_info['retry_after'] = int(headers['retry-after'])
        
        limit_info['last_updated'] = time.time()
    
    def is_rate_limited(self, client_id: str) -> bool:
        if client_id not in self.client_limits:
            return False
        
        limit_info = self.client_limits[client_id]
        return limit_info.get('remaining', 1) <= 0
    
    def get_retry_after(self, client_id: str) -> Optional[int]:
        if client_id not in self.client_limits:
            return None
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
                if hasattr(e, 'response') and e.response and e.response.status_code == 429:
                    should_retry = False
                
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
        if error.response is None and not hasattr(error, 'timeout'): 
            return True
            
        # Server errors (5xx) - retry
        if error.response is not None and 500 <= error.response.status_code < 600: 
            return True
            
        # Rate limiting (429) - DO NOT retry (handled separately)
        if error.response is not None and error.response.status_code == 429: 
            return False
            
        # Don't retry on client errors (4xx except 429)
        return False