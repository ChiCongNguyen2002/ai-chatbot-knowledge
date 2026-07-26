"""
Phase 2 - Context Compression & Citation
Compress long contexts and track citations
"""

from typing import List, Dict, Tuple, Optional
import re


class ContextCompressor:
    """
    Compress search results to fit within token limits

    Strategies:
    1. Extract key sentences (TF-IDF style)
    2. Remove redundant information
    3. Preserve question-relevant content
    4. Maintain citations to original docs
    """

    def __init__(self, max_tokens: int = 4000):
        """
        Initialize context compressor

        Args:
            max_tokens: Maximum tokens in output (approximate)
        """
        self.max_tokens = max_tokens
        self.tokens_per_word = 0.75  # Rough estimate: 1 word ≈ 0.75 tokens

    def compress_context(
        self,
        documents: List[Dict],
        query: str,
        max_words: Optional[int] = None
    ) -> str:
        """
        Compress documents into combined context

        Args:
            documents: Search results
            query: User question (for relevance)
            max_words: Override max word count

        Returns:
            Compressed context with citations
        """
        if not documents:
            return ""

        max_words = max_words or int(self.max_tokens / self.tokens_per_word)

        # Score sentences by relevance to query
        context_parts = []

        for doc in documents:
            title = doc.get('title', '')
            content = doc.get('content', '')

            # Extract key sentences
            key_sentences = self._extract_key_sentences(content, query, max_sentences=3)

            if key_sentences:
                context_parts.append({
                    'title': title,
                    'sentences': key_sentences,
                    'doc_id': doc.get('id', 'unknown')
                })

        # Combine and truncate
        combined = self._combine_with_citations(context_parts, max_words)
        return combined

    def _extract_key_sentences(
        self,
        text: str,
        query: str,
        max_sentences: int = 3
    ) -> List[str]:
        """Extract key sentences relevant to query"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        # Score by relevance to query
        query_words = set(query.lower().split())
        scored = []

        for sent in sentences:
            sent_words = set(sent.lower().split())
            relevance = len(query_words & sent_words) / (len(query_words) + 1)
            scored.append((sent, relevance))

        # Sort by relevance
        scored.sort(key=lambda x: x[1], reverse=True)

        # Return top sentences
        return [s[0] for s in scored[:max_sentences]]

    def _combine_with_citations(
        self,
        context_parts: List[Dict],
        max_words: int
    ) -> str:
        """Combine contexts with citations"""
        result = []
        word_count = 0

        for i, part in enumerate(context_parts, 1):
            title = part['title']
            sentences = part['sentences']
            doc_id = part['doc_id']

            # Add source header
            source_header = f"\n[Source {i}: {title} (ID: {doc_id})]"
            result.append(source_header)
            word_count += len(source_header.split())

            # Add sentences
            for sent in sentences:
                if word_count >= max_words:
                    result.append(" ...")
                    break

                result.append(f" {sent}")
                word_count += len(sent.split())

            if word_count >= max_words:
                break

        return "".join(result)


class CitationHandler:
    """
    Track and format citations for search results
    """

    def __init__(self):
        """Initialize citation handler"""
        self.citations = {}

    def add_citation(
        self,
        doc_id: str,
        title: str,
        content: str,
        snippet: str
    ) -> str:
        """
        Add citation and return citation key

        Args:
            doc_id: Document ID
            title: Document title
            content: Full content
            snippet: Text snippet cited

        Returns:
            Citation key (e.g., "[1]")
        """
        citation_key = f"[{len(self.citations) + 1}]"

        self.citations[citation_key] = {
            'doc_id': doc_id,
            'title': title,
            'snippet': snippet,
            'full_content': content
        }

        return citation_key

    def format_citations(self, format_type: str = 'inline') -> str:
        """
        Format citations for output

        Args:
            format_type: 'inline', 'footnote', or 'bibliography'

        Returns:
            Formatted citation section
        """
        if not self.citations:
            return ""

        if format_type == 'inline':
            return self._format_inline()
        elif format_type == 'footnote':
            return self._format_footnote()
        else:  # bibliography
            return self._format_bibliography()

    def _format_inline(self) -> str:
        """Inline citation format"""
        parts = ["\n\n**Sources:**"]

        for key, citation in self.citations.items():
            parts.append(f"  {key} **{citation['title']}** (ID: {citation['doc_id']})")

        return "\n".join(parts)

    def _format_footnote(self) -> str:
        """Footnote style citations"""
        parts = ["\n\n**References:**"]

        for key, citation in self.citations.items():
            parts.append(
                f"  {key} {citation['title']}\n"
                f"      Snippet: \"{citation['snippet'][:100]}...\""
            )

        return "\n".join(parts)

    def _format_bibliography(self) -> str:
        """Bibliography style citations"""
        parts = ["\n\n**Bibliography:**"]

        for key, citation in sorted(self.citations.items()):
            parts.append(
                f"  {citation['title']}. "
                f"(Source ID: {citation['doc_id']})"
            )

        return "\n".join(parts)

    def clear(self):
        """Clear citations for new query"""
        self.citations = {}
