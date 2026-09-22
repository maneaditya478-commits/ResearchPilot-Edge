"""
ResearchPilot Edge - Local Vector Store
High-performance FAISS vector storage with persistent metadata and document-level indexing.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import faiss

from app.core.config import settings, VECTOR_STORE_DIR
from app.core.logger import logger
from app.retrieval.embeddings import EmbeddingEngine

class VectorStore:
    """
    FAISS-powered local vector database with disk persistence,
    document-aware metadata indexing, and similarity search.
    """

    INDEX_FILENAME = "faiss_index.bin"
    METADATA_FILENAME = "chunks_metadata.json"

    def __init__(self, storage_dir: Path = None, embedding_engine: EmbeddingEngine = None):
        self.storage_dir = Path(storage_dir or VECTOR_STORE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.dimension = self.embedding_engine.dimension
        
        self.index_path = self.storage_dir / self.INDEX_FILENAME
        self.metadata_path = self.storage_dir / self.METADATA_FILENAME
        
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []
        
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Loads existing FAISS index & metadata from disk or creates new empty index."""
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded existing vector index with {self.index.ntotal} vectors from {self.storage_dir}")
                return
            except Exception as e:
                logger.error(f"Failed to load vector store from disk ({e}). Rebuilding new index.")

        # Create new Inner Product index for cosine similarity over normalized vectors
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        self._save()
        logger.info(f"Initialized new FAISS IndexFlatIP (dim={self.dimension})")

    def _save(self):
        """Persists FAISS binary index and chunk metadata to disk."""
        try:
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved vector index ({self.index.ntotal} vectors) to disk.")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            raise

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Embeds and indexes document chunks.
        Returns total number of chunks added.
        """
        if not chunks:
            return 0

        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_engine.encode(texts)

        if embeddings.shape[0] == 0:
            return 0

        # Ensure float32 and 2D
        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)

        # Add to FAISS index
        self.index.add(embeddings)
        self.metadata.extend(chunks)
        self._save()

        logger.info(f"Added {len(chunks)} chunks to vector index. Total chunks: {self.index.ntotal}")
        return len(chunks)

    def search(self, query: str, top_k: int = None, min_similarity: float = None) -> List[Dict[str, Any]]:
        """
        Searches the vector index for chunks semantically matching the query.
        Returns: list of chunks with attached 'similarity_score' and 'rank'.
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        top_k = top_k or settings.top_k_retrieval
        min_similarity = min_similarity if min_similarity is not None else settings.similarity_threshold

        query_vec = self.embedding_engine.encode([query])
        query_vec = np.ascontiguousarray(query_vec, dtype=np.float32)

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_vec, k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
            if idx < 0 or idx >= len(self.metadata):
                continue
            
            float_score = float(score)
            if float_score < min_similarity and len(results) >= 1:
                # Discard low-confidence tail if we have at least 1 match
                continue

            chunk_meta = dict(self.metadata[idx])
            chunk_meta["similarity_score"] = round(float_score, 4)
            chunk_meta["rank"] = rank
            results.append(chunk_meta)

        return results

    def delete_document(self, doc_name: str) -> int:
        """
        Deletes all chunks belonging to a document and rebuilds index.
        Returns number of deleted chunks.
        """
        remaining_chunks = [c for c in self.metadata if c.get("document") != doc_name]
        deleted_count = len(self.metadata) - len(remaining_chunks)

        if deleted_count > 0:
            # Rebuild index from remaining chunks
            self.clear()
            if remaining_chunks:
                self.add_chunks(remaining_chunks)
            logger.info(f"Deleted {deleted_count} chunks for document: {doc_name}")

        return deleted_count

    def clear(self):
        """Clears all vectors and metadata."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        self._save()
        logger.info("Vector store cleared.")

    def get_document_list(self) -> List[Dict[str, Any]]:
        """Returns aggregated summary of all ingested documents."""
        docs_map = {}
        for chunk in self.metadata:
            doc = chunk.get("document", "Unknown")
            page = chunk.get("page", 1)
            char_count = chunk.get("char_count", 0)

            if doc not in docs_map:
                docs_map[doc] = {
                    "document": doc,
                    "file_path": chunk.get("file_path", ""),
                    "chunk_count": 0,
                    "page_count": 0,
                    "pages_seen": set(),
                    "total_chars": 0
                }
            docs_map[doc]["chunk_count"] += 1
            docs_map[doc]["pages_seen"].add(page)
            docs_map[doc]["total_chars"] += char_count

        summary_list = []
        for doc_name, info in docs_map.items():
            summary_list.append({
                "document": doc_name,
                "file_path": info["file_path"],
                "chunk_count": info["chunk_count"],
                "page_count": len(info["pages_seen"]),
                "total_chars": info["total_chars"]
            })
        return summary_list

    def get_document_chunks(self, doc_name: str) -> List[Dict[str, Any]]:
        """Returns all chunks belonging to a specific document ordered by page and chunk."""
        return [c for c in self.metadata if c.get("document") == doc_name]

    @property
    def total_chunks(self) -> int:
        return self.index.ntotal if self.index else 0
