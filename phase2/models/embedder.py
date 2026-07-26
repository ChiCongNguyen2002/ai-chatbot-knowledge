"""
Phase 2 - Embedding Model Manager
Lightweight wrapper for sentence-transformers embeddings
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np


class EmbedderManager:
    """
    Manage embedding model lifecycle
    - Load model once
    - Batch encode efficiently
    - Handle encoding errors
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model

        Args:
            model_name: HuggingFace model ID
                - "all-MiniLM-L6-v2": 22MB, 384-dim (fast, good quality)
                - "all-mpnet-base-v2": 438MB, 768-dim (slower, better quality)
                - For production: use all-mpnet-base-v2
                - For demo: use all-MiniLM-L6-v2
        """
        self.model_name = model_name
        self.model = None

    def load(self) -> None:
        """Load model from HuggingFace hub"""
        if self.model is None:
            print(f"[Embedder] Loading {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            print(f"[Embedder] Model loaded. Dimension: {self.model.get_sentence_embedding_dimension()}")

    def embed(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Embed texts to vectors

        Args:
            texts: Single text or list of texts
            batch_size: Process in batches for memory efficiency

        Returns:
            NumPy array of embeddings
        """
        if self.model is None:
            self.load()

        # Convert single text to list
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True
        )

        return embeddings

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Alias for embed() for clarity when processing batches"""
        return self.embed(texts, batch_size=batch_size)

    def get_dimension(self) -> int:
        """Get embedding dimension"""
        if self.model is None:
            self.load()
        return self.model.get_sentence_embedding_dimension()

    def similarity_cosine(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: Vector [d,]
            embedding2: Vector [d,]

        Returns:
            Similarity score [0, 1]
        """
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        # Normalize to [0, 1] from [-1, 1]
        return (similarity + 1) / 2
