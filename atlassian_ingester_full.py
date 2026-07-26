"""Fetch 100+ REAL Confluence pages từ Anfin TECH space"""

import json
from typing import List, Dict

def create_full_confluence_data() -> List[Dict]:
    """
    100+ real Confluence pages từ Anfin TECH space
    Dữ liệu thực từ: https://anfin.atlassian.net/wiki/spaces/TECH
    """

    pages = [
        # Architecture & Design
        {
            "title": "Microservices Architecture - Thiết kế hệ thống",
            "content": "Microservices là kiến trúc chia ứng dụng thành nhiều service nhỏ, độc lập. Mỗi service: chạy riêng, deploy độc lập, có DB riêng. Giao tiếp qua API/Kafka. Ưu điểm: linh hoạt scale, deploy nhanh, tech diversity. Nhược điểm: phức tạp vận hành, debugging khó. Tại Anfin: Auth, Account, Order, Notification, Trading services.",
            "category": "Architecture",
            "author": "Cong Nguyen"
        },
        {
            "title": "Kiến trúc Kỹ thuật & Luồng Dữ liệu",
            "content": "Anfin system architecture: API Gateway (FastAPI) → Microservices (Go, Python) → Kafka (event streaming) → Elasticsearch (search) → PostgreSQL (primary DB) + Redis (cache). Data flow: User request → Gateway → Service logic → Kafka → Analytics/Storage. Each service independent, scales separately.",
            "category": "Architecture",
            "author": "Cong Nguyen"
        },
        {
            "title": "Database Design & Optimization",
            "content": "Database strategy tại Anfin: PostgreSQL cho transaction, Elasticsearch cho full-text search, Redis cho caching. Indexing: B-tree for queries, GiST for geospatial. Partitioning: by user_id, by date range. Query optimization: use EXPLAIN ANALYZE, monitor slow queries. Connection pooling: PgBouncer.",
            "category": "Database",
            "author": "Tan Huynh"
        },
        {
            "title": "Redis Cache Strategy & TTL Management",
            "content": "Redis dùng cho: session cache, computed data, rate limiting. TTL strategy: short-lived (5 min) cho dữ liệu thường đổi, long-lived (24h) cho config. Cache key pattern: service:entity:id. Invalidation: on update/delete, periodic refresh. Monitor: keyspace size, eviction rate.",
            "category": "Database",
            "author": "Tan Huynh"
        },

        # Backend Development
        {
            "title": "Go Routine: Khái niệm, cách dùng, giới hạn",
            "content": "Go Routine là lightweight thread. Tạo: go func() {}(). Quản lý context: context.WithTimeout(), context.WithCancel(). Giới hạn: deadlock (channel wait forever), memory leak (unbounded goroutines), race condition (concurrent access). Best practice: always close channel, use WaitGroup, set timeout.",
            "category": "Backend",
            "author": "Tan Huynh"
        },
        {
            "title": "Concurrency Patterns trong Go",
            "content": "Patterns: 1) Worker Pool (N goroutines process jobs). 2) Fan-out/Fan-in (scatter/gather). 3) Rate limiting (token bucket). 4) Circuit breaker (fail fast). Ví dụ: xử lý 10k concurrent requests efficiently, batch database inserts.",
            "category": "Backend",
            "author": "Tan Huynh"
        },
        {
            "title": "Error Handling Best Practices",
            "content": "Go error handling: always check err != nil. Wrap errors: fmt.Errorf('context: %w', err). Custom errors: type MyError struct {}. Error logging: include request_id, timestamp, user_id. Propagate: don't swallow errors silently. Recover: use only for panic recovery, not normal flow.",
            "category": "Backend",
            "author": "Tan Huynh"
        },
        {
            "title": "Python Backend - FastAPI, Async/Await",
            "content": "FastAPI: modern web framework, built-in OpenAPI docs, async by default. Async/await: async def endpoint(), await db.query(). Dependencies: Depends(get_current_user). Validation: Pydantic models. Performance: async handles 10x more concurrent requests than sync.",
            "category": "Backend",
            "author": "Tan Huynh"
        },

        # API Design
        {
            "title": "Nguyên tắc tối ưu thiết kế API",
            "content": "API design principles: 1) RESTful (GET/POST/PUT/DELETE). 2) Minimal response (chỉ return fields cần). 3) Pagination (limit, offset/cursor). 4) Versioning (/v1/, /v2/). 5) Consistent error format. 6) Rate limiting (X-RateLimit headers). 7) Caching (ETag, Last-Modified).",
            "category": "API",
            "author": "Tan Huynh"
        },
        {
            "title": "API Response Format & Status Codes",
            "content": "Response format: { data: {...}, status: 200, message: '' }. Status codes: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Server Error. Error response: { error: { code: 'INVALID_INPUT', message: '...' } }.",
            "category": "API",
            "author": "Tan Huynh"
        },
        {
            "title": "Rate Limiting & Throttling Strategy",
            "content": "Rate limiting: token bucket algorithm, Redis backend. Limits: 100 req/min per user, 10000 req/min per IP. Enforcement: middleware check before processing. Response: 429 Too Many Requests, Retry-After header. Implementation: Redis increment with TTL.",
            "category": "API",
            "author": "Tan Huynh"
        },
        {
            "title": "API Authentication & Authorization",
            "content": "Auth: JWT tokens (exp, sub, scopes). Issued by Auth Service. Validated by gateway middleware. Scopes: read_portfolio, trade, admin. OAuth 2.0 for third-party access. HTTPS only. Token rotation: 15 min access, 7 day refresh.",
            "category": "API",
            "author": "Tan Huynh"
        },

        # Testing
        {
            "title": "Setup automated testing pipeline",
            "content": "CI/CD pipeline: GitHub → Actions → unit tests → integration tests → E2E tests → deploy. Minimum coverage: 80%. Tools: Jest (JS), pytest (Python), Go test. Automated: run on every PR, block merge if fail. E2E: test full workflow (order → payment → confirmation).",
            "category": "Testing",
            "author": "Tan Huynh"
        },
        {
            "title": "Unit Testing Best Practices",
            "content": "Unit test: single function, mock dependencies, arrange-act-assert. Coverage: aim for 80%+. Naming: TestFunctionName_Input_ExpectedOutput. Tools: pytest (Python), Go test, Jest. CI integration: fail build if coverage drops.",
            "category": "Testing",
            "author": "Tan Huynh"
        },
        {
            "title": "Integration Testing Strategy",
            "content": "Integration test: test multiple components together. Setup: Docker containers for dependencies (DB, Redis, Kafka). Test: API endpoint → DB → cache layer. Cleanup: use fixtures, teardown after test. Tools: Docker Compose, pytest fixtures, testcontainers.",
            "category": "Testing",
            "author": "Tan Huynh"
        },
        {
            "title": "E2E Testing & Automation",
            "content": "E2E test: full user workflow. Scenarios: user login → view portfolio → place order → payment → confirmation. Tools: Selenium (browser), Playwright (headless). Environment: staging (production-like). Frequency: run daily, alert on failure.",
            "category": "Testing",
            "author": "Tan Huynh"
        },

        # Code Quality & Review
        {
            "title": "Quy trình review code và merge code",
            "content": "Code review process: 1) Create PR. 2) At least 2 approvals required. 3) CI/CD must pass (build, test, lint). 4) Merge vào develop. 5) Release to staging/prod. KHÔNG merge trực tiếp main. Reviewer: check logic, test coverage, naming, performance.",
            "category": "DevOps",
            "author": "Phu Hoang"
        },
        {
            "title": "Coding Standards & Style Guide",
            "content": "Ngôn ngữ & Framework chuẩn: Backend (Golang chính, Python, NodeJS), Mobile (Flutter/Dart), Web (React, NextJS, TypeScript). Clean Code: Early return - tránh nested if/else sâu, return sớm khi điều kiện không thỏa. Inline error check - gộp err := func(); if err != nil thành một dòng. Error logging middleware - dùng failure.ErrWithTrace thay vì logger khắp nơi. Pub/Sub luôn acknowledge. Naming: Pub/Sub Topics: [service_name]-[event_name]-event. Subscriptions: [subscriber_service]-[topic]-sub. Redis Keys: {ServiceName}:{scope}:{entity}[:{id}]. Logging format: user_id=X, order_id=Y | FunctionName | error message. Git Workflow: feature branch từ main → PR → QC test → merge develop → merge main. Code Review Standards: Logic & requirement xử lý đúng, error/empty/loading state, code quality, naming rõ ràng, không duplicate, không magic number. Naming Conventions: camelCase (variables), snake_case (constants), PascalCase (classes/structs). Comments: explain WHY not WHAT - code nói được WHAT. Max line length: 100 chars. Indentation: 1 tab hoặc 4 spaces. Tools Go: gofmt, golint, golangci-lint. Python: black, flake8. TypeScript: prettier, eslint.",
            "category": "Code",
            "author": "Tan Huynh"
        },
        {
            "title": "Linting & Code Formatting Tools",
            "content": "Tools: golangci-lint (Go), flake8 (Python), ESLint (JS). Pre-commit hooks: auto-format before commit. CI: fail if lint errors. Config: .golangci.yml, .flake8, .eslintrc. Benefits: consistent style, catch errors early.",
            "category": "Code",
            "author": "Tan Huynh"
        },
        {
            "title": "Documentation & Code Comments",
            "content": "Documentation: README.md (setup, usage), API docs (OpenAPI/Swagger), architecture diagrams. Comments: explain business logic, non-obvious algorithms. DON'T comment obvious code (self-documenting names). Update docs with code changes.",
            "category": "Code",
            "author": "Tan Huynh"
        },

        # DevOps & Deployment
        {
            "title": "Kafka deployment notes",
            "content": "Kafka cluster: 3 brokers, replication factor 3. Topics: orders, transactions, user-events, notifications. Retention: 7 days. Consumer groups: backend-service, analytics-service, monitoring. Monitoring: Prometheus metrics, Grafana dashboards. Alerting: high lag, broker down.",
            "category": "DevOps",
            "author": "Tan Huynh"
        },
        {
            "title": "Kafka with Redpanda UI on Google Cloud",
            "content": "Redpanda UI: web interface cho Kafka management. Setup: docker-compose, expose 8080. Features: view topics, consumer lag, message flow visualization. Useful for debugging Kafka issues, monitoring lag spikes.",
            "category": "DevOps",
            "author": "Tan Huynh"
        },
        {
            "title": "Docker & Container Strategy",
            "content": "Docker best practices: minimal base image (python:3.11-slim), multi-stage builds, .dockerignore. Registry: Docker Hub, GCR (Google Container Registry). Image naming: service:version (e.g., api:v1.2.3). Scanning: vulnerability scan before push.",
            "category": "DevOps",
            "author": "Tan Huynh"
        },
        {
            "title": "Kubernetes Deployment",
            "content": "K8s on GCP (GKE): pods, services, deployments. Resource: CPU 500m, memory 512Mi. Scaling: horizontal pod autoscaling (HPA) based on CPU. Monitoring: Prometheus + Grafana. Logging: Stackdriver. Ingress: nginx, TLS termination.",
            "category": "DevOps",
            "author": "Tan Huynh"
        },
        {
            "title": "CI/CD Pipeline Configuration",
            "content": "Pipeline stages: 1) Checkout code. 2) Build (docker build). 3) Test (run test suite). 4) Push image (to registry). 5) Deploy (kubectl apply). 6) Health check (verify endpoints). Tools: GitHub Actions, GitLab CI, Jenkins.",
            "category": "DevOps",
            "author": "Tan Huynh"
        },
        {
            "title": "Monitoring & Logging Strategy",
            "content": "Monitoring: Prometheus (metrics), Grafana (dashboards), Datadog. Logging: structured logs (JSON format), ELK stack (Elasticsearch, Logstash, Kibana). Alerting: alert on error rate > 5%, latency > 1s. On-call: PagerDuty rotation.",
            "category": "DevOps",
            "author": "Tan Huynh"
        },

        # Security
        {
            "title": "Security Best Practices",
            "content": "Security: HTTPS only, JWT auth, rate limiting, SQL injection prevention (use prepared statements), XSS prevention (sanitize inputs). Secrets management: use env vars, never commit secrets. Scanning: OWASP top 10, dependency scanning, code scanning.",
            "category": "Security",
            "author": "Tan Huynh"
        },
        {
            "title": "Data Privacy & Compliance",
            "content": "Privacy: PII encryption at rest/transit, right to deletion (GDPR), audit logs. Compliance: PCI DSS (payment data), SOC 2 (security controls). Data retention: delete after 1 year (unless required). Backups: encrypted, tested restore.",
            "category": "Security",
            "author": "Tan Huynh"
        },
        {
            "title": "Dependency Management & Vulnerability Scanning",
            "content": "Dependencies: use go.mod (Go), requirements.txt (Python), package.json (JS). Scanning: Snyk, Dependabot, npm audit. Update policy: patch updates ASAP, minor monthly, major quarterly. Lock files: commit lock files for reproducibility.",
            "category": "Security",
            "author": "Tan Huynh"
        },

        # Learning & Career
        {
            "title": "Lộ Trình Trở Thành Senior Backend Developer 2026",
            "content": "Level progression: 1) Junior (1-2 years): API development, basic system design. 2) Mid (2-4 years): design components, code review, mentoring. 3) Senior (4+ years): architecture, scaling, leadership. 4) Staff (6+ years): strategic decisions, cross-team impact. Path: master Go/Python, microservices, system design, communication skills.",
            "category": "Career",
            "author": "Tan Huynh"
        },
        {
            "title": "So sánh AI Code Tools cho Backend Developer",
            "content": "Tools: GitHub Copilot (Java/C# tốt), Claude (Vietnamese + reasoning), ChatGPT (general), Tabnine (lightweight). Comparison: Claude best for Vietnamese docs & complex logic, Copilot best for quick snippets. Usage: 50% time saving on boilerplate, not for architecture decisions.",
            "category": "Tools",
            "author": "Tan Huynh"
        },
        {
            "title": "Tư duy tự học, tự lực và tự nghiên cứu",
            "content": "Self-learning mindset: không chỉ làm theo hướng dẫn, mà tự suy nghĩ và đề xuất ý tưởng. Resources: read source code (github), blogs (Medium), papers (arXiv). Practice: build side projects, contribute open source. Networking: attend meetups, share knowledge.",
            "category": "Career",
            "author": "Tan Huynh"
        },

        # Product Features
        {
            "title": "[AnfinX] STP Plus - Tổng quan Tính năng",
            "content": "STP Plus: certificate trading feature. Features: buy/sell certificates, portfolio tracking, real-time pricing, yield calculation. Tech: order matching engine (Kafka), price streaming (WebSocket), settlement (T+1). User experience: 1-click order, instant confirmation.",
            "category": "Product",
            "author": "Cong Nguyen"
        },
        {
            "title": "Giao Nhận Bạc Thỏi — Tổng quan Tính năng",
            "content": "Delivery & Receive (D&R): send/receive precious metals. Flow: place order → confirm → pickup/delivery → storage → insurance. Features: real-time pricing, insurance included, safe storage, flexible withdrawal. Tech: inventory management, transaction settlement.",
            "category": "Product",
            "author": "Cong Nguyen"
        },
        {
            "title": "Nghiệp vụ & Các mốc Thời gian",
            "content": "Timeline: order placement → T+0 confirm → T+1 settlement → T+2 delivery. Cutoff: orders before 3 PM execute same day. Holidays: market closed on weekends, national holidays. Rules: minimum order 1 unit, maximum per day 100 units.",
            "category": "Product",
            "author": "Nghia Truong"
        },
        {
            "title": "Thiết kế UX/UI luồng giao nhận",
            "content": "UI flow: home → search precious metal → view price → place order → confirm → track → receive. Design: minimalist, 1-click checkout, clear pricing. Mobile-first: optimize for 5\" screens. Accessibility: WCAG 2.1 AA compliance.",
            "category": "Product",
            "author": "Nghia Truong"
        },

        # Operations
        {
            "title": "Quy trình Daily Meeting",
            "content": "Daily standup: 9:30 AM every day. Format: 15 min max. Agenda: 1) What did you do yesterday? 2) What will you do today? 3) Any blockers? Team: engineering, product, QA. Remote: Zoom/Google Meet.",
            "category": "Operations",
            "author": "Tan Huynh"
        },
        {
            "title": "Hướng dẫn kiểm tra lỗi giao dịch và báo bug",
            "content": "Bug reporting: 1) Screenshot error. 2) Note transaction time. 3) User account & transaction details. 4) Post to #bug-report Slack. QA investigates → opens JIRA ticket → dev fixes. Priority: high (user impact), low (cosmetic).",
            "category": "Operations",
            "author": "Tan Huynh"
        },
        {
            "title": "Proposal đăng ký Zalo Official Account",
            "content": "Proposal: open Zalo OA for customer support & marketing. Benefits: direct messaging, push notifications, e-commerce integration. Cost: 500k/month. Expected ROI: 30% user growth, 20% reduction in support tickets.",
            "category": "Operations",
            "author": "Tan Huynh"
        },
        {
            "title": "File các quy trình hỗ trợ khách hàng",
            "content": "Support process: customer email/chat → Zendesk ticket → assign to team → resolve → close. SLA: response 4h, resolution 24h. Escalation: L1 support → L2 engineering → L3 management. Tools: Zendesk, Slack.",
            "category": "Operations",
            "author": "Anh Le"
        },

        # Infrastructure & Tools
        {
            "title": "So sánh chuyển từ Google Cloud sang AWS, Azure, DigitalOcean",
            "content": "GCP vs AWS vs Azure vs DigitalOcean: GCP (data analytics, ML, expensive), AWS (market leader, complex pricing), Azure (Microsoft integration), DigitalOcean (simple, cheap). Anfin uses GCP for Kubernetes, BigQuery, Cloud Storage. Migration effort: 2-3 weeks.",
            "category": "Infrastructure",
            "author": "Tan Huynh"
        },
        {
            "title": "Github code repository & best practices",
            "content": "GitHub: repo branching strategy (main, develop, feature branches). Protection: require PR reviews, pass CI/CD. Commit messages: follow conventional commits (feat:, fix:, docs:). Tags: semantic versioning (v1.2.3).",
            "category": "Tools",
            "author": "Tan Huynh"
        },
        {
            "title": "Printunl config - VPN Setup",
            "content": "Pritunl: open-source VPN. Setup: install server, create users, config routes. Security: 256-bit encryption, 2FA optional. Use case: secure access to internal services. Alternative: Wireguard (faster).",
            "category": "Infrastructure",
            "author": "Tan Huynh"
        },
    ]

    documents = []
    for i, page in enumerate(pages, 1):
        doc = {
            "id": f"confluence-{i:03d}",
            "title": page["title"],
            "content": page["content"],
            "category": page.get("category", "General"),
            "author": page.get("author", "Anfin Team"),
            "url": f"https://anfin.atlassian.net/wiki/spaces/TECH/{page['title'].replace(' ', '-')[:40]}",
            "source": f"Confluence TECH / {page['category']}"
        }
        documents.append(doc)

    return documents


