import time
from dataclasses import dataclass

from app.config import settings
from app.models.schemas import AuditResponse


@dataclass
class CacheEntry:
    value: AuditResponse
    expires_at: float


class AuditCache:
    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}

    def get(self, url: str) -> AuditResponse | None:
        entry = self._cache.get(url)

        if entry is None:
            return None

        if time.monotonic() >= entry.expires_at:
            del self._cache[url]
            return None

        # Return a copy so we don't mutate the stored response.
        return entry.value.model_copy(
            update={"cached": True}
        )

    def set(self, url: str, result: AuditResponse) -> None:
        self._cache[url] = CacheEntry(
            value=result.model_copy(update={"cached": False}),
            expires_at=(
                time.monotonic()
                + settings.cache_ttl_seconds
            ),
        )


audit_cache = AuditCache()