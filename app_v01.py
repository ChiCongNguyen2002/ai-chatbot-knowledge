"""Phase 1: FastAPI MVP - With Greeting Detection"""

import os
import json
import uuid
import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

from search_v01 import search, init_search_index, DOCUMENTS

app = FastAPI(title="AI Chatbot Knowledge v0.1")


# ===== GREETING DETECTION =====
GREETINGS = {
    'hello', 'hi', 'hey', 'greetings', 'what\'s up',
    'chào', 'xin chào', 'alo', 'yo',
    'morning', 'afternoon', 'evening',
    'can you hear me', 'are you there', 'test', 'hello?', 'hi?'
}

def is_greeting(text: str) -> bool:
    """Check if text is a greeting/test message"""
    text_lower = text.lower().strip()

    # Exact matches
    if text_lower in GREETINGS:
        return True

    # Short messages with greeting keywords
    if len(text_lower.split()) <= 2:
        for greeting in GREETINGS:
            if greeting in text_lower:
                return True

    return False

def get_greeting_response() -> str:
    """Return friendly greeting response"""
    responses = [
        "👋 Xin chào! Tôi là knowledge search bot của Anfin. Bạn có câu hỏi gì về công ty không?",
        "Hi 👋 Mình sẵn sàng giúp bạn tìm kiếm kiến thức. Hỏi tôi về microservices, coding standards, hoặc bất kỳ chủ đề nào!",
        "Chào bạn! 😊 Hôm nay bạn muốn biết gì về Anfin?",
    ]
    return random.choice(responses)


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
    init_search_index()


# ===== ENDPOINTS =====
@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "version": "0.1 MVP",
        "documents": len(DOCUMENTS),
        "cost": "$0.00",
        "type": "BM25 keyword search + greeting detection"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint - Phase 1 MVP with greeting detection"""

    session_id = request.session_id or str(uuid.uuid4())

    # Check if greeting
    if is_greeting(request.question):
        return ChatResponse(
            session_id=session_id,
            answer=get_greeting_response(),
            sources=[]
        )

    # Search for relevant docs
    docs = search(request.question, top_k=3)

    if not docs:
        answer = "Xin lỗi, không tìm thấy tài liệu liên quan. Bạn có thể rephrase câu hỏi không?"
        sources = []
    else:
        # Phase 1: Simple template answer (not LLM synthesis yet)
        top_doc = docs[0]
        answer = f"""Based on company knowledge base:

**{top_doc['title']}**

{top_doc['content'][:300]}...

[Learn more in {top_doc['source']}]"""

        # Format sources
        sources = [
            {
                "id": doc["id"],
                "title": doc["title"],
                "source": doc["source"],
                "url": doc["url"],
                "score": round(doc["score"], 2)
            }
            for doc in docs
        ]

    return ChatResponse(
        session_id=session_id,
        answer=answer,
        sources=sources
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    """Web UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Anfin Knowledge Search v0.1</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                max-width: 900px;
                width: 100%;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }
            .header h1 { font-size: 32px; margin-bottom: 8px; }
            .header p { opacity: 0.9; font-size: 14px; }
            .badge {
                display: inline-block;
                background: rgba(255,255,255,0.2);
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                margin-top: 12px;
            }
            .chat-container {
                padding: 30px;
                min-height: 400px;
                display: flex;
                flex-direction: column;
            }
            .messages {
                flex: 1;
                overflow-y: auto;
                margin-bottom: 20px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                background: #fafafa;
            }
            .message {
                margin-bottom: 15px;
                padding: 12px;
                border-radius: 6px;
                line-height: 1.6;
            }
            .user-msg {
                background: #667eea;
                color: white;
                margin-left: 40px;
                text-align: right;
            }
            .bot-msg {
                background: white;
                border: 1px solid #ddd;
                margin-right: 40px;
            }
            .input-group {
                display: flex;
                gap: 10px;
            }
            input {
                flex: 1;
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
            }
            input:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                padding: 12px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 500;
                font-size: 14px;
            }
            button:hover { background: #5568d3; }
            .sources {
                margin-top: 12px;
                padding-top: 12px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
            }
            .source-item {
                margin: 6px 0;
                padding: 8px;
                background: #f5f5f5;
                border-radius: 4px;
            }
            .loading {
                display: none;
                color: #667eea;
                font-style: italic;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Anfin Knowledge Search</h1>
                <p>Search company knowledge base instantly</p>
                <div class="badge">v0.1 MVP | 10 Documents | $0.00 | Greeting Detection ✅</div>
            </div>

            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="bot-msg">
                        👋 Xin chào! Tôi là knowledge search bot của Anfin.
                        <br><br>
                        Bạn có thể hỏi tôi về:
                        <br>• Microservices
                        <br>• Coding standards
                        <br>• Testing strategy
                        <br>• API design
                        <br>• Deployment process
                    </div>
                </div>

                <div class="loading" id="loading">⏳ Searching...</div>

                <div class="input-group">
                    <input type="text" id="question" placeholder="Hỏi gì đó..." onkeypress="if(event.key==='Enter') sendMessage()">
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

                    if (data.sources && data.sources.length > 0) {
                        botMsg += '<div class="sources"><strong>📚 Sources:</strong>';
                        data.sources.forEach((s, i) => {
                            botMsg += `<div class="source-item">[${i+1}] <a href="${s.url}" target="_blank">${s.title}</a> (score: ${s.score})</div>`;
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
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("🚀 Starting Anfin Knowledge Search v0.1")
    print(f"💰 Cost: $0.00 (local BM25 search + greeting detection)")
    print(f"🌐 Listening on: 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
