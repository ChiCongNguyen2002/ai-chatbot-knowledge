# 🚀 PHASE 2 IMPLEMENTATION PLAN
## Zero-Cost, High-Quality RAG System

**Goal:** Build 85-90% quality knowledge assistant with $0 cost  
**Timeline:** 8-10 weeks  
**Approach:** Smart retrieval + context engineering (NOT smart models)

---

## 📋 PROJECT STRUCTURE

```
ai-chatbot-knowledge/
├── phase1/                          # Current system (keep as reference)
│   ├── app_simple.py
│   ├── search_simple.py
│   └── synthesis_fallback.py
│
├── phase2/                          # Phase 2 implementation
│   ├── retrieval/
│   │   ├── hybrid_search.py         # FAISS + BM25
│   │   ├── reranker.py              # Cross-encoder
│   │   ├── chunk_manager.py         # Smart chunking
│   │   └── query_rewriter.py        # Intent detection
│   │
│   ├── processing/
│   │   ├── context_compressor.py    # Remove noise
│   │   ├── metadata_filter.py       # Category-based
│   │   ├── citation_handler.py      # Source tracking
│   │   └── knowledge_graph.py       # Entity relationships
│   │
│   ├── memory/
│   │   ├── conversation_memory.py   # Multi-turn context
│   │   └── session_manager.py       # Session tracking
│   │
│   ├── models/
│   │   ├── embedder.py              # Vector embeddings
│   │   ├── reranker_model.py        # Cross-encoder
│   │   └── local_llm.py             # Mistral 7B
│   │
│   ├── app.py                       # Phase 2 FastAPI app
│   ├── pipeline.py                  # Complete RAG pipeline
│   └── config.py                    # Configuration
│
├── data/
│   ├── documents/                   # 43 Confluence documents
│   ├── chunks/                      # Smart chunks cache
│   ├── embeddings/                  # Vector embeddings cache
│   ├── graph/                       # Knowledge graph
│   └── metadata/                    # Document metadata
│
├── tests/
│   ├── test_retrieval.py
│   ├── test_reranking.py
│   ├── test_synthesis.py
│   └── test_pipeline.py
│
└── requirements-phase2.txt
```

---

## 🔄 PHASE 2 ARCHITECTURE

```
User Query
    ↓
┌─────────────────────────────────────┐
│ 1. CONVERSATION MEMORY              │  Week 8-9
│ Extract context from last 3 turns   │
└─────────────────────────────────────┘
    ↓ [current_query + history]
┌─────────────────────────────────────┐
│ 2. QUERY REWRITER (Rule-based)      │  Week 3-4
│ - Intent detection                  │
│ - Keyword expansion                 │
│ - Synonym injection                 │
└─────────────────────────────────────┘
    ↓ [expanded_queries: 3-5 variants]
┌─────────────────────────────────────┐
│ 3. HYBRID SEARCH                    │  Week 1-2
│ - BM25 search (50 docs)             │
│ - Vector search via FAISS (50 docs) │
│ - Combine results (100 candidates)  │
└─────────────────────────────────────┘
    ↓ [100 ranked docs with scores]
┌─────────────────────────────────────┐
│ 4. METADATA FILTER                  │  Week 5-6
│ Filter by:                          │
│ - Category                          │
│ - Tags                              │
│ - Freshness                         │
│ Result: 50 filtered docs            │
└─────────────────────────────────────┘
    ↓ [50 filtered docs]
┌─────────────────────────────────────┐
│ 5. RERANKER (Cross-Encoder)         │  Week 2-3
│ Score each doc by relevance         │
│ Keep top-10                         │
└─────────────────────────────────────┘
    ↓ [Top-10 chunks]
┌─────────────────────────────────────┐
│ 6. CONTEXT COMPRESSION              │  Week 6-7
│ - Extract relevant sentences        │
│ - Remove duplicates                 │
│ - Compress to ~2000 tokens          │
└─────────────────────────────────────┘
    ↓ [Clean context + citations]
┌─────────────────────────────────────┐
│ 7. KNOWLEDGE GRAPH LOOKUP           │  Week 9-10
│ - Check for entity relationships    │
│ - Add graph-based context           │
└─────────────────────────────────────┘
    ↓ [Final context + graph]
┌─────────────────────────────────────┐
│ 8. CITATION SETUP                   │  Week 7-8
│ - Map each sentence to source       │
│ - Prepare citation markers          │
└─────────────────────────────────────┘
    ↓ [Citation-ready context]
┌─────────────────────────────────────┐
│ 9. LLM SYNTHESIS (Mistral 7B)       │  Week 3 (use existing)
│ "Write answer based on context"     │
│ (NOT reasoning, just rephrasing)    │
└─────────────────────────────────────┘
    ↓
Response with citations
```

