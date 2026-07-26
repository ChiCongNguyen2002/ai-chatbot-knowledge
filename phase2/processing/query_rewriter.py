"""
Phase 2 - Query Rewriter
Intent detection and intelligent query expansion
"""

import re
from typing import List, Dict, Tuple, Optional


class QueryRewriter:
    """
    Intelligent query rewriting for better search results.

    Strategy:
    1. Detect query intent (definition, comparison, example, how-to)
    2. Expand query with synonyms and related terms
    3. Generate variations of the query
    4. Use best variation for search

    Benefits:
    - Handles paraphrased queries ("How to split app into services" → "microservices")
    - Adds context terms ("Docker" → "Docker container orchestration deployment")
    - Improves semantic matching through multiple angles
    """

    def __init__(self):
        """Initialize query rewriter with synonym and expansion maps"""
        # Synonym mappings for Anfin tech stack
        self.synonyms = {
            'microservice': ['microservices', 'service-oriented', 'distributed-system', 'service-mesh'],
            'docker': ['container', 'containerization', 'image', 'dockerfile'],
            'kubernetes': ['k8s', 'orchestration', 'container-orchestration', 'deployment-platform'],
            'api': ['endpoint', 'rest', 'rest-api', 'http-api', 'interface', 'service-interface'],
            'kafka': ['event-streaming', 'pub-sub', 'message-broker', 'event-bus'],
            'database': ['db', 'sql', 'postgres', 'postgresql', 'mysql', 'data-store'],
            'cache': ['redis', 'in-memory', 'caching', 'cached-data'],
            'testing': ['test', 'unit-test', 'integration-test', 'e2e-test', 'test-case'],
            'deployment': ['deploy', 'rollout', 'release', 'go-live'],
            'monitoring': ['observability', 'logging', 'metrics', 'tracing', 'alerting'],
            'security': ['authentication', 'authorization', 'encryption', 'safety'],
            'performance': ['optimization', 'scalability', 'throughput', 'latency'],
            'concurrency': ['parallel', 'async', 'threading', 'goroutine'],
        }

        # Intent patterns for query understanding
        self.intent_patterns = {
            'definition': {
                'patterns': [r'^what is', r'^what\s+are', r'define', r'meaning\s+of', r'explain'],
                'boost_terms': ['definition', 'concept', 'overview', 'introduction']
            },
            'comparison': {
                'patterns': [r'vs\.?', r'versus', r'compared?\s+to', r'difference\s+between'],
                'boost_terms': ['comparison', 'difference', 'trade-off', 'vs']
            },
            'how-to': {
                'patterns': [r'^how', r'how do', r'how can', r'guide', r'tutorial', r'steps?'],
                'boost_terms': ['guide', 'tutorial', 'steps', 'implement', 'example']
            },
            'example': {
                'patterns': [r'example', r'for\s+example', r'sample', r'instance'],
                'boost_terms': ['example', 'sample', 'use-case', 'real-world']
            },
            'best-practice': {
                'patterns': [r'best\s+practice', r'pattern', r'recommend', r'should'],
                'boost_terms': ['best-practice', 'pattern', 'recommendation', 'guideline']
            }
        }

    def detect_intent(self, query: str) -> str:
        """
        Detect the intent of the query

        Args:
            query: User question

        Returns:
            Intent type: 'definition', 'comparison', 'how-to', 'example', 'best-practice', or 'general'
        """
        query_lower = query.lower()

        for intent, config in self.intent_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, query_lower):
                    return intent

        return 'general'

    def get_boost_terms(self, intent: str) -> List[str]:
        """Get boost terms for detected intent"""
        if intent in self.intent_patterns:
            return self.intent_patterns[intent]['boost_terms']
        return []

    def expand_terms(self, tokens: List[str]) -> List[str]:
        """
        Expand tokens with synonyms

        Args:
            tokens: List of query tokens

        Returns:
            Expanded list of tokens (original + synonyms)
        """
        expanded = list(tokens)

        for token in tokens:
            token_lower = token.lower()

            # Check direct synonyms
            if token_lower in self.synonyms:
                expanded.extend(self.synonyms[token_lower])

            # Check partial matches (e.g., "microservice" matches "microservices")
            for key, syns in self.synonyms.items():
                if key in token_lower or token_lower in key:
                    expanded.extend(syns)

        # Remove duplicates while preserving order
        seen = set()
        result = []
        for token in expanded:
            if token not in seen:
                seen.add(token)
                result.append(token)

        return result

    def rewrite_query(self, query: str) -> Dict[str, any]:
        """
        Rewrite query with expansion and intent detection

        Args:
            query: Original user question

        Returns:
            Dictionary with:
            - original: Original query
            - intent: Detected intent
            - expanded: Query with expanded terms
            - variations: Multiple query variations
            - primary_variation: Best variation for search
        """
        # Detect intent
        intent = self.detect_intent(query)

        # Tokenize
        tokens = re.findall(r'\w+', query.lower())

        # Expand with synonyms
        expanded_tokens = self.expand_terms(tokens)

        # Generate variations
        variations = []

        # Variation 1: Original + boost terms for intent
        boost_terms = self.get_boost_terms(intent)
        variation1 = f"{query} {' '.join(boost_terms)}"
        variations.append({
            'query': variation1.strip(),
            'type': f'intent-boosted ({intent})',
            'score': 1.0
        })

        # Variation 2: Expanded tokens
        variation2 = ' '.join(expanded_tokens)
        if variation2 != query:
            variations.append({
                'query': variation2,
                'type': 'synonym-expanded',
                'score': 0.95
            })

        # Variation 3: Original only (fallback)
        variations.append({
            'query': query,
            'type': 'original',
            'score': 0.90
        })

        # Sort by score
        variations.sort(key=lambda x: x['score'], reverse=True)

        return {
            'original': query,
            'intent': intent,
            'expanded_tokens': expanded_tokens,
            'variations': variations,
            'primary_variation': variations[0]['query'],
            'boost_terms': boost_terms
        }

    def generate_multi_queries(self, query: str, num_queries: int = 3) -> List[str]:
        """
        Generate multiple query variations for ensemble search

        Strategy: Search with multiple query angles to catch edge cases
        - Query 1: Original
        - Query 2: Synonym-expanded
        - Query 3: Intent-boosted

        Args:
            query: Original question
            num_queries: Number of variations to generate (1-3)

        Returns:
            List of query variations
        """
        rewritten = self.rewrite_query(query)

        queries = []
        for variation in rewritten['variations'][:num_queries]:
            queries.append(variation['query'])

        return queries


