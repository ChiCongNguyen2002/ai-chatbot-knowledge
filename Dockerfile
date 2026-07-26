FROM ollama/ollama:latest AS ollama-base

FROM python:3.11-slim

# Copy Ollama binary from base image
COPY --from=ollama-base /bin/ollama /usr/local/bin/ollama

WORKDIR /app

# Install system dependencies + supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Phase 4 Lite files (NO Elasticsearch!)
COPY atlassian_ingester_full.py \
    search_simple.py \
    synthesis_ultimate.py \
    app_simple.py \
    entrypoint_simple.py \
    supervisord.conf \
    ./

# Environment
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://localhost:11434
ENV FORCE_REBUILD=v5

# Setup directories for Ollama
RUN mkdir -p /root/.ollama/models

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# Start with supervisor to manage both Ollama + FastAPI
CMD ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]
# Force rebuild 1785052661