---

## 📅 WEEK-BY-WEEK IMPLEMENTATION

### **WEEK 1-2: HYBRID SEARCH (BM25 + Vector)**

**Objective:** Enable semantic search without keyword dependency

**Files to create:**
- `retrieval/hybrid_search.py`
- `models/embedder.py`
- `tests/test_retrieval.py`

**Step 1.1: Setup FAISS**
```python
# retrieval/hybrid_search.py

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class HybridSearchEngine:
    def __init__(self, documents, embedding_model="all-MiniLM-L6-v2"):
        """
        Initialize hybrid search with FAISS + BM25
        
        Args:
            documents: List of doc dicts with 'content', 'title', 'id'
            embedding_model: HuggingFace model name (small, fast)
        """
        self.docs = documents
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize BM25 (already have)
        from rank_bm25 import BM25Okapi
        self.tokenized_docs = [
            doc['content'].lower().split() for doc in documents
        ]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        
        # Initialize FAISS
        self.embeddings = self._create_embeddings()
        self.index = self._build_faiss_index()
    
    def _create_embeddings(self):
        """Create vector embeddings for all documents"""
        corpus = [f"{doc['title']} {doc['content']}" for doc in self.docs]
        embeddings = self.embedding_model.encode(
            corpus, 
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings
    
    def _build_faiss_index(self):
        """Build FAISS index for fast similarity search"""
        dimension = self.embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(self.embeddings.astype('float32'))
        return index
    
    def bm25_search(self, query, top_k=50):
        """Traditional keyword search"""
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        
        results = []
        for idx, score in enumerate(scores):
            if score > 0:
                results.append({
                    'id': self.docs[idx]['id'],
                    'title': self.docs[idx]['title'],
                    'score': float(score),
                    'method': 'bm25'
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
    
    def vector_search(self, query, top_k=50):
        """Semantic search via embeddings"""
        query_embedding = self.embedding_model.encode(
            query, 
            convert_to_numpy=True
        ).reshape(1, -1)
        
        distances, indices = self.index.search(
            query_embedding.astype('float32'), 
            top_k
        )
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            # Convert L2 distance to similarity score (inverse)
            similarity = 1 / (1 + distance)
            results.append({
                'id': self.docs[idx]['id'],
                'title': self.docs[idx]['title'],
                'score': float(similarity),
                'method': 'vector'
            })
        
        return results
    
    def hybrid_search(self, query, top_k=50, alpha=0.4):
        """
        Combine BM25 + Vector search
        
        Args:
            query: User question
            top_k: Number of results
            alpha: Weight for BM25 (0.4 = 40% BM25, 60% vector)
        """
        # Get results from both methods
        bm25_results = self.bm25_search(query, top_k=100)
        vector_results = self.vector_search(query, top_k=100)
        
        # Normalize scores to [0, 1]
        bm25_max = max([r['score'] for r in bm25_results], default=1)
        vector_max = max([r['score'] for r in vector_results], default=1)
        
        # Combine scores
        score_map = {}
        
        for result in bm25_results:
            doc_id = result['id']
            normalized_score = result['score'] / bm25_max if bm25_max > 0 else 0
            score_map[doc_id] = score_map.get(doc_id, 0) + alpha * normalized_score
        
        for result in vector_results:
            doc_id = result['id']
            normalized_score = result['score'] / vector_max if vector_max > 0 else 0
            score_map[doc_id] = score_map.get(doc_id, 0) + (1 - alpha) * normalized_score
        
        # Sort and return top-k
        final_results = [
            {
                'id': doc_id,
                'title': next(d['title'] for d in self.docs if d['id'] == doc_id),
                'score': score,
                'method': 'hybrid'
            }
            for doc_id, score in score_map.items()
        ]
        
        return sorted(
            final_results, 
            key=lambda x: x['score'], 
            reverse=True
        )[:top_k]
```

**Step 1.2: Test Hybrid Search**
```python
# tests/test_retrieval.py

def test_hybrid_search():
    from retrieval.hybrid_search import HybridSearchEngine
    
    documents = load_jira_docs()
    search = HybridSearchEngine(documents)
    
    # Test cases
    test_queries = [
        ("Nếu service chết thì sao?", "resilience"),  # Semantic
        ("microservice", "architecture"),              # Keyword
        ("goroutine leak", "concurrency"),             # Semantic + keyword
    ]
    
    for query, expected_keyword in test_queries:
        results = search.hybrid_search(query, top_k=5)
        assert len(results) > 0
        assert expected_keyword.lower() in results[0]['title'].lower()
        print(f"✅ {query} → {results[0]['title']}")
```

