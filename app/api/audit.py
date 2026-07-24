import httpx

from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import AuditRequest, AuditResponse
from app.services.auditor import audit_url
from app.services.cache import audit_cache
from app.services.rate_limiter import rate_limiter


router = APIRouter(
    prefix="/api/v1",
    tags=["Audit"],
)


@router.post("/audit", response_model=AuditResponse)
async def create_audit(
    audit_request: AuditRequest,
    request: Request,
):
    url = str(audit_request.url)

    # Identify the client by IP address
    client_id = (
        request.client.host
        if request.client
        else "unknown"
    )

    # Apply per-client rate limiting
    allowed, retry_after = rate_limiter.is_allowed(client_id)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many audit requests.",
                "retry_after_seconds": retry_after,
            },
            headers={
                "Retry-After": str(retry_after)
            },
        )

    # Check whether this URL was recently audited
    cached_result = audit_cache.get(url)

    if cached_result:
        return cached_result

    try:
        # Perform the actual URL audit
        result = await audit_url(url)

        # Store successful result in cache
        audit_cache.set(url, result)

        return result

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail={
                "code": "UPSTREAM_TIMEOUT",
                "message": (
                    "The target website did not respond "
                    "within the allowed time."
                ),
            },
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "UPSTREAM_REQUEST_FAILED",
                "message": (
                    "Page Pulse could not reach "
                    "the target website."
                ),
            },
        )