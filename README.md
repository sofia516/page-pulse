# Page Pulse

Page Pulse is a production-oriented URL auditing API built as part of the Digital Heroes Software Development qualification task.

It accepts a URL, fetches the target page, and returns useful information such as HTTP status, response time, content type, content length, and page title.

## Features

- URL input validation
- Async HTTP auditing
- Configurable request timeouts
- Concurrency limiting
- TTL-based caching
- Per-client rate limiting
- Structured JSON logging
- Request IDs for tracing
- Structured upstream error responses
- Automated pytest test suite
- GitHub Actions CI
- Health endpoint

## Tech Stack

- Python
- FastAPI
- HTTPX
- Pydantic
- Pytest
- GitHub Actions

## Project Structure

```text
app/
├── api/
│   └── audit.py
├── middleware/
│   └── request_context.py
├── models/
│   └── schemas.py
├── services/
│   ├── auditor.py
│   ├── cache.py
│   └── rate_limiter.py
├── config.py
└── main.py

tests/
└── test_api.py
```

## API Contract

### POST `/api/v1/audit`

Audits a publicly accessible HTTP/HTTPS URL.

Request:

```json
{
  "url": "https://example.com"
}
```

Successful response:

```json
{
  "url": "https://example.com/",
  "status_code": 200,
  "response_time_ms": 191.08,
  "content_type": "text/html",
  "content_length": 559,
  "title": "Example Domain",
  "cached": false
}
```

### Validation Error

Invalid URLs return HTTP `422`.

### Rate Limit

Clients are limited to a configurable number of requests per time window.

When the limit is exceeded:

```json
{
  "detail": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many audit requests.",
    "retry_after_seconds": 42
  }
}
```

HTTP status: `429`

A `Retry-After` header is also returned.

### Upstream Timeout

```json
{
  "detail": {
    "code": "UPSTREAM_TIMEOUT",
    "message": "The target website did not respond within the allowed time."
  }
}
```

HTTP status: `504`

### Upstream Connection Failure

HTTP status: `502`

Error code:

```text
UPSTREAM_REQUEST_FAILED
```

### GET `/health`

Response:

```json
{
  "status": "healthy"
}
```

## Request IDs

Every request receives an `X-Request-ID` response header.

Clients may also provide their own `X-Request-ID`, allowing a request to be traced through structured application logs.

## Configuration

Copy:

```bash
cp .env.example .env
```

Available settings:

| Variable | Default | Purpose |
|---|---:|---|
| REQUEST_TIMEOUT | 10 | Maximum upstream request duration |
| MAX_CONCURRENT_AUDITS | 10 | Maximum simultaneous audits |
| CACHE_TTL_SECONDS | 300 | Audit cache lifetime |
| RATE_LIMIT_REQUESTS | 10 | Requests allowed per client |
| RATE_LIMIT_WINDOW_SECONDS | 60 | Rate-limit window |

## Running Locally

Create a virtual environment and install dependencies:

```bash
python -m venv venv
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Swagger documentation is available at `/docs`.

## Tests

Run:

```bash
pytest -v
```

The test suite covers:

- Health checks
- URL validation
- Successful audits
- Cache behavior
- Rate limiting
- Request IDs
- Custom request-ID propagation
- Upstream timeout handling

Tests also run automatically through GitHub Actions on pushes and pull requests.

## Production Scaling Note

The current implementation intentionally keeps caching and rate-limit state in process for a lightweight single-instance deployment.

For horizontal scaling, I would move this shared state to Redis so multiple API instances observe the same cache entries and client limits. The scaling architecture and trade-offs are covered separately in Task B.

## AI Usage

I used AI as a development assistant to pressure-test the API structure, identify production concerns such as request tracing and failure handling, and review test cases. I implemented and ran the application locally, verified each behavior through Swagger and pytest, and adjusted the implementation based on the observed results rather than submitting generated code without validation.

---

Built for Digital Heroes Training Task.