**Deliverable:** `hybrid_search.py` + tests passing

---

### **WEEK 2-3: RERANKER (Cross-Encoder)**

**Objective:** Pick the RIGHT document, not just top keyword match

**Files to create:**
- `retrieval/reranker.py`
- `models/reranker_model.py`
- `tests/test_reranking.py`

**Step 2.1: Setup Cross-Encoder**
```python
# retrieval/reranker.py

from sentence_transformers import CrossEncoder
import numpy as np

class DocumentReranker:
    def __init__(self, model_name="bge-reranker-v2-m3"):
        """
        Initialize cross-encoder for relevance ranking
        
        Note: First time will download ~1.2GB model
        """
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query, documents, top_k=10):
        """
        Rerank documents by relevance to query
        
        Args:
            query: User question
            documents: List of doc dicts
            top_k: Keep top-k results
        
        Returns:
            List of reranked documents with scores
        """
        # Prepare pairs: (query, doc_text)
        doc_texts = [
            f"{doc['title']}\n{doc['content'][:500]}"
            for doc in documents
        ]
        
        pairs = [[query, doc_text] for doc_text in doc_texts]
        
        # Get relevance scores
        scores = self.model.predict(pairs)
        
        # Add scores to documents
        results = []
        for doc, score in zip(documents, scores):
            results.append({
                **doc,
                'rerank_score': float(score)
            })
        
        # Sort by rerank score
        return sorted(
            results, 
            key=lambda x: x['rerank_score'], 
            reverse=True
        )[:top_k]
```

**Step 2.2: Integrate with Hybrid Search**
```python
# retrieval/hybrid_search.py (update)

def search_and_rerank(self, query, top_k=10):
    """Hybrid search + reranking"""
    # Get 100 candidates from hybrid search
    candidates = self.hybrid_search(query, top_k=100)
    
    # Convert to doc format for reranker
    docs = [
        self.docs[idx] for idx in range(len(self.docs))
        if self.docs[idx]['id'] in [c['id'] for c in candidates]
    ]
    
    # Rerank
    reranked = self.reranker.rerank(query, docs, top_k=top_k)
    
    return reranked
```

**Deliverable:** `reranker.py` + integration tests

---

### **WEEK 3-4: QUERY REWRITER (Intent Detection)**

**Objective:** Expand query to catch more relevant documents

**Files to create:**
- `retrieval/query_rewriter.py`
- `tests/test_query_rewrite.py`

**Step 3.1: Rule-based Query Rewriter**
```python
# retrieval/query_rewriter.py

class QueryRewriter:
    def __init__(self):
        """Rule-based query expansion"""
        self.expansion_rules = {
            "goroutine leak": [
                "goroutine memory leak",
                "unbounded goroutine",
                "goroutine termination",
                "context cancellation",
                "worker pool"
            ],
            "service.*die": [
                "service failure",
                "service timeout",
                "service unavailable",
                "circuit breaker",
                "retry policy",
                "fallback"
            ],
            "jwt": [
                "authentication",
                "token",
                "oauth",
                "authorization",
                "session"
            ],
            "deployment": [
                "kubernetes",
                "docker",
                "ci/cd",
                "release",
                "scale"
            ],
        }
    
    def rewrite(self, query):
        """
        Expand query based on rules
        
        Returns:
            List of expanded queries to search
        """
        expanded = [query]  # Always include original
        
        query_lower = query.lower()
        
        # Exact match expansion
        for keyword, expansions in self.expansion_rules.items():
            if keyword in query_lower:
                expanded.extend(expansions)
        
        # Fuzzy match (if original not found)
        if not any(kw in query_lower for kw in self.expansion_rules.keys()):
            # Use LLM for expansion (optional, Phase 2.5)
            pass
        
        # Remove duplicates, keep order
        seen = set()
        result = []
        for q in expanded:
            if q.lower() not in seen:
                result.append(q)
                seen.add(q.lower())
        
        return result
    
    def multi_query_search(self, query, search_engine, top_k=50):
        """
        Search with multiple query variants
        Combine results
        """
        expanded_queries = self.rewrite(query)
        
        all_results = {}
        
        # Search each variant
        for expanded_q in expanded_queries:
            results = search_engine.hybrid_search(expanded_q, top_k=50)
            
            for result in results:
                doc_id = result['id']
                if doc_id not in all_results:
                    all_results[doc_id] = {
                        **result,
                        'match_count': 0,
                        'match_queries': []
                    }
                
                all_results[doc_id]['match_count'] += 1
                all_results[doc_id]['match_queries'].append(expanded_q)
        
        # Rank by: match_count * base_score
        final_results = []
        for doc_id, doc in all_results.items():
            doc['boost_score'] = doc['score'] * (1 + 0.2 * doc['match_count'])
            final_results.append(doc)
        
        return sorted(
            final_results,
            key=lambda x: x['boost_score'],
            reverse=True
        )[:top_k]
```

