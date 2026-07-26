"""Phase 2: Setup Elasticsearch indexing"""

import json
import time
from typing import List, Dict

try:
    from elasticsearch import Elasticsearch
    ES_AVAILABLE = True
except ImportError:
    ES_AVAILABLE = False
    print("⚠️ elasticsearch package not installed")


def create_elasticsearch_index(es_host: str = "http://localhost:9200"):
    """Create and configure Elasticsearch index"""

    if not ES_AVAILABLE:
        print("❌ Elasticsearch not available")
        return None

    try:
        es = Elasticsearch([es_host])

        # Wait for ES to be ready
        max_retries = 10
        for i in range(max_retries):
            try:
                es.info()
                print("✅ Elasticsearch connected")
                break
            except Exception as e:
                if i < max_retries - 1:
                    print(f"⏳ Waiting for Elasticsearch... ({i+1}/{max_retries})")
                    time.sleep(2)
                else:
                    print(f"❌ Could not connect to Elasticsearch: {e}")
                    return None

        # Create index with mapping
        index_name = "knowledge"

        # Delete existing index if it exists
        try:
            es.indices.delete(index=index_name)
            print(f"🗑️  Deleted existing index '{index_name}'")
        except:
            pass

        # Create new index
        es.indices.create(
            index=index_name,
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "key": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "standard"},
                    "content": {"type": "text", "analyzer": "standard"},
                    "project": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "url": {"type": "keyword"},
                    "source": {"type": "keyword"}
                }
            },
            settings={
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        )

        print(f"✅ Created index '{index_name}'")
        return es

    except Exception as e:
        print(f"❌ Error creating Elasticsearch index: {e}")
        return None


def index_documents(es, docs: List[Dict], index_name: str = "knowledge"):
    """Index documents into Elasticsearch"""

    if not es:
        print("❌ Elasticsearch not available")
        return False

    try:
        for doc in docs:
            es.index(index=index_name, id=doc["id"], document=doc)

        print(f"✅ Indexed {len(docs)} documents")

        # Refresh index
        es.indices.refresh(index=index_name)
        print(f"✅ Index refreshed")

        return True

    except Exception as e:
        print(f"❌ Error indexing documents: {e}")
        return False


def verify_elasticsearch(es, index_name: str = "knowledge"):
    """Verify Elasticsearch index"""

    if not es:
        return False

    try:
        # Get index stats
        stats = es.indices.stats(index=index_name)
        doc_count = stats["indices"][index_name]["primaries"]["docs"]["count"]

        print(f"\n✅ Index '{index_name}' has {doc_count} documents")

        # Test search
        result = es.search(
            index=index_name,
            query={"match": {"content": "microservices"}}
        )
        hits = len(result["hits"]["hits"])
        print(f"✅ Search test: found {hits} results for 'microservices'")

        return True

    except Exception as e:
        print(f"❌ Error verifying Elasticsearch: {e}")
        return False


if __name__ == "__main__":
    print("🔄 Setting up Elasticsearch...")

    # Create ES connection
    es = create_elasticsearch_index()

    if es:
        # Load documents
        with open("jira_docs.json") as f:
            docs = json.load(f)

        # Index documents
        index_documents(es, docs)

        # Verify
        verify_elasticsearch(es)
