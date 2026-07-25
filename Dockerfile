# Build on ollama/ollama base (has all Ollama dependencies)
FROM ollama/ollama:latest

# Add Python to the ollama image
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3-pip python3.11-venv curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

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