**Deliverable:** `query_rewriter.py` + multi-query search

---

### **WEEK 4-5: SMART CHUNKING**

**Objective:** Split documents into semantic chunks instead of token-based

**Files to create:**
- `retrieval/chunk_manager.py`
- `tests/test_chunking.py`

**Step 4.1: Smart Chunking**
```python
# retrieval/chunk_manager.py

import re
from typing import List, Dict

class ChunkManager:
    def __init__(self, chunk_size=400, overlap=50):
        """
        Smart chunking by semantic boundaries
        
        Args:
            chunk_size: Target tokens per chunk
            overlap: Overlap tokens between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_document(self, document: Dict) -> List[Dict]:
        """
        Split document into smart chunks
        
        Strategy:
        1. Split by section headers (##, ###)
        2. Split by paragraphs if section too long
        3. Maintain overlap for context
        """
        title = document['title']
        content = document['content']
        doc_id = document['id']
        
        chunks = []
        
        # Split by section headers
        sections = re.split(r'\n#+\s+', content)
        
        current_section = ""
        for i, section in enumerate(sections):
            # Get section title if exists
            section_title = ""
            if i > 0:
                # Try to extract section name from context
                section_title = section.split('\n')[0][:50]
            
            # If section is small, accumulate
            if len(section.split()) < self.chunk_size:
                current_section += section + "\n"
            else:
                # If accumulated, flush
                if current_section:
                    chunk = self._create_chunk(
                        title, 
                        current_section, 
                        doc_id, 
                        section_title
                    )
                    chunks.append(chunk)
                    current_section = ""
                
                # Split large section by paragraphs
                paragraphs = section.split('\n\n')
                para_chunk = ""
                
                for para in paragraphs:
                    if len((para_chunk + para).split()) < self.chunk_size:
                        para_chunk += para + "\n\n"
                    else:
                        if para_chunk:
                            chunk = self._create_chunk(
                                title,
                                para_chunk,
                                doc_id,
                                section_title
                            )
                            chunks.append(chunk)
                        para_chunk = para + "\n\n"
                
                # Flush remaining
                if para_chunk:
                    chunk = self._create_chunk(
                        title,
                        para_chunk,
                        doc_id,
                        section_title
                    )
                    chunks.append(chunk)
        
        # Flush accumulated
        if current_section:
            chunk = self._create_chunk(title, current_section, doc_id)
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, title, content, doc_id, section=""):
        """Create chunk with metadata"""
        return {
            'doc_id': doc_id,
            'title': title,
            'section': section,
            'content': content.strip(),
            'word_count': len(content.split()),
            'char_count': len(content)
        }
    
    def chunk_all_documents(self, documents):
        """Chunk all documents"""
        all_chunks = []
        chunk_id = 0
        
        for doc in documents:
            chunks = self.chunk_document(doc)
            for chunk in chunks:
                chunk['chunk_id'] = chunk_id
                all_chunks.append(chunk)
                chunk_id += 1
        
        return all_chunks
```

**Deliverable:** `chunk_manager.py` + chunked document cache

---

### **WEEK 5-6: METADATA FILTERING**

**Objective:** Filter search results by category, tags, freshness

**Files to create:**
- `retrieval/metadata_filter.py`
- `data/metadata/document_metadata.json`

**Step 5.1: Document Metadata**
```python
# data/metadata/document_metadata.json

{
  "documents": [
    {
      "id": "microservices-arch",
      "title": "Microservices Architecture",
      "categories": ["Architecture", "Backend", "Design"],
      "tags": ["service", "architecture", "design", "deployment"],
      "author": "Platform Team",
      "last_updated": "2024-07-15",
      "importance": 0.95,
      "is_core": true
    },
    {
      "id": "go-routine",
      "title": "Go Routine",
      "categories": ["Backend", "Go", "Concurrency"],
      "tags": ["goroutine", "concurrency", "performance"],
      "author": "Backend Team",
      "last_updated": "2024-06-20",
      "importance": 0.85,
      "is_core": true
    },
    ...
  ]
}
```

