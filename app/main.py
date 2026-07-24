from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.audit import router as audit_router
from app.middleware.request_context import request_context_middleware


app = FastAPI(
    title="Page Pulse",
    description="Production-ready URL auditing API",
    version="1.0.0",
)

app.middleware("http")(request_context_middleware)

app.include_router(audit_router)


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Page Pulse</title>

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                min-height: 100vh;
                font-family: Arial, sans-serif;
                background: #0f172a;
                color: #f8fafc;
                display: flex;
                flex-direction: column;
            }

            main {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 40px 20px;
            }

            .card {
                max-width: 700px;
                text-align: center;
                padding: 50px;
                background: #1e293b;
                border-radius: 18px;
            }

            h1 {
                font-size: 48px;
                margin-bottom: 15px;
            }

            p {
                color: #cbd5e1;
                line-height: 1.6;
            }

            .button {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 22px;
                background: #f8fafc;
                color: #0f172a;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
            }

            footer {
                text-align: center;
                padding: 20px;
                color: #94a3b8;
            }

            footer a {
                color: #e2e8f0;
            }
        </style>
    </head>

    <body>

        <main>
            <section class="card">
                <h1>Page Pulse</h1>

                <p>
                    A production-oriented URL auditing API
                    built with FastAPI.
                </p>

                <p>
                    Validate URLs, inspect response metadata,
                    cache repeat audits and protect the API
                    through concurrency and rate controls.
                </p>

                <a class="button" href="/docs">
                    Open API Documentation
                </a>
            </section>
        </main>

        <footer>
            <a
                href="https://digitalheroesco.com"
                target="_blank"
                rel="noopener noreferrer"
            >
                Built for Digital Heroes Training Task
            </a>
        </footer>

    </body>
    </html>
    """


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }