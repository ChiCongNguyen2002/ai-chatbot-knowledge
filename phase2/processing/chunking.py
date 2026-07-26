"""
Phase 2 - Smart Chunking
Split documents by semantic boundaries instead of fixed token count
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a document chunk"""
    id: str
    source_doc_id: str
    text: str
    start_pos: int
    end_pos: int
    chunk_type: str  # 'paragraph', 'section', 'table', 'list'
    metadata: Dict = None


class SmartChunker:
    """
    Split documents into chunks by semantic boundaries.

    Strategies:
    1. Detect natural boundaries (paragraphs, sections, lists)
    2. Preserve context with overlap between chunks
    3. Respect semantic unit sizes (not arbitrary token counts)
    4. Maintain metadata for each chunk

    Benefits:
    - Better retrieval: complete semantic units
    - Better context: not cutting mid-sentence
    - Better ranking: chunk boundaries are natural
    """

    def __init__(
        self,
        chunk_size: int = 300,
        overlap: int = 50,
        min_chunk_size: int = 100
    ):
        """
        Initialize smart chunker

        Args:
            chunk_size: Target characters per chunk (approximate)
            overlap: Characters to overlap between chunks
            min_chunk_size: Minimum characters to create a chunk
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

    def chunk_document(
        self,
        doc_id: str,
        title: str,
        content: str
    ) -> List[Chunk]:
        """
        Chunk a document into semantic units

        Strategy:
        1. Split by double newline (paragraphs) first
        2. If paragraphs too large, split by sentences
        3. Add overlap between chunks
        4. Preserve metadata

        Args:
            doc_id: Document identifier
            title: Document title
            content: Document content

        Returns:
            List of chunks with metadata
        """
        chunks = []

        # First pass: split by paragraphs (double newline)
        paragraphs = content.split('\n\n')

        current_chunk_text = ""
        current_chunk_start = 0
        char_pos = 0

        for para_idx, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                char_pos += 2  # Account for \n\n
                continue

            # Try to add paragraph to current chunk
            test_text = (
                current_chunk_text + "\n\n" + paragraph
                if current_chunk_text
                else paragraph
            )

            if len(test_text) <= self.chunk_size:
                # Paragraph fits in current chunk
                if current_chunk_text:
                    current_chunk_text += "\n\n"
                current_chunk_text += paragraph
            else:
                # Paragraph doesn't fit

                # Save current chunk if large enough
                if len(current_chunk_text) >= self.min_chunk_size:
                    chunk = self._create_chunk(
                        doc_id,
                        title,
                        current_chunk_text,
                        current_chunk_start,
                        len(chunks)
                    )
                    chunks.append(chunk)

                # Start new chunk with current paragraph
                current_chunk_text = paragraph
                current_chunk_start = char_pos

            char_pos += len(paragraph) + 2  # Account for \n\n

        # Add final chunk
        if len(current_chunk_text) >= self.min_chunk_size:
            chunk = self._create_chunk(
                doc_id,
                title,
                current_chunk_text,
                current_chunk_start,
                len(chunks)
            )
            chunks.append(chunk)

        # Add overlap
        chunks = self._add_overlap(chunks)

        return chunks

    def _create_chunk(
        self,
        doc_id: str,
        title: str,
        text: str,
        start_pos: int,
        chunk_index: int
    ) -> Chunk:
        """Create a chunk with metadata"""
        chunk_type = self._detect_chunk_type(text)

        return Chunk(
            id=f"{doc_id}_chunk{chunk_index}",
            source_doc_id=doc_id,
            text=text,
            start_pos=start_pos,
            end_pos=start_pos + len(text),
            chunk_type=chunk_type,
            metadata={
                'title': title,
                'source_doc_id': doc_id,
                'chunk_index': chunk_index,
                'chunk_type': chunk_type,
                'char_length': len(text),
                'word_count': len(text.split())
            }
        )

    def _detect_chunk_type(self, text: str) -> str:
        """Detect the type of chunk"""
        if re.search(r'[│├└]', text):  # ASCII table characters
            return 'table'
        elif re.search(r'^[\s]*[-*•] ', text, re.MULTILINE):
            return 'list'
        elif re.search(r'^#{1,6} ', text, re.MULTILINE):
            return 'section'
        else:
            return 'paragraph'

    def _add_overlap(self, chunks: List[Chunk]) -> List[Chunk]:
        """Add overlapping context between chunks"""
        if len(chunks) <= 1:
            return chunks

        enhanced_chunks = []

        for i, chunk in enumerate(chunks):
            enhanced_chunk = chunk
            overlap_text = ""

            # Add previous chunk's ending as context
            if i > 0:
                prev_text = chunks[i - 1].text
                overlap_text = prev_text[-self.overlap:] if len(prev_text) > self.overlap else prev_text

            # Add current chunk
            if overlap_text:
                enhanced_chunk.text = f"...\n{overlap_text}\n\n{chunk.text}"

            enhanced_chunks.append(enhanced_chunk)

        return enhanced_chunks

    def chunk_documents(self, documents: List[Dict]) -> List[Chunk]:
        """Chunk multiple documents"""
        all_chunks = []

        for doc in documents:
            chunks = self.chunk_document(
                doc_id=doc.get('id', 'unknown'),
                title=doc.get('title', ''),
                content=doc.get('content', '')
            )
            all_chunks.extend(chunks)

        return all_chunks


class ChunkingStrategy:
    """
    Different chunking strategies for different use cases
    """

    @staticmethod
    def aggressive_chunking(
        content: str,
        chunk_size: int = 200,
        overlap: int = 30
    ) -> List[str]:
        """Small chunks for detailed search (more chunks, less context)"""
        chunker = SmartChunker(chunk_size=chunk_size, overlap=overlap)
        dummy_chunks = chunker.chunk_document("doc", "title", content)
        return [c.text for c in dummy_chunks]

    @staticmethod
    def balanced_chunking(
        content: str,
        chunk_size: int = 300,
        overlap: int = 50
    ) -> List[str]:
        """Medium chunks for balanced performance (default)"""
        chunker = SmartChunker(chunk_size=chunk_size, overlap=overlap)
        dummy_chunks = chunker.chunk_document("doc", "title", content)
        return [c.text for c in dummy_chunks]

    @staticmethod
    def conservative_chunking(
        content: str,
        chunk_size: int = 500,
        overlap: int = 100
    ) -> List[str]:
        """Large chunks for comprehensive context (fewer chunks, more context)"""
        chunker = SmartChunker(chunk_size=chunk_size, overlap=overlap)
        dummy_chunks = chunker.chunk_document("doc", "title", content)
        return [c.text for c in dummy_chunks]