**Step 5.2: Metadata Filter**
```python
# retrieval/metadata_filter.py

class MetadataFilter:
    def __init__(self, metadata_path="data/metadata/document_metadata.json"):
        import json
        with open(metadata_path) as f:
            self.metadata = json.load(f)
        
        self.metadata_map = {
            doc['id']: doc for doc in self.metadata['documents']
        }
    
    def filter_by_category(self, documents, categories):
        """Keep docs with matching categories"""
        if not categories:
            return documents
        
        filtered = []
        for doc in documents:
            meta = self.metadata_map.get(doc['id'])
            if meta and any(cat in meta['categories'] for cat in categories):
                filtered.append(doc)
        
        return filtered
    
    def filter_by_tags(self, documents, tags):
        """Keep docs with matching tags"""
        if not tags:
            return documents
        
        filtered = []
        for doc in documents:
            meta = self.metadata_map.get(doc['id'])
            if meta and any(tag in meta['tags'] for tag in tags):
                filtered.append(doc)
        
        return filtered
    
    def filter_core_only(self, documents):
        """Keep only core/important documents"""
        filtered = []
        for doc in documents:
            meta = self.metadata_map.get(doc['id'])
            if meta and meta.get('is_core', False):
                filtered.append(doc)
        
        return filtered if filtered else documents
    
    def apply_filters(self, documents, categories=None, tags=None, core_only=False):
        """Apply multiple filters"""
        result = documents
        
        if categories:
            result = self.filter_by_category(result, categories)
        
        if tags:
            result = self.filter_by_tags(result, tags)
        
        if core_only:
            result = self.filter_core_only(result)
        
        return result
```

**Deliverable:** `metadata_filter.py` + metadata.json

---

### **WEEK 6-7: CONTEXT COMPRESSION & CITATION**

**Objective:** Extract only relevant parts, reduce token usage, track sources

**Files to create:**
- `processing/context_compressor.py`
- `processing/citation_handler.py`

**Step 6.1: Context Compression**
```python
# processing/context_compressor.py

class ContextCompressor:
    def __init__(self):
        pass
    
    def compress_chunk(self, chunk, query, keep_sentences=3):
        """
        Keep only relevant sentences from chunk
        """
        content = chunk['content']
        sentences = content.split('.')
        
        # Score sentences by relevance to query
        query_words = set(query.lower().split())
        
        scored_sentences = []
        for i, sent in enumerate(sentences):
            sent_words = set(sent.lower().split())
            relevance = len(query_words & sent_words) / (len(query_words) + 1e-6)
            scored_sentences.append((i, sent, relevance))
        
        # Keep top sentences by position + relevance
        important = sorted(
            scored_sentences,
            key=lambda x: (-x[2], x[0])  # By relevance, then position
        )[:keep_sentences]
        
        # Restore original order
        important = sorted(important, key=lambda x: x[0])
        
        compressed = '.'.join([s[1] for s in important])
        
        return {
            **chunk,
            'compressed_content': compressed,
            'original_length': len(content.split()),
            'compressed_length': len(compressed.split())
        }
    
    def compress_context(self, chunks, query, max_tokens=2000):
        """
        Compress all chunks to fit within token budget
        """
        compressed_chunks = []
        token_count = 0
        
        for chunk in chunks:
            compressed = self.compress_chunk(chunk, query, keep_sentences=3)
            chunk_tokens = len(compressed['compressed_content'].split())
            
            if token_count + chunk_tokens < max_tokens:
                compressed_chunks.append(compressed)
                token_count += chunk_tokens
            else:
                # Try to fit partial chunk
                remaining = max_tokens - token_count
                if remaining > 50:
                    # Keep partial sentences
                    sentences = compressed['compressed_content'].split('.')[:1]
                    partial = '.'.join(sentences)
                    compressed['compressed_content'] = partial
                    compressed_chunks.append(compressed)
                
                break
        
        return compressed_chunks, token_count
```

