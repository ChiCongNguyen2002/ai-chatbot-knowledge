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

    prompt = f"""Bạn là trợ lý kiến thức của Anfin. Trả lời bằng tiếng Việt, chuyên nghiệp như Rovo.

TÀI LIỆU THAM KHẢO:
{context}

CÂUẨ HỎI: {question}

HƯỚNG DẪN:
1. Bắt đầu bằng định nghĩa/giải thích rõ ràng
2. Sử dụng heading (Đặc điểm, Ví dụ, So sánh, Khi nào dùng, v.v.)
3. Khi so sánh: dùng bảng hoặc list
4. Khi có ví dụ: nêu cụ thể (Ví dụ tại Anfin, hoặc tình huống thực tế)
5. Chỉ dùng thông tin từ tài liệu
6. Output: 400-600 từ, có cấu trúc (không dùng markdown code)
7. Đừng viết "Theo tài liệu" hay "Theo [1]" - cứ trả lời tự nhiên"""

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
