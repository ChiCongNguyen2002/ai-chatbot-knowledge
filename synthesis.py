"""Phase 3: LLM Synthesis - Qwen 7B generates natural language answers"""

import os, requests
from typing import List, Dict

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL = "qwen:7b-int4"

def synthesize_answer(question: str, docs: List[Dict]) -> str:
    """Use Qwen 7B to synthesize natural answer from retrieved docs"""
    if not docs:
        return "Xin lỗi, kiến thức này chưa được cập nhật."

    context = "\n".join([
        f"[{i+1}] {doc['title']}\n{doc['content']}"
        for i, doc in enumerate(docs[:10])
    ])

    prompt = f"""Bạn là trợ lý kiến thức cho công ty Anfin.
Dựa vào các tài liệu sau:

{context}

Trả lời câu hỏi này bằng tiếng Việt, tự nhiên và có cấu trúc:
{question}

Hãy cung cấp câu trả lời rõ ràng, nêu được thông tin từ các tài liệu.
Nếu liên quan đến nhiều tài liệu, hãy nói rõ mỗi thông tin đến từ tài liệu nào.
Giữ câu trả lời dưới 400 từ."""

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3
            },
            timeout=60
        )

        if response.status_code == 200:
            answer = response.json().get("response", "")
            return answer.strip() if answer.strip() else "Không thể tạo câu trả lời."
        else:
            return f"Lỗi LLM: {response.status_code}"

    except requests.exceptions.Timeout:
        return "Yêu cầu timeout. Vui lòng thử lại."
    except Exception as e:
        return f"Lỗi: {str(e)}"

def get_synthesis_response(question: str, docs: List[Dict]) -> Dict:
    """Retrieve → Synthesize → Format"""
    answer = synthesize_answer(question, docs)
    sources = [{"title": d['title'], "score": round(d['score'], 2), "url": d.get('url', '#')} for d in docs[:3]]
    return {"answer": answer, "sources": sources, "type": "llm_generated"}
