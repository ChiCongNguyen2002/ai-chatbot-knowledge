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

    prompt = f"""Bạn là trợ lý kiến thức cho công ty Anfin. Trả lời bằng tiếng Việt, ngắn gọn và tự nhiên.

Tài liệu tham khảo:
{context}

Câu hỏi: {question}

Yêu cầu:
1. Trả lời rõ ràng, dùng thông tin từ tài liệu
2. Không thêm thông tin ngoài tài liệu
3. Nếu liên quan nhiều tài liệu, nói rõ từ đâu
4. Giữ dưới 300 từ, không cần "Learn more" hay link"""

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,
                "num_predict": 256
            },
            timeout=90
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
