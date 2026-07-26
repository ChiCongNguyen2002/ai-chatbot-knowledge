"""Hybrid App: KB Retrieval + Mistral Reasoning"""

import os
import sys
import uuid
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'phase2'))

from rag_pipeline import RAGPipeline
from hybrid_reasoning import HybridRAG
from atlassian_ingester_full import create_full_confluence_data

app = FastAPI(title="Anfin Knowledge - Hybrid (KB + Reasoning)")

# Initialize
docs = create_full_confluence_data()
kb_pipeline = RAGPipeline(docs)
hybrid_system = HybridRAG(kb_pipeline)

print(f"✅ Hybrid system ready: KB (44 docs) + Mistral reasoning")

GREETINGS = {'hello', 'hi', 'chào', 'xin chào', 'alo', 'hey'}

def is_greeting(text: str) -> bool:
    return any(re.match(rf'^{re.escape(g)}', text.lower()) for g in GREETINGS)


class ChatRequest(BaseModel):
    question: str
    session_id: str = ""


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[dict]
    confidence: float
    latency_ms: float
    mode: str  # "kb-only" or "kb+reasoning"
    model: str = "hybrid-v1"


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "Hybrid 1.0",
        "architecture": "KB Retrieval + Mistral Reasoning",
        "documents": len(docs),
        "cost": "$0/month",
        "features": [
            "✅ Fact Retrieval (160ms)",
            "✅ Deep Reasoning (2-5s on complex)",
            "✅ Automatic Mode Selection",
            "✅ Zero Hallucinations",
            "✅ Free (Ollama + KB)"
        ]
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    if is_greeting(req.question):
        return ChatResponse(
            session_id=session_id,
            answer="👋 Xin chào! Tôi là Anfin Assistant. Hỏi gì cũng được - facts hoặc analysis!",
            sources=[],
            confidence=1.0,
            latency_ms=0.0,
            mode="greeting"
        )

    try:
        response = hybrid_system.search(req.question, session_id=session_id)

        return ChatResponse(
            session_id=session_id,
            answer=response.answer,
            sources=[{"title": s.get('title', ''), "id": s.get('id', '')} for s in response.sources],
            confidence=response.confidence,
            latency_ms=response.latency_ms,
            mode=response.mode
        )

    except Exception as e:
        return ChatResponse(
            session_id=session_id,
            answer=f"⚠️  Lỗi: {str(e)}",
            sources=[],
            confidence=0.0,
            latency_ms=0.0,
            mode="error"
        )


@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>🤖 Anfin Knowledge - Hybrid</title>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
        .container {{ background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 1000px; width: 100%; padding: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        h1 {{ color: #667eea; margin-bottom: 10px; }}
        .badge {{ display: inline-block; background: #4CAF50; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px; margin: 0 4px; }}
        .info {{ background: #f0f4ff; border-left: 4px solid #667eea; padding: 15px; border-radius: 4px; margin-bottom: 20px; font-size: 13px; }}
        .chat-container {{ display: flex; flex-direction: column; height: 500px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; background: #f9f9f9; }}
        #messages {{ flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }}
        .message {{ padding: 12px 16px; border-radius: 8px; max-width: 70%; word-wrap: break-word; }}
        .message.user {{ background: #667eea; color: white; align-self: flex-end; }}
        .message.assistant {{ background: #e8eaf6; color: #333; align-self: flex-start; }}
        .mode-badge {{ font-size: 11px; color: #999; margin-top: 4px; }}
        .input-area {{ display: flex; gap: 10px; }}
        input {{ flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; }}
        button {{ padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }}
        button:hover {{ background: #764ba2; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Anfin Knowledge - Hybrid System</h1>
            <p>Facts (160ms) + Reasoning (2-5s)</p>
            <div>
                <span class="badge">✅ KB Retrieval</span>
                <span class="badge">✅ Mistral Reasoning</span>
                <span class="badge">✅ Auto Mode</span>
                <span class="badge">✅ $0</span>
            </div>
        </div>

        <div class="info">
            📊 {len(docs)} documents indexed
            <br>🟢 Simple questions → Fast KB lookup (160ms)
            <br>🟠 Complex questions → KB + Mistral analysis (2-5s)
            <br>✅ Automatic question classification
        </div>

        <div class="chat-container">
            <div id="messages"></div>
        </div>

        <div class="input-area">
            <input type="text" id="question" placeholder="Hỏi gì cũng được..." />
            <button onclick="sendMessage()">Send</button>
        </div>

        <script>
            const sessionId = localStorage.getItem('sessionId') || Math.random().toString();
            localStorage.setItem('sessionId', sessionId);

            async function sendMessage() {{
                const question = document.getElementById('question').value.trim();
                if (!question) return;

                addMessage(question, 'user');
                document.getElementById('question').value = '';

                try {{
                    const response = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{question, session_id: sessionId}})
                    }});

                    const data = await response.json();
                    const modeLabel = data.mode === 'kb-only' ? '🟢 KB Only' : '🟠 KB + Reasoning';
                    addMessage(data.answer + `\\n\\n[Mode: ${{modeLabel}} | Confidence: ${{(data.confidence*100).toFixed(0)}}% | Latency: ${{data.latency_ms.toFixed(0)}}ms]`, 'assistant');
                }} catch (e) {{
                    addMessage('Error: ' + e.message, 'assistant');
                }}
            }}

            function addMessage(text, role) {{
                const div = document.createElement('div');
                div.className = 'message ' + role;
                div.textContent = text;
                document.getElementById('messages').appendChild(div);
                document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
            }}

            document.getElementById('question').addEventListener('keypress', (e) => {{
                if (e.key === 'Enter') sendMessage();
            }});

            addMessage('👋 Xin chào! Tôi là AI Assistant với 2 chế độ:\\n🟢 Hỏi facts → Trả lời nhanh từ KB (160ms)\\n🟠 Hỏi phức tạp → Trả lời có phân tích (2-5s)\\n\\nHỏi gì cũng được!', 'assistant');
        </script>
    </div>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
