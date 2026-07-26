FROM ollama/ollama:latest AS ollama-base

FROM python:3.11-slim

# Copy Ollama binary from base image
COPY --from=ollama-base /bin/ollama /usr/local/bin/ollama

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
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
    ./

# Environment
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://localhost:11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# Simple: Ollama background + FastAPI foreground
CMD ["/bin/bash", "-c", "ollama serve >/dev/null 2>&1 & sleep 2 && python entrypoint_simple.py"]
