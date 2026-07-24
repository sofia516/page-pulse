from unittest.mock import AsyncMock, patch

import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.services.cache import audit_cache
from app.services.rate_limiter import rate_limiter
from app.models.schemas import AuditResponse


client = TestClient(app)


def reset_state():
    audit_cache._cache.clear()
    rate_limiter.requests.clear()


def setup_function():
    reset_state()


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_invalid_url():
    response = client.post(
        "/api/v1/audit",
        json={"url": "not-a-valid-url"},
    )

    assert response.status_code == 422


@patch("app.api.audit.audit_url", new_callable=AsyncMock)
def test_successful_audit(mock_audit):
    mock_audit.return_value = AuditResponse(
        url="https://example.com/",
        status_code=200,
        response_time_ms=100.0,
        content_type="text/html",
        content_length=559,
        title="Example Domain",
        cached=False,
    )

    response = client.post(
        "/api/v1/audit",
        json={"url": "https://example.com"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status_code"] == 200
    assert data["title"] == "Example Domain"
    assert data["cached"] is False


@patch("app.api.audit.audit_url", new_callable=AsyncMock)
def test_cache_is_used(mock_audit):
    mock_audit.return_value = AuditResponse(
        url="https://example.com/",
        status_code=200,
        response_time_ms=100.0,
        content_type="text/html",
        content_length=559,
        title="Example Domain",
        cached=False,
    )

    first = client.post(
        "/api/v1/audit",
        json={"url": "https://example.com"},
    )

    second = client.post(
        "/api/v1/audit",
        json={"url": "https://example.com"},
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json()["cached"] is False
    assert second.json()["cached"] is True

    # The real audit function should only run once.
    assert mock_audit.await_count == 1


def test_request_id_header():
    response = client.get("/health")

    assert response.status_code == 200
    assert "x-request-id" in response.headers


def test_custom_request_id_is_preserved():
    response = client.get(
        "/health",
        headers={
            "X-Request-ID": "page-pulse-test-123"
        },
    )

    assert response.status_code == 200

    assert (
        response.headers["x-request-id"]
        == "page-pulse-test-123"
    )


@patch("app.api.audit.audit_url", new_callable=AsyncMock)
def test_upstream_timeout(mock_audit):
    mock_audit.side_effect = httpx.TimeoutException(
        "Target timed out"
    )

    response = client.post(
        "/api/v1/audit",
        json={"url": "https://example.com"},
    )

    assert response.status_code == 504
    assert (
        response.json()["detail"]["code"]
        == "UPSTREAM_TIMEOUT"
    )

@patch("app.api.audit.audit_url", new_callable=AsyncMock)
def test_rate_limit(mock_audit):
    mock_audit.return_value = AuditResponse(
        url="https://example.com/",
        status_code=200,
        response_time_ms=100.0,
        content_type="text/html",
        content_length=559,
        title="Example Domain",
        cached=False,
    )

    # Send the maximum number of allowed requests.
    for _ in range(10):
        response = client.post(
            "/api/v1/audit",
            json={"url": "https://example.com"},
        )

        assert response.status_code == 200

    # The next request should be rejected.
    response = client.post(
        "/api/v1/audit",
        json={"url": "https://example.com"},
    )

    assert response.status_code == 429

    data = response.json()

    assert (
        data["detail"]["code"]
        == "RATE_LIMIT_EXCEEDED"
    )

    assert "Retry-After" in response.headers    