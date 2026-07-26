"""Phase 4 Lite - Mistral synthesis + simple BM25 search, NO Elasticsearch"""

import os
import json
import uuid
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

from search_simple import SimpleSearch
from synthesis_ultimate import get_synthesis_response
from synthesis_fallback import get_fallback_response

app = FastAPI(title="Anfin Knowledge - Phase 4 Lite")
search = SimpleSearch()

GREETINGS = {'hello', 'hi', 'chào', 'xin chào', 'test', 'alo', 'hey', 'xin', 'chào bạn'}

def is_greeting(text: str) -> bool:
    text_lower = text.lower().strip()
    return any(g in text_lower for g in GREETINGS)

class ChatRequest(BaseModel):
    question: str
    session_id: str = ""

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list
    model: str = "mistral:latest"

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "0.4",
        "features": "Mistral synthesis + BM25 search",
        "cost": "$0.00",
        "documents": len(search.docs)
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    sid = req.session_id or str(uuid.uuid4())

    # Greeting detection
    if is_greeting(req.question):
        return ChatResponse(
            session_id=sid,
            answer="👋 Xin chào! Tôi là Rovo - AI Assistant của Anfin. Bạn hỏi tôi gì?",
            sources=[],
            model="greeting"
        )

    # Search
    docs = search.search(req.question, top_k=10)

    if not docs:
        return ChatResponse(
            session_id=sid,
            answer="Xin lỗi, kiến thức này chưa được cập nhật. Thử hỏi về: Microservices, Go Routine, API Design, Testing, DevOps, Security.",
            sources=[],
            model="fallback"
        )

    # Synthesize (with fallback if Ollama fails)
    try:
        result = get_synthesis_response(req.question, docs)
        # Check if answer contains error string
        if "❌" in result["answer"] or "Lỗi" in result["answer"] or "Connection refused" in result["answer"]:
            result = get_fallback_response(req.question, docs)
    except Exception as e:
        # Ollama failed, use fallback
        result = get_fallback_response(req.question, docs)

    return ChatResponse(
        session_id=sid,
        answer=result["answer"],
        sources=result["sources"],
        model=result.get("model", "fallback")
    )

@app.get("/", response_class=HTMLResponse)
async def root():
    doc_count = len(search.docs)
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>🤖 Anfin Knowledge - Rovo Chat</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
        .container {{ background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 900px; width: 100%; padding: 40px; }}
        h1 {{ color: #667eea; margin-bottom: 10px; font-size: 32px; }}
        .subtitle {{ color: #666; margin-bottom: 30px; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px; }}
        .info-box {{ background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .chat-section {{ margin-top: 30px; }}
        .chat-box {{ background: #f8f9fa; border: 2px solid #e0e0e0; border-radius: 8px; padding: 20px; }}
        .messages {{ height: 300px; overflow-y: auto; margin-bottom: 15px; background: white; border-radius: 6px; padding: 15px; border: 1px solid #e0e0e0; }}
        .message {{ margin-bottom: 12px; padding: 10px; border-radius: 6px; word-wrap: break-word; }}
        .message.user {{ background: #667eea; color: white; margin-left: 20px; text-align: right; }}
        .message.bot {{ background: #e8eaf6; color: #333; margin-right: 20px; }}
        .input-group {{ display: flex; gap: 10px; }}
        input {{ flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }}
        button {{ background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: 600; }}
        button:hover {{ background: #5568d3; }}
        .loading {{ display: none; color: #667eea; text-align: center; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Anfin Knowledge</h1>
        <p class="subtitle">Mistral 7B + {doc_count} Confluence pages = Rovo-level chat</p>

        <div class="info-grid">
            <div class="info-box">✅ LLM: Mistral 7B</div>
            <div class="info-box">✅ Search: BM25</div>
            <div class="info-box">✅ Data: {doc_count} pages</div>
            <div class="info-box">✅ Cost: $0</div>
        </div>

        <div class="chat-section">
            <div class="chat-box">
                <div class="messages" id="messages"></div>
                <div class="loading" id="loading">⏳ Generating...</div>
                <div class="input-group">
                    <input type="text" id="question" placeholder="Hỏi: Microservices? Go? API? Testing?" />
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById("messages");
        const questionInput = document.getElementById("question");
        const loadingDiv = document.getElementById("loading");
        let sessionId = "";

        async function sendMessage() {{
            const question = questionInput.value.trim();
            if (!question) return;

            const userMsg = document.createElement("div");
            userMsg.className = "message user";
            userMsg.textContent = question;
            messagesDiv.appendChild(userMsg);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            questionInput.value = "";
            questionInput.disabled = true;
            loadingDiv.style.display = "block";

            try {{
                const response = await fetch("/chat", {{
                    method: "POST",
                    headers: {{"Content-Type": "application/json"}},
                    body: JSON.stringify({{question, session_id: sessionId}})
                }});

                const data = await response.json();
                sessionId = data.session_id;

                const botMsg = document.createElement("div");
                botMsg.className = "message bot";
                botMsg.innerHTML = data.answer.replace(/\\n/g, "<br>");
                messagesDiv.appendChild(botMsg);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }} catch (error) {{
                const errorMsg = document.createElement("div");
                errorMsg.className = "message bot";
                errorMsg.textContent = "❌ Error: " + error.message;
                messagesDiv.appendChild(errorMsg);
            }} finally {{
                loadingDiv.style.display = "none";
                questionInput.disabled = false;
                questionInput.focus();
            }}
        }}

        questionInput.addEventListener("keypress", (e) => {{
            if (e.key === "Enter") sendMessage();
        }});

        const welcomeMsg = document.createElement("div");
        welcomeMsg.className = "message bot";
        welcomeMsg.textContent = "👋 Xin chào! Tôi là Rovo - hỏi tôi gì về Anfin knowledge base ({doc_count} pages)?";
        messagesDiv.appendChild(welcomeMsg);
    </script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("🚀 Phase 4 Lite: Mistral + BM25 (no Elasticsearch)")
    uvicorn.run(app, host="0.0.0.0", port=port)