**Step 6.2: Citation Handler**
```python
# processing/citation_handler.py

class CitationHandler:
    def __init__(self):
        pass
    
    def map_citations(self, chunks):
        """
        Create citation map for compressed chunks
        
        Returns: {chunk_id: {doc_title, section, updated_date, owner}}
        """
        citations = {}
        
        for chunk in chunks:
            citations[chunk['chunk_id']] = {
                'doc_id': chunk['doc_id'],
                'title': chunk['title'],
                'section': chunk.get('section', 'General'),
                'updated': chunk.get('last_updated', 'N/A'),
                'owner': chunk.get('author', 'Platform Team')
            }
        
        return citations
    
    def format_citation(self, chunk_id, citations):
        """Format a single citation for inline reference"""
        if chunk_id not in citations:
            return ""
        
        cite = citations[chunk_id]
        return f"[{cite['title']} - {cite['section']}]"
    
    def add_citations_to_answer(self, answer, chunk_ids, citations):
        """
        Add citations to answer text
        Simple approach: append citations at end
        """
        cite_lines = []
        
        for i, chunk_id in enumerate(chunk_ids, 1):
            if chunk_id in citations:
                cite = citations[chunk_id]
                cite_lines.append(
                    f"{i}. {cite['title']} - {cite['section']}\n"
                    f"   Updated: {cite['updated']} | Owner: {cite['owner']}"
                )
        
        if cite_lines:
            answer += "\n\n**Sources:**\n" + "\n".join(cite_lines)
        
        return answer
```

**Deliverable:** `context_compressor.py` + `citation_handler.py`

---

### **WEEK 7-8: CONVERSATION MEMORY**

**Objective:** Track multi-turn conversations, maintain context

**Files to create:**
- `memory/conversation_memory.py`
- `memory/session_manager.py`

**Step 7.1: Conversation Memory**
```python
# memory/conversation_memory.py

class ConversationMemory:
    def __init__(self, max_history=5, max_tokens=2000):
        """
        Track conversation history
        
        Args:
            max_history: Keep last N turns
            max_tokens: Max tokens in summary
        """
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.turns = []  # List of {question, answer, context}
    
    def add_turn(self, question, answer, context=None):
        """Add a new turn to history"""
        self.turns.append({
            'question': question,
            'answer': answer[:200],  # Keep summary
            'context': context,
            'timestamp': time.time()
        })
        
        # Keep only recent turns
        if len(self.turns) > self.max_history:
            self.turns.pop(0)
    
    def get_summary(self):
        """
        Summarize conversation for context injection
        
        Format:
        Q: First question
        A: Brief answer...
        
        Q: Second question  
        A: Brief answer...
        
        (Current question)
        """
        if not self.turns:
            return ""
        
        summary_parts = []
        token_count = 0
        
        for turn in self.turns[-3:]:  # Last 3 turns
            q_line = f"Q: {turn['question']}"
            a_line = f"A: {turn['answer']}"
            
            tokens = len((q_line + a_line).split())
            if token_count + tokens < self.max_tokens:
                summary_parts.append(q_line)
                summary_parts.append(a_line)
                summary_parts.append("")  # Blank line
                token_count += tokens
        
        return "\n".join(summary_parts)
    
    def should_expand_query(self):
        """Decide if query needs context from history"""
        return len(self.turns) > 0
```

**Step 7.2: Session Manager**
```python
# memory/session_manager.py

import json
import os
from datetime import datetime

class SessionManager:
    def __init__(self, session_dir="data/sessions"):
        self.session_dir = session_dir
        os.makedirs(session_dir, exist_ok=True)
    
    def create_session(self, session_id=None):
        """Create new conversation session"""
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        session = {
            'id': session_id,
            'created': datetime.now().isoformat(),
            'memory': ConversationMemory(),
            'turns': []
        }
        
        return session
    
    def save_session(self, session):
        """Save session to disk"""
        path = os.path.join(self.session_dir, f"{session['id']}.json")
        
        # Serialize (exclude memory object)
        data = {
            'id': session['id'],
            'created': session['created'],
            'turns': session['turns']
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_session(self, session_id):
        """Load session from disk"""
        path = os.path.join(self.session_dir, f"{session_id}.json")
        
        if not os.path.exists(path):
            return self.create_session(session_id)
        
        with open(path) as f:
            data = json.load(f)
        
        session = {
            **data,
            'memory': ConversationMemory()
        }
        
        # Restore turns to memory
        for turn in data['turns']:
            session['memory'].add_turn(
                turn['question'],
                turn['answer'],
                turn.get('context')
            )
        
        return session
```

**Deliverable:** `conversation_memory.py` + `session_manager.py`

---

### **WEEK 8-9: KNOWLEDGE GRAPH**

**Objective:** Store entity relationships for multi-hop reasoning

**Files to create:**
- `processing/knowledge_graph.py`
- `data/graph/knowledge_graph.json`

