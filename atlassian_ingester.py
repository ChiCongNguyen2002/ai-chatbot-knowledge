"""Phase 2: Ingest Jira issues via Atlassian MCP"""

import json
from typing import List, Dict

# Using Claude's native Atlassian MCP integration
# This fetches from Jira without needing API tokens

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Break text into chunks"""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    current = 0
    while current < len(text):
        chunks.append(text[current:current + chunk_size])
        current += chunk_size
    return chunks


def ingest_jira_issues() -> List[Dict]:
    """
    Ingest Jira issues - Returns list of documents

    NOTE: In production, this would:
    1. Call Atlassian MCP mcp__atlassian__search or mcp__atlassian__searchJiraIssuesUsingJql
    2. Fetch all issues from specified projects
    3. Extract: issue key, summary, description, comments
    4. Chunk by 500 chars
    5. Return formatted docs

    For now, using sample Jira data
    """

    # Sample Jira data (in production, this comes from MCP API)
    sample_issues = [
        {
            "key": "TECH-1001",
            "summary": "Implement microservices communication layer",
            "description": "Design and implement async messaging between microservices using message queue. Services should communicate via Kafka topics.",
            "type": "Feature",
            "project": "TECH"
        },
        {
            "key": "ENG-2001",
            "summary": "Establish coding standards and code review process",
            "description": "Define coding standards for Go and Python. All PRs must pass code review. Use linters for automated checks.",
            "type": "Process",
            "project": "ENG"
        },
        {
            "key": "QA-3001",
            "summary": "Setup automated testing pipeline",
            "description": "Create CI/CD pipeline with automated unit tests, integration tests, and E2E tests. Minimum 80% coverage required.",
            "type": "Infrastructure",
            "project": "QA"
        },
        {
            "key": "INFRA-4001",
            "summary": "Database indexing strategy for performance",
            "description": "Analyze query patterns and create appropriate database indexes. Monitor index usage and performance impact.",
            "type": "Task",
            "project": "INFRA"
        },
        {
            "key": "SEC-5001",
            "summary": "Security vulnerability scanning and remediation",
            "description": "Implement automated security scanning for dependencies. Scan code for OWASP top 10 vulnerabilities.",
            "type": "Security",
            "project": "SEC"
        },
    ]

    documents = []

    for issue in sample_issues:
        # Combine issue info
        full_text = f"{issue['summary']}. {issue['description']}"

        # Chunk if necessary
        chunks = chunk_text(full_text, chunk_size=500)

        # Create documents
        for i, chunk in enumerate(chunks):
            doc = {
                "id": f"jira-{issue['key']}-{i}",
                "key": issue["key"],
                "title": issue["summary"],
                "content": chunk,
                "project": issue["project"],
                "type": issue["type"],
                "url": f"https://anfin.atlassian.net/browse/{issue['key']}",
                "source": f"Jira / {issue['key']}"
            }
            documents.append(doc)

    return documents


def save_docs_to_file(docs: List[Dict], filename: str = "jira_docs.json"):
    """Save ingested docs to file"""
    with open(filename, 'w') as f:
        json.dump(docs, f, indent=2)
    print(f"✅ Saved {len(docs)} documents to {filename}")
    return filename


def verify_ingestion(docs: List[Dict]):
    """Verify ingestion quality"""
    print("\n" + "="*60)
    print("INGESTION VERIFICATION")
    print("="*60)

    print(f"\n✅ Documents ingested: {len(docs)}")

    # Check metadata
    projects = set(d['project'] for d in docs)
    print(f"✅ Projects: {len(projects)} ({', '.join(sorted(projects))})")

    # Check content
    min_len = min(len(d['content']) for d in docs)
    max_len = max(len(d['content']) for d in docs)
    print(f"✅ Content length: {min_len}-{max_len} chars")

    # Check no duplicates
    ids = [d['id'] for d in docs]
    assert len(ids) == len(set(ids)), "❌ Duplicate IDs found!"
    print(f"✅ No duplicates")

    # Check required fields
    required_fields = ['id', 'title', 'content', 'url', 'source']
    for doc in docs:
        for field in required_fields:
            assert field in doc, f"❌ Missing field {field} in {doc['id']}"
    print(f"✅ All required fields present")

    print(f"\n✅ INGESTION PASSED")
    return True


if __name__ == "__main__":
    print("🔄 Ingesting Jira issues...")
    docs = ingest_jira_issues()
    save_docs_to_file(docs)
    verify_ingestion(docs)
