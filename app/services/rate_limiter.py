import time
from collections import defaultdict, deque

from app.config import settings


class RateLimiter:
    def __init__(self):
        self.requests: dict[str, deque] = defaultdict(deque)

    def is_allowed(self, client_id: str) -> tuple[bool, int]:
        now = time.monotonic()

        window_start = (
            now - settings.rate_limit_window_seconds
        )

        client_requests = self.requests[client_id]

        # Remove requests outside the current window
        while (
            client_requests
            and client_requests[0] <= window_start
        ):
            client_requests.popleft()

        if len(client_requests) >= settings.rate_limit_requests:
            retry_after = int(
                settings.rate_limit_window_seconds
                - (now - client_requests[0])
            ) + 1

            return False, retry_after

        client_requests.append(now)

        return True, 0


rate_limiter = RateLimiter()