class QueryAnalyzer:
    """Analyze query characteristics for better understanding"""

    @staticmethod
    def get_query_length(query: str) -> str:
        """Classify query by length"""
        tokens = len(query.split())
        if tokens < 3:
            return 'short'
        elif tokens < 7:
            return 'medium'
        else:
            return 'long'

    @staticmethod
    def extract_entities(query: str) -> List[str]:
        """
        Extract potential entity mentions from query

        Simple heuristic: capitalized words or common tech terms
        """
        # Tech-specific terms (case-insensitive)
        tech_terms = {
            'docker', 'kubernetes', 'kafka', 'redis', 'mongodb', 'postgres',
            'microservices', 'api', 'rest', 'graphql', 'grpc', 'http',
            'go', 'python', 'java', 'javascript', 'rust', 'typescript',
            'aws', 'gcp', 'azure', 'railway', 'vercel', 'docker'
        }

        entities = []

        # Capitalized words (proper nouns)
        capitalized = re.findall(r'\b[A-Z]\w*\b', query)
        entities.extend(capitalized)

        # Tech terms
        query_lower = query.lower()
        for term in tech_terms:
            if term in query_lower:
                entities.append(term)

        # Remove duplicates
        return list(set(entities))

    @staticmethod
    def get_query_complexity(query: str) -> str:
        """Estimate query complexity"""
        tokens = query.split()
        unique_tokens = len(set(t.lower() for t in tokens))

        if unique_tokens < 3:
            return 'simple'
        elif unique_tokens < 6:
            return 'moderate'
        else:
            return 'complex'
