# Multi-stage: extract ollama binary, then build single container for HF Spaces
FROM ollama/ollama:latest AS ollama-src

FROM python:3.11-slim
COPY --from=ollama-src /bin/ollama /usr/local/bin/ollama

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app_demo.py search.py entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Environment for HF Spaces (localhost) + smaller model to fit free tier
ENV OLLAMA_HOST=http://localhost:11434
ENV OLLAMA_MODEL=phi3:mini

# Bake models into image at BUILD time (not runtime) to avoid 3.5GB re-download on every restart
RUN (ollama serve &) && sleep 5 \
    && ollama pull phi3:mini \
    && ollama pull bge-m3 \
    && pkill ollama || true

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
