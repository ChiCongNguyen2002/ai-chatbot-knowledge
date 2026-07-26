"""Fallback synthesis - Format search results as structured answer (NO Ollama needed!)"""

from typing import List, Dict

def synthesize_from_search(question: str, docs: List[Dict]) -> str:
    """
    Format search results into structured Vietnamese answer.
    Works without Ollama - just smart formatting!
    """

    if not docs:
        return "Xin lỗi, kiến thức này chưa được cập nhật trong hệ thống Anfin."

    # Get best doc
    best_doc = docs[0]
    title = best_doc['title']
    content = best_doc['content']

    # Smart formatting based on doc type
    if 'microservice' in content.lower():
        return f"""{content}

Đặc điểm chính:
• Độc lập: Mỗi service chạy trong tiến trình riêng
• Giao tiếp qua API: REST API, gRPC, message queue (Kafka)
• Cơ sở dữ liệu riêng: Tránh phụ thuộc lẫn nhau
• Công nghệ linh hoạt: Mỗi service dùng ngôn ngữ khác nhau

So sánh với Monolith:
| Khía cạnh | Monolith | Microservices |
|-----------|----------|---------------|
| Cấu trúc | Một khối duy nhất | Nhiều service nhỏ |
| Deploy | Deploy toàn bộ | Deploy từng service |
| Scale | Scale cả hệ thống | Scale từng phần |
| Độ phức tạp | Đơn giản hơn ban đầu | Phức tạp hơn về vận hành |

Ví dụ thực tế tại Anfin:
- Auth Service (xác thực người dùng)
- Account Service (quản lý tài khoản đầu tư)
- Order Service (xử lý lệnh mua/bán)
- Notification Service (gửi thông báo)

Khi nào nên dùng?
✅ Hệ thống lớn, nhiều team phát triển song song
✅ Cần scale từng phần riêng lẻ
✅ Yêu cầu high availability
❌ Dự án nhỏ, team ít người → Monolith đơn giản hơn"""

    elif 'go routine' in content.lower():
        return f"""{content}

Cách sử dụng:
1. Khởi động goroutine: go myFunction()
2. Quản lý lifecycle với context: context.WithTimeout()
3. Đồng bộ hóa với WaitGroup: sync.WaitGroup

Giới hạn và Gotchas:
⚠️ Memory leak nếu không close channel
⚠️ Deadlock nếu goroutine wait vô thời hạn
⚠️ Race condition với concurrent map access

Best practice:
• Luôn set timeout
• Đóng channel đúng cách
• Dùng sync.Mutex cho concurrent access
• Giới hạn số goroutines (max ~1 triệu)

Ví dụ thực tế:
- Xử lý 1000s concurrent requests
- Batch processing
- Worker pool pattern
- Real-time data streaming"""

    elif 'api' in content.lower() or 'design' in content.lower():
        return f"""{content}

6 Nguyên tắc Thiết Kế API:
1. Minimal Response - Chỉ return fields cần thiết
2. Pagination - limit, offset hoặc cursor cho large datasets
3. Versioning - /v1/, /v2/ (backward compatibility)
4. Rate Limiting - X-RateLimit headers, 429 status code
5. Error Handling - Consistent error format
6. Caching - ETag, Last-Modified, Cache-Control header

Status Codes Chính:
• 200 OK - Thành công
• 201 Created - Tạo resource mới
• 204 No Content - Thành công, không có body
• 400 Bad Request - Client error (invalid input)
• 401 Unauthorized - Cần authentication
• 403 Forbidden - Không có quyền
• 404 Not Found - Resource không tồn tại
• 429 Too Many Requests - Rate limit exceeded
• 500 Server Error - Lỗi server

Response Format:
{{
  "data": [...],
  "pagination": {{
    "total": 150,
    "limit": 10,
    "offset": 0,
    "hasMore": true
  }}
}}

Áp dụng tại Anfin: Tất cả microservices tuân theo practices này"""

    elif 'kafka' in content.lower():
        return f"""{content}

Setup Kafka Cluster:
- 3 brokers
- Replication factor: 3
- Topics: orders, transactions, user-events, notifications
- Retention: 7 days

Consumer Groups:
• backend-service (xử lý business logic)
• analytics-service (collect metrics)
• monitoring-service (real-time alerts)

Monitoring & Alerting:
⚠️ High consumer lag (>1000 messages)
⚠️ Broker down
⚠️ Replication lag
⚠️ Topic space usage >80%

Tools:
- Prometheus metrics
- Grafana dashboards
- Redpanda UI (web console)"""

    else:
        # Generic structured answer
        return f"""{title}

{content}

Thông tin bổ sung:
- Nguồn: Tài liệu nội bộ Anfin
- Cập nhật gần nhất: {best_doc.get('updated', 'N/A')}
- Danh mục: {best_doc.get('category', 'General')}"""


def get_fallback_response(question: str, docs: List[Dict]) -> Dict:
    """Fallback synthesis without Ollama"""
    answer = synthesize_from_search(question, docs)
    sources = [
        {
            "title": d['title'],
            "category": d.get('category', 'General'),
            "score": d['score'],
            "url": d.get('url', '#')
        }
        for d in docs[:3]
    ]
    return {
        "answer": answer,
        "sources": sources,
        "type": "fallback_structured",
        "note": "Powered by smart formatting (no AI synthesis needed)"
    }
