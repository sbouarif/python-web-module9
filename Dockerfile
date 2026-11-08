FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
   PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
   apt-get upgrade -y && \
   apt-get install -y --no-install-recommends gcc python3-dev libssl-dev && \
   rm -rf /var/lib/apt/lists/* && \
   python -m pip install --upgrade pip "setuptools>=78.1.1" wheel && \
   groupadd -r appgroup && \
   useradd -r -g appgroup appuser

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt && \
       python -m pip install --no-cache-dir --upgrade "setuptools>=78.1.1"

# Install Chromium in a shared location
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Chromium and its required system libraries
RUN python -m playwright install --with-deps chromium

# Create a home directory and give appuser browser access
RUN mkdir -p /home/appuser && \
    chown -R appuser:appgroup /home/appuser && \
    chmod -R a+rX /ms-playwright

COPY . .
RUN chown -R appuser:appgroup /app

USER appuser

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
   CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
