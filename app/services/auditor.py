import asyncio
import re
import time

import httpx

from app.config import settings
from app.models.schemas import AuditResponse


audit_semaphore = asyncio.Semaphore(
    settings.max_concurrent_audits
)


def extract_title(html: str) -> str | None:
    match = re.search(
        r"<title[^>]*>(.*?)</title>",
        html,
        re.IGNORECASE | re.DOTALL,
    )

    if match:
        return match.group(1).strip()

    return None


async def audit_url(url: str) -> AuditResponse:

    async with audit_semaphore:

        start_time = time.perf_counter()

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(settings.request_timeout),
            follow_redirects=True,
        ) as client:

            response = await client.get(url)

        elapsed = (time.perf_counter() - start_time) * 1000

        content_type = response.headers.get("content-type")

        title = None

        if content_type and "text/html" in content_type.lower():
            title = extract_title(response.text)

        return AuditResponse(
            url=str(response.url),
            status_code=response.status_code,
            response_time_ms=round(elapsed, 2),
            content_type=content_type,
            content_length=len(response.content),
            title=title,
            cached=False,
        )