**Step 8.1: Knowledge Graph**
```python
# processing/knowledge_graph.py

import json
from typing import Dict, List

class KnowledgeGraph:
    def __init__(self, graph_path="data/graph/knowledge_graph.json"):
        """Load knowledge graph from JSON"""
        with open(graph_path) as f:
            self.graph = json.load(f)
        
        self.entities = self.graph.get('entities', {})
        self.relations = self.graph.get('relations', {})
    
    def get_entity(self, entity_name):
        """Get entity by name"""
        for entity_id, entity in self.entities.items():
            if entity_name.lower() in entity['names']:
                return entity
        return None
    
    def get_related_entities(self, entity_id, relation_type=None, depth=1):
        """
        Get entities connected to this one
        
        Args:
            entity_id: Starting entity
            relation_type: Filter by relationship type
            depth: How many hops to follow
        """
        related = []
        visited = {entity_id}
        queue = [(entity_id, 0)]
        
        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_depth >= depth:
                continue
            
            # Find relationships
            for rel_id, rel in self.relations.items():
                if rel['from'] == current_id:
                    if relation_type and rel['type'] != relation_type:
                        continue
                    
                    target_id = rel['to']
                    if target_id not in visited:
                        visited.add(target_id)
                        related.append({
                            'entity': self.entities[target_id],
                            'relation': rel['type'],
                            'depth': current_depth + 1
                        })
                        queue.append((target_id, current_depth + 1))
        
        return related
    
    def find_path(self, source_id, target_id):
        """Find connection path between two entities"""
        from collections import deque
        
        queue = deque([(source_id, [source_id])])
        visited = {source_id}
        
        while queue:
            current_id, path = queue.popleft()
            
            if current_id == target_id:
                return path
            
            # Find next entities
            for rel_id, rel in self.relations.items():
                if rel['from'] == current_id:
                    next_id = rel['to']
                    if next_id not in visited:
                        visited.add(next_id)
                        queue.append((next_id, path + [next_id]))
        
        return None
    
    def get_context_from_graph(self, question):
        """
        Extract graph-based context for question
        
        E.g., "Order Service dependencies?"
        → Find Order Service → Get related entities
        """
        # Simple keyword matching for entity extraction
        for entity_id, entity in self.entities.items():
            if any(name in question.lower() for name in entity['names']):
                related = self.get_related_entities(entity_id, depth=2)
                
                if related:
                    context = f"\nGraph context: {entity['names'][0]} connects to:\n"
                    for rel in related:
                        context += f"- {rel['entity']['names'][0]} ({rel['relation']})\n"
                    
                    return context
        
        return ""
```

**Step 8.2: Knowledge Graph Data**
```python
# data/graph/knowledge_graph.json

{
  "entities": {
    "order-service": {
      "id": "order-service",
      "names": ["Order Service", "order"],
      "type": "service",
      "description": "Handles purchase/sale orders"
    },
    "auth-service": {
      "id": "auth-service",
      "names": ["Auth Service", "authentication"],
      "type": "service",
      "description": "User authentication"
    },
    "kafka": {
      "id": "kafka",
      "names": ["Kafka", "message queue"],
      "type": "infrastructure",
      "description": "Event streaming"
    },
    "notification-service": {
      "id": "notification-service",
      "names": ["Notification Service", "notification"],
      "type": "service",
      "description": "Send notifications"
    }
  },
  "relations": {
    "rel-1": {
      "from": "order-service",
      "to": "auth-service",
      "type": "depends_on",
      "description": "Order Service depends on Auth Service"
    },
    "rel-2": {
      "from": "order-service",
      "to": "kafka",
      "type": "publishes_to",
      "description": "Order Service publishes events to Kafka"
    },
    "rel-3": {
      "from": "kafka",
      "to": "notification-service",
      "type": "triggers",
      "description": "Kafka events trigger Notification Service"
    }
  }
}
```

**Deliverable:** `knowledge_graph.py` + graph.json

---

### **WEEK 9-10: INTEGRATION & PIPELINE**

**Objective:** Combine all 9 components into single pipeline

**Files to create:**
- `pipeline.py` (Main RAG pipeline)
- `app.py` (Phase 2 FastAPI)
- `config.py` (Configuration)

