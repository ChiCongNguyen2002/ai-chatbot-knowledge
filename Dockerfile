# Build on Python 3.11 base + install Ollama
FROM python:3.11-slim

# Install Ollama + dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates zstd \
    && curl -fsSL https://ollama.ai/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app_demo.py search.py entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Environment for Railway
ENV OLLAMA_HOST=http://localhost:11434
ENV OLLAMA_MODEL=phi3:mini

# Bake models into image at BUILD time
RUN (ollama serve &) && sleep 5 \
    && ollama pull phi3:mini \
    && ollama pull bge-m3 \
    && pkill ollama || true

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
