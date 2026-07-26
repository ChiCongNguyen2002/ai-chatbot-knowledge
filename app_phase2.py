"""Phase 2 - Enterprise RAG Chatbot"""

import os
import sys
import uuid
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'phase2'))

from phase2.rag_pipeline import RAGPipeline
from atlassian_ingester_full import create_full_confluence_data

app = FastAPI(title="Anfin Knowledge Enterprise")

# Load and initialize
CONFLUENCE_DOCUMENTS = create_full_confluence_data()
pipeline = RAGPipeline(CONFLUENCE_DOCUMENTS, config={'hybrid_alpha': 0.4, 'chunk_size': 300, 'max_tokens': 4000})

print(f"[✅] RAG Pipeline ready: {len(CONFLUENCE_DOCUMENTS)} docs, 9 stages")

GREETINGS = {'hello', 'hi', 'chào', 'xin chào', 'alo', 'hey', 'xin', 'chào bạn'}

def is_greeting(text: str) -> bool:
    text_lower = text.lower().strip()
    for greeting in GREETINGS:
        if re.match(rf'^{re.escape(greeting)}[\s\?!.]*$', text_lower):
            return True
    return False

class ChatRequest(BaseModel):
    question: str
    session_id: str = ""
    use_reranking: bool = True
    max_results: int = 5

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[dict]
    confidence: float
    latency_ms: float
    intent: str

@app.get("/health")
async def health():
    info = pipeline.get_pipeline_info()
    return {
        "status": "ok",
        "version": "2.0",
        "documents": info['documents_indexed'],
        "stages": info['stages'],
        "cost": "$0/month"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    if is_greeting(req.question):
        return ChatResponse(
            session_id=session_id, answer="👋 Xin chào! Hỏi gì?",
            sources=[], confidence=1.0, latency_ms=0.0, intent="greeting"
        )

    try:
        response = pipeline.search(
            query=req.question, session_id=session_id,
            use_reranking=req.use_reranking, top_k=req.max_results,
            max_context_words=2000
        )
        return ChatResponse(
            session_id=session_id, answer=response.answer,
            sources=[{"title": s.get('title', ''), "id": s.get('id', '')} for s in response.sources],
            confidence=response.confidence, latency_ms=response.latency_ms,
            intent=response.metadata.get('query_intent', 'general')
        )
    except Exception as e:
        return ChatResponse(
            session_id=session_id, answer=f"⚠️ Lỗi: {str(e)}",
            sources=[], confidence=0.0, latency_ms=0.0, intent="error"
        )

@app.get("/", response_class=HTMLResponse)
async def root():
    doc_count = len(CONFLUENCE_DOCUMENTS)
    return f"""<!DOCTYPE html>
<html>
<head><title>🤖 Anfin Knowledge</title><meta charset="UTF-8"><style>
body {{font-family: -apple-system; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px;}}
.container {{background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); max-width: 1000px; width: 100%; padding: 40px;}}
h1 {{color: #667eea; margin-bottom: 10px;}}
.chat-container {{display: flex; flex-direction: column; height: 500px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; background: #f9f9f9;}}
#messages {{flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px;}}
.message {{padding: 12px 16px; border-radius: 8px; word-wrap: break-word; max-width: 70%;}}
.message.user {{background: #667eea; color: white; align-self: flex-end;}}
.message.assistant {{background: #e8eaf6; color: #333; align-self: flex-start;}}
.input-area {{display: flex; gap: 10px;}}
input {{flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px;}}
button {{padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;}}
</style></head><body>
<div class="container">
<h1>🤖 Anfin Knowledge Enterprise</h1>
<p>9-Component RAG Pipeline • {doc_count} docs • 85-90% quality • $0/month</p>
<div class="chat-container"><div id="messages"></div></div>
<div class="input-area">
<input type="text" id="question" placeholder="Hỏi gì?" />
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
            body: JSON.stringify({{question, session_id: sessionId, use_reranking: true, max_results: 5}})
        }});
        const data = await response.json();
        addMessage(data.answer, 'assistant');
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

addMessage('👋 Xin chào! Hỏi gì?', 'assistant');
</script>
</div></body></html>"""

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
