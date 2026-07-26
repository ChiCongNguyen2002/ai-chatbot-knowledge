"""AI Chatbot Demo - FREE Local LLM with Hybrid Search (BM25 + Semantic)"""

import os
import requests
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uuid

from search import hybrid_search, init_embeddings, DOCUMENTS

app = FastAPI(title="AI Chatbot Demo - FREE")

# ===== MODELS =====
class ChatRequest(BaseModel):
    question: str
    session_id: str = ""

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[dict]

# ===== STARTUP =====
@app.on_event("startup")
async def startup():
    """Initialize search index on startup."""
    init_embeddings()

def search_documents(query: str) -> List[dict]:
    """Wrapper around hybrid search."""
    return hybrid_search(query, top_k=3)

# ===== LLM CALL (LOCAL OLLAMA) =====
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")

def call_ollama(question: str, docs: List[dict]) -> str:
    """Call Ollama running locally - NO API COST"""

    # Build context
    context = "Documents:\n"
    for i, doc in enumerate(docs, 1):
        context += f"\n[{i}] {doc['title']}\n{doc['text']}\n"

    prompt = f"""Answer based on these documents:

{context}

Question: {question}

Answer:"""

    try:
        # Call Ollama (running locally on port 11434)
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=60
        )

        if response.status_code == 200:
            return response.json().get("response", "No response")
        else:
            # Fallback: return summary of documents when LLM fails
            return f"⚠️ LLM unavailable. Based on documents: {', '.join([d['title'] for d in docs])} - please check the sources for details."

    except requests.exceptions.ConnectionError:
        return "⚠️ Ollama server not responding. Try again in a moment..."
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

# ===== API ENDPOINTS =====
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint - uses FREE local Ollama"""

    session_id = request.session_id or str(uuid.uuid4())

    # Search documents
    docs = search_documents(request.question)

    # Get answer from Ollama (running locally, NO API COST)
    answer = call_ollama(request.question, docs)

    # Format response with citations
    sources = [
        {
            "id": doc["id"],
            "title": doc["title"],
            "url": doc["url"],
            "text": doc["text"][:200] + "..."
        }
        for doc in docs[:3]
    ]

    return ChatResponse(
        session_id=session_id,
        answer=answer,
        sources=sources
    )

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "cost": "$0.00",
        "type": f"LOCAL LLM (Ollama {OLLAMA_MODEL})",
        "search": "BM25 keyword ranking",
        "documents": len(DOCUMENTS),
        "note": "Running completely local - NO API calls, NO credit card needed"
    }

# ===== WEB UI =====
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 AI Chatbot - FREE Local LLM</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
            .container { max-width: 800px; margin: 20px auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .header h1 { font-size: 24px; margin-bottom: 8px; }
            .header p { opacity: 0.9; font-size: 14px; }
            .chat-box { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .messages { height: 400px; overflow-y: auto; margin-bottom: 20px; border: 1px solid #e0e0e0; padding: 15px; border-radius: 4px; background: #fafafa; }
            .message { margin-bottom: 12px; padding: 10px; border-radius: 4px; }
            .user-msg { background: #667eea; color: white; margin-left: 40px; }
            .bot-msg { background: #f0f0f0; margin-right: 40px; }
            .input-group { display: flex; gap: 10px; }
            input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
            button { padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; }
            button:hover { background: #5568d3; }
            .sources { margin-top: 12px; padding-top: 12px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #666; }
            .cost-badge { display: inline-block; background: #4caf50; color: white; padding: 4px 8px; border-radius: 3px; font-size: 12px; margin-top: 10px; }
            .loading { display: none; color: #667eea; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI Chatbot - FREE Local LLM</h1>
                <p>✅ Running on your machine • NO API calls • NO credit card needed</p>
            </div>

            <div class="chat-box">
                <div class="messages" id="messages">
                    <div class="bot-msg">
                        👋 Hello! I'm running on your machine using Mistral 7B (FREE local model).
                        <br><br>
                        Ask me about: Microservices, Architecture, Notifications
                        <div class="cost-badge">💰 Cost: $0.00</div>
                    </div>
                </div>

                <div class="loading" id="loading">⏳ Generating response...</div>

                <div class="input-group">
                    <input type="text" id="question" placeholder="Ask a question..." onkeypress="handleKey(event)">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>

        <script>
            let sessionId = '';

            async function sendMessage() {
                const question = document.getElementById('question').value.trim();
                if (!question) return;

                const messagesDiv = document.getElementById('messages');
                const loading = document.getElementById('loading');

                // Add user message
                messagesDiv.innerHTML += `<div class="message user-msg">${question}</div>`;
                document.getElementById('question').value = '';
                loading.style.display = 'block';
                messagesDiv.scrollTop = messagesDiv.scrollHeight;

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question, session_id: sessionId })
                    });

                    const data = await response.json();
                    sessionId = data.session_id;

                    let botMsg = `<div class="bot-msg">${data.answer}`;

                    // Only show sources if we got a real answer (not an error)
                    if (data.answer && !data.answer.includes("error") && data.sources && data.sources.length > 0) {
                        botMsg += '<div class="sources"><strong>📚 Sources:</strong>';
                        data.sources.forEach((s, i) => {
                            botMsg += `<br>[${i+1}] <a href="${s.url}" target="_blank">${s.title}</a>`;
                        });
                        botMsg += '</div>';
                    }

                    botMsg += '</div>';

                    messagesDiv.innerHTML += botMsg;
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                } catch (error) {
                    messagesDiv.innerHTML += `<div class="bot-msg">❌ Error: ${error.message}</div>`;
                }

                loading.style.display = 'none';
            }

            function handleKey(e) {
                if (e.key === 'Enter') sendMessage();
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("🚀 Starting Chatbot Server...")
    print("💰 Cost: $0.00 (running LOCAL Ollama)")
    print(f"🌐 Listening on: 0.0.0.0:{port}")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=port)
