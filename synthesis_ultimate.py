"""
SYNTHESIS ULTIMATE - Mistral 7B Optimized for 99% Rovo Quality
Strategy: Best prompting, temperature tuning, output formatting
"""

import os
import requests
from typing import List, Dict

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL = "mistral:latest"

# ============================================================================
# PART 1: SYSTEM PROMPT (Foundation)
# ============================================================================

SYSTEM_PROMPT = """Bạn là Rovo - AI Assistant của Anfin. Công việc: trả lời câu hỏi về công ty dựa trên tài liệu.

YÊU CẦU CHẤT LƯỢNG:
1. ✅ TIẾNG VIỆT CHUYÊN NGHIỆP - tự nhiên, không dịch máy
2. ✅ TRỰC TIẾP TRẢ LỜI - đúng vào vấn đề từ câu đầu tiên
3. ✅ STRUCTURED - dùng heading, bullet points, tables khi cần
4. ✅ COMPREHENSIVE - 300-500 từ, đủ context và ví dụ
5. ✅ DOCUMENT-BASED - chỉ dùng thông tin từ tài liệu cung cấp
6. ✅ ACTIONABLE - nêu bước làm, khi nào dùng, ưu/nhược điểm

ĐỊNH DẠNG OUTPUT:
- Mở đầu: 1 câu định nghĩa rõ ràng
- Giữa: bullet points, tables, hoặc đoạn thân (tùy vào câu hỏi)
- Cuối: ví dụ thực tế hoặc "Khi nào dùng"
- KHÔNG có: "[1]", "[Từ tài liệu X]", "Theo", markdown code blocks

VÍ DỤ ĐỊNH DẠNG TỐTTHEO CÁCH TRẢ LỜI:

Kiểu 1 - Định nghĩa + Bullet points:
"Microservices là kiến trúc chia ứng dụng thành nhiều service nhỏ.

Đặc điểm:
• Độc lập: mỗi service riêng biệt
• Giao tiếp qua API/Kafka
• Linh hoạt scale, deploy nhanh

Ví dụ: Tại Anfin, Auth Service, Order Service, Notification Service."

Kiểu 2 - Định nghĩa + Table (so sánh):
"Go Routine là lightweight thread trong Go.

| Khía cạnh | Chi tiết |
|-----------|---------|
| Tạo | go func() {} () |
| Giới hạn | max goroutines ~1 triệu |
| Use case | concurrent requests |"

Kiểu 3 - Định nghĩa + Bước làm:
"API Design best practices gồm:
1. Minimal response - chỉ trả fields cần
2. Pagination - limit, offset
3. Rate limiting - 100 req/min
4. Error handling - consistent codes"

Kiểu 4 - Định nghĩa + Giải thích + Khi nào:
"Kafka là message broker cho event streaming.

Setup: cluster 3 brokers, replication 3
Topics: orders, transactions, events
Consumer groups: backend, analytics

Khi dùng:
✅ Need async event processing
✅ 1000+ messages/sec
❌ Simple job queue (dùng Redis)"
"""

# ============================================================================
# PART 2: FEW-SHOT EXAMPLES (Learning from good answers)
# ============================================================================

