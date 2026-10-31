"""
Rate Limiter & Account Protection Module for SIH26101 Platform.
Implements:
1. IP-based rate limiting with sliding time windows for registration, login, and password reset.
2. In-database account lockout threshold tracking (5 failed attempts -> 15-minute lock).
3. Thread-safe in-memory cache for sliding windows.
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

RATE_LIMIT_RULES = {
    "login": {"max_requests": 10, "window_seconds": 60},             # 10 / min / IP
    "register": {"max_requests": 5, "window_seconds": 3600},          # 5 / hr / IP
    "password_reset": {"max_requests": 3, "window_seconds": 3600},    # 3 / hr / IP
    "verify_email": {"max_requests": 10, "window_seconds": 300},      # 10 / 5 min / IP
}


class InMemoryRateLimiter:
    """Sliding-window in-memory rate limiter per action and client IP."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._history: Dict[Tuple[str, str], List[float]] = {}

    def is_allowed(self, action: str, client_ip: str) -> Tuple[bool, int]:
        """
        Check if request is permitted under rate limit rule.
        Returns: (allowed: bool, retry_after_seconds: int)
        """
        rule = RATE_LIMIT_RULES.get(action)
        if not rule:
            return True, 0

        max_req = rule["max_requests"]
        window = rule["window_seconds"]
        now = time.time()
        key = (action, client_ip)

        with self._lock:
            timestamps = self._history.get(key, [])
            # Prune timestamps outside window
            cutoff = now - window
            timestamps = [ts for ts in timestamps if ts > cutoff]

            if len(timestamps) >= max_req:
                oldest = timestamps[0]
                retry_after = max(1, int(oldest + window - now))
                self._history[key] = timestamps
                return False, retry_after

            timestamps.append(now)
            self._history[key] = timestamps
            return True, 0

    def reset(self) -> None:
        """Clear all rate limit history (for testing)."""
        with self._lock:
            self._history.clear()


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


def is_user_locked_out(lockout_until: Optional[datetime]) -> bool:
    """Check if account is currently locked out."""
    if not lockout_until:
        return False
    now = datetime.now(timezone.utc)
    if lockout_until.tzinfo is None:
        lockout_until = lockout_until.replace(tzinfo=timezone.utc)
    return lockout_until > now


def calculate_new_lockout(current_failed_attempts: int) -> Tuple[int, Optional[datetime]]:
    """
    Calculate updated failed_attempts count and optional lockout_until timestamp.
    """
    new_count = current_failed_attempts + 1
    if new_count >= MAX_FAILED_ATTEMPTS:
        lockout_time = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        return new_count, lockout_time
    return new_count, None

