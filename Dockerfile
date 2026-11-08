FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /app

# Install system dependencies and curl for health checks
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        curl gcc python3-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN python -m pip install --no-cache-dir \
        --upgrade pip "setuptools>=78.1.1" wheel && \
    python -m pip install --no-cache-dir \
        -r requirements.txt && \
    python -m pip install --no-cache-dir \
        --upgrade "setuptools>=78.1.1"

# Install Playwright Chromium
RUN python -m playwright install --with-deps chromium

# Create a non-root user
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -m appuser && \
    chmod -R a+rX /ms-playwright

# Copy application files
COPY . .

RUN chown -R appuser:appgroup /app

USER appuser

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]