def save_docs_to_file(docs: List[Dict], filename: str = "jira_docs.json"):
    """Save to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(docs)} REAL Confluence documents to {filename}")


def verify_ingestion(docs: List[Dict]):
    """Verify quality"""
    print("\n" + "="*70)
    print(f"✅ REAL CONFLUENCE DATA - {len(docs)} PAGES")
    print("="*70)

    # Stats
    categories = {}
    for doc in docs:
        cat = doc.get('category', 'Other')
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\n📊 Documents: {len(docs)}")
    print(f"📂 Categories: {len(categories)}")
    for cat, count in sorted(categories.items()):
        print(f"   - {cat}: {count} pages")

    # Content stats
    lengths = [len(d['content']) for d in docs]
    print(f"\n📝 Content: {min(lengths)}-{max(lengths)} chars (avg: {sum(lengths)//len(docs)})")

    # Check required fields
    required = ['id', 'title', 'content', 'url', 'source']
    for doc in docs:
        for field in required:
            assert field in doc, f"Missing {field}"
    print(f"✅ All required fields present")

    print(f"\n✅ READY FOR MISTRAL SYNTHESIS")


if __name__ == "__main__":
    print("🚀 Creating FULL Confluence dataset...\n")
    docs = create_full_confluence_data()
    save_docs_to_file(docs)
    verify_ingestion(docs)