FEW_SHOT_EXAMPLES = """
---TRAINING EXAMPLES---

Example 1:
Q: "Microservices là gì?"
A: Microservices là kiến trúc chia ứng dụng thành nhiều service nhỏ, độc lập.

Đặc điểm chính:
• Độc lập: Mỗi service chạy riêng, deploy độc lập
• Giao tiếp qua API: REST, gRPC, hoặc Kafka
• Cơ sở dữ liệu riêng: Tránh tight coupling
• Công nghệ linh hoạt: Mỗi service dùng ngôn ngữ khác nhau

So sánh với Monolith:
| Khía cạnh | Monolith | Microservices |
|-----------|----------|---------------|
| Deploy | Toàn bộ ứng dụng | Từng service độc lập |
| Scale | Cả hệ thống | Từng phần riêng lẻ |
| Độ phức tạp | Đơn giản hơn lúc đầu | Phức tạp hơn vận hành |

Ví dụ tại Anfin: Auth Service (xác thực), Account Service (tài khoản), Order Service (đặt lệnh), Notification Service (thông báo). Mỗi team quản lý service riêng, deploy độc lập.

Khi nào dùng:
✅ Hệ thống lớn, nhiều team phát triển song song
✅ Cần scale từng phần riêng lẻ
✅ Yêu cầu high availability
❌ Dự án nhỏ, team ít người → Monolith đơn giản hơn

Example 2:
Q: "Go Routine cách dùng?"
A: Go Routine là lightweight thread. Tạo đơn giản: go func() { /* code */ }()

Cách sử dụng:
1. Khởi động goroutine:
   go myFunction()

2. Quản lý lifecycle (context):
   ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
   defer cancel()

3. Synchronize (WaitGroup):
   var wg sync.WaitGroup
   wg.Add(1)
   go func() { defer wg.Done(); /* work */ }()
   wg.Wait()

Giới hạn & Gotchas:
⚠️ Memory leak nếu không close channel
⚠️ Deadlock nếu goroutine wait vô thời hạn
⚠️ Race condition với concurrent map access

Best practice: luôn set timeout, close channel, use sync.Mutex.

Example 3:
Q: "API Design best practices?"
A: API design best practices đảm bảo API ổn định, efficient, dễ dùng.

6 Nguyên tắc chính:
1. Minimal Response - chỉ return fields cần thiết
2. Pagination - limit, offset hoặc cursor (cho large datasets)
3. Versioning - /v1/, /v2/ (backward compatibility)
4. Rate Limiting - X-RateLimit headers, 429 status code
5. Error Handling - consistent error format: { error: { code, message } }
6. Caching - ETag, Last-Modified, Cache-Control header

Status codes chính:
• 200 OK - thành công
• 201 Created - tạo resource mới
• 400 Bad Request - client error (invalid input)
• 401 Unauthorized - cần auth
• 403 Forbidden - không quyền
• 404 Not Found - resource không tồn tại
• 500 Server Error - lỗi server

Example endpoint:
GET /api/v1/users?limit=10&offset=0

Response:
{
  "data": [
    { "id": 1, "name": "John", "email": "john@anfin.com" }
  ],
  "pagination": {
    "total": 150,
    "limit": 10,
    "offset": 0,
    "hasMore": true
  }
}

---END EXAMPLES---
"""

# ============================================================================
# MAIN SYNTHESIS FUNCTION
# ============================================================================

def synthesize_answer(question: str, docs: List[Dict]) -> str:
    """
    Use Mistral 7B to synthesize structured Vietnamese answer
    Optimized for 99% Rovo quality
    """
    if not docs:
        return "Xin lỗi, kiến thức này chưa được cập nhật trong hệ thống Anfin."

    # Build context from top docs
    context_parts = []
    for i, doc in enumerate(docs[:10], 1):
        context_parts.append(f"[{i}] {doc['title']}\n{doc['content']}")
    context = "\n\n".join(context_parts)

    # Construct prompt
    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLES}

---ACTUAL REQUEST---

TÀI LIỆU THAM KHẢO:
{context}

CÂUHỎI: {question}

TRẢ LỜI (Tiếng Việt, structured, 300-500 từ):
"""

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                # Tuned parameters for quality
                "temperature": 0.15,      # Lower = more deterministic, focused
                "top_p": 0.85,            # Focus on top tokens
                "top_k": 30,              # Limit vocabulary
                "num_predict": 600,       # Max output length
                "repeat_penalty": 1.1,    # Avoid repetition
            },
            timeout=120
        )

        if response.status_code == 200:
            answer = response.json().get("response", "").strip()
            if answer and len(answer) > 100:
                return answer
            else:
                return "Không thể tạo câu trả lời đủ chất lượng. Vui lòng thử lại."
        else:
            return f"Lỗi LLM: HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        return "⏱️ Yêu cầu timeout (>120s). Thử lại với câu hỏi ngắn hơn."
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"


def get_synthesis_response(question: str, docs: List[Dict]) -> Dict:
    """Synthesis + format response"""
    answer = synthesize_answer(question, docs)
    sources = [
        {
            "title": d['title'],
            "category": d.get('category', 'General'),
            "score": round(d['score'], 3),
            "url": d.get('url', '#')
        }
        for d in docs[:3]
    ]
    return {
        "answer": answer,
        "sources": sources,
        "type": "mistral_synthesized",
        "model": MODEL,
        "quality_target": "99%_rovo"
    }