**Step 9.1: Complete RAG Pipeline**
```python
# pipeline.py

class RAGPipeline:
    def __init__(self):
        # Initialize all components
        self.hybrid_search = HybridSearchEngine(load_docs())
        self.reranker = DocumentReranker()
        self.query_rewriter = QueryRewriter()
        self.chunk_manager = ChunkManager()
        self.metadata_filter = MetadataFilter()
        self.compressor = ContextCompressor()
        self.citations = CitationHandler()
        self.memory = ConversationMemory()
        self.kg = KnowledgeGraph()
        self.session = SessionManager()
    
    def process_query(self, question, session_id=None):
        """Complete RAG pipeline"""
        
        # 1. Load/create session
        session = self.session.load_session(session_id)
        
        # 2. Get conversation context
        memory_summary = self.memory.get_summary() if self.memory.should_expand_query() else ""
        
        # 3. Rewrite query with context
        expanded_queries = self.query_rewriter.rewrite(question)
        
        # 4. Hybrid search + reranking
        candidates = []
        for query in expanded_queries:
            results = self.hybrid_search.search_and_rerank(query, top_k=50)
            candidates.extend(results)
        
        # 5. Metadata filtering
        filtered = self.metadata_filter.apply_filters(
            candidates,
            core_only=True
        )
        
        # 6. Chunk documents
        chunks = []
        for doc in filtered[:10]:  # Top 10
            doc_chunks = self.chunk_manager.chunk_document(doc)
            chunks.extend(doc_chunks)
        
        # 7. Context compression
        compressed, tokens = self.compressor.compress_context(
            chunks,
            question,
            max_tokens=2000
        )
        
        # 8. Add graph context
        graph_context = self.kg.get_context_from_graph(question)
        
        # 9. Prepare prompt with citations
        final_context = "\n".join([
            f"{c['compressed_content']}\n[Source: {c['title']}, {c['section']}]"
            for c in compressed
        ])
        
        if graph_context:
            final_context += graph_context
        
        if memory_summary:
            final_context = memory_summary + "\n\n" + final_context
        
        # 10. LLM synthesis
        prompt = f"""
        Conversation Context:
        {memory_summary}
        
        Sources:
        {final_context}
        
        Question: {question}
        
        Instructions:
        - Answer based on sources only
        - If unsure, say "I don't have this information"
        - Be concise and structured
        - Use bullet points when helpful
        """
        
        answer = self.llm.generate(prompt)
        
        # 11. Add citations to answer
        answer = self.citations.add_citations_to_answer(
            answer,
            [c['chunk_id'] for c in compressed],
            self.citations.map_citations(compressed)
        )
        
        # 12. Store in session memory
        self.memory.add_turn(question, answer, final_context)
        session['turns'].append({
            'question': question,
            'answer': answer,
            'context': final_context
        })
        self.session.save_session(session)
        
        return {
            'answer': answer,
            'session_id': session['id'],
            'sources': [c['title'] for c in compressed]
        }
```

**Step 9.2: Phase 2 FastAPI App**
```python
# app.py

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Anfin Knowledge Assistant - Phase 2")
pipeline = RAGPipeline()

class QueryRequest(BaseModel):
    question: str
    session_id: str = None

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    sources: List[str]

@app.post("/chat")
async def chat(request: QueryRequest):
    result = pipeline.process_query(
        request.question,
        request.session_id
    )
    return QueryResponse(**result)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "2.0",
        "components": [
            "hybrid_search",
            "reranker",
            "query_rewriter",
            "chunking",
            "compression",
            "citations",
            "memory",
            "knowledge_graph"
        ]
    }
```

**Deliverable:** Complete RAG pipeline + Phase 2 app

---

## 📊 EXPECTED RESULTS

| Week | Component | Status | Quality Impact |
|------|-----------|--------|-----------------|
| 1-2 | Hybrid Search | ✅ | +30% recall |
| 2-3 | Reranker | ✅ | +20% precision |
| 3-4 | Query Rewrite | ✅ | +15% coverage |
| 4-5 | Smart Chunking | ✅ | +15% relevance |
| 5-6 | Metadata Filter | ✅ | +10% accuracy |
| 6-7 | Compression + Citation | ✅ | Model focus + trust |
| 7-8 | Memory | ✅ | Multi-turn OK |
| 8-9 | Knowledge Graph | ✅ | +20% reasoning |
| 9-10 | Integration | ✅ | Full pipeline |

**Final Quality:** 85-90% (vs 8.5/10 for demo)

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] All 9 components implemented
- [ ] Tests passing (>95% coverage)
- [ ] Local integration working
- [ ] Response time <3s (avg)
- [ ] Memory usage <500MB
- [ ] Docker image built
- [ ] Deploy to Railway
- [ ] E2E testing on production

---

**This is a 10-week roadmap to build production-quality RAG with $0 cost.**

**Start Week 1 with Hybrid Search?**

