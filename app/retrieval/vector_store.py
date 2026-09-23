"""
ResearchPilot Edge - Local Vector Store
High-performance vector storage with FAISS and pure-NumPy fallback engine,
persistent metadata, and document-level indexing.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

# Try importing FAISS; if unavailable (e.g. on serverless Vercel / Linux without libgomp), fallback to NumPy
_FAISS_AVAILABLE = False
try:
    import faiss
    _FAISS_AVAILABLE = True
except Exception:
    _FAISS_AVAILABLE = False

from app.core.config import settings, VECTOR_STORE_DIR
from app.core.logger import logger
from app.retrieval.embeddings import EmbeddingEngine


class VectorStore:
    """
    Local vector database supporting FAISS IndexFlatIP with automatic
    pure-NumPy cosine similarity fallback for serverless & edge environments.
    """

    INDEX_FILENAME = "faiss_index.bin"
    NUMPY_VECTORS_FILENAME = "vectors.npy"
    METADATA_FILENAME = "chunks_metadata.json"

    def __init__(self, storage_dir: Path = None, embedding_engine: EmbeddingEngine = None):
        self.storage_dir = Path(storage_dir or VECTOR_STORE_DIR)
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.dimension = self.embedding_engine.dimension
        
        self.index_path = self.storage_dir / self.INDEX_FILENAME
        self.npy_path = self.storage_dir / self.NUMPY_VECTORS_FILENAME
        self.metadata_path = self.storage_dir / self.METADATA_FILENAME
        
        self.use_faiss = _FAISS_AVAILABLE
        self.faiss_index: Optional[Any] = None
        self.numpy_vectors: Optional[np.ndarray] = None
        self.metadata: List[Dict[str, Any]] = []
        
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Loads existing index & metadata from disk or creates new empty index."""
        # 1. Load metadata if present
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}")
                self.metadata = []

        # 2. Try loading FAISS index if FAISS is available
        if self.use_faiss and self.index_path.exists():
            try:
                self.faiss_index = faiss.read_index(str(self.index_path))
                logger.info(f"Loaded FAISS vector index ({self.faiss_index.ntotal} vectors)")
                return
            except Exception as e:
                logger.warning(f"FAISS load failed ({e}), falling back to NumPy matrix")

        # 3. Try loading NumPy matrix if present
        if self.npy_path.exists():
            try:
                self.numpy_vectors = np.load(str(self.npy_path)).astype(np.float32)
                logger.info(f"Loaded NumPy vector matrix ({len(self.numpy_vectors)} vectors)")
                return
            except Exception as e:
                logger.warning(f"NumPy vector matrix load failed: {e}")

        # 4. Initialize fresh index
        if self.use_faiss:
            try:
                self.faiss_index = faiss.IndexFlatIP(self.dimension)
                logger.info(f"Initialized new FAISS IndexFlatIP (dim={self.dimension})")
            except Exception:
                self.use_faiss = False
                self.numpy_vectors = np.empty((0, self.dimension), dtype=np.float32)
        else:
            self.numpy_vectors = np.empty((0, self.dimension), dtype=np.float32)
            logger.info(f"Initialized pure-NumPy vector store (dim={self.dimension})")

    def _save(self):
        """Persists vector representations and chunk metadata to disk."""
        try:
            # Save FAISS index
            if self.use_faiss and self.faiss_index is not None:
                try:
                    faiss.write_index(self.faiss_index, str(self.index_path))
                except Exception:
                    pass

            # Save NumPy matrix
            if self.numpy_vectors is not None and len(self.numpy_vectors) > 0:
                try:
                    np.save(str(self.npy_path), self.numpy_vectors)
                except Exception:
                    pass

            # Save metadata
            try:
                with open(self.metadata_path, "w", encoding="utf-8") as f:
                    json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Vector store persistence notice: {e}")

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

        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)

        # Add to FAISS index if active
        if self.use_faiss and self.faiss_index is not None:
            try:
                self.faiss_index.add(embeddings)
            except Exception as e:
                logger.warning(f"FAISS add failed ({e}), falling back to NumPy")
                self.use_faiss = False

        # Add to NumPy matrix
        if self.numpy_vectors is None or len(self.numpy_vectors) == 0:
            self.numpy_vectors = embeddings
        else:
            self.numpy_vectors = np.vstack([self.numpy_vectors, embeddings])

        self.metadata.extend(chunks)
        self._save()

        logger.info(f"Added {len(chunks)} chunks. Total chunks in store: {self.total_chunks}")
        return len(chunks)

    def search(self, query: str, top_k: int = None, min_similarity: float = None) -> List[Dict[str, Any]]:
        """
        Searches the vector index for chunks semantically matching the query.
        Returns: list of chunks with attached 'similarity_score' and 'rank'.
        """
        total = self.total_chunks
        if total == 0:
            return []

        top_k = top_k or settings.top_k_retrieval
        min_similarity = min_similarity if min_similarity is not None else settings.similarity_threshold

        query_vec = self.embedding_engine.encode([query])
        query_vec = np.ascontiguousarray(query_vec, dtype=np.float32)

        k = min(top_k, total)

        # FAISS search path
        if self.use_faiss and self.faiss_index is not None:
            try:
                scores, indices = self.faiss_index.search(query_vec, k)
                scores = scores[0]
                indices = indices[0]
            except Exception:
                # Fallback to NumPy calculation below
                self.use_faiss = False
                scores, indices = self._numpy_search(query_vec, k)
        else:
            scores, indices = self._numpy_search(query_vec, k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores, indices), start=1):
            if idx < 0 or idx >= len(self.metadata):
                continue
            
            float_score = float(score)
            if float_score < min_similarity and len(results) >= 1:
                continue

            chunk_meta = dict(self.metadata[idx])
            chunk_meta["similarity_score"] = round(float_score, 4)
            chunk_meta["rank"] = rank
            results.append(chunk_meta)

        return results

    def _numpy_search(self, query_vec: np.ndarray, k: int):
        """Pure NumPy cosine similarity ranking (dot product of L2 normalized vectors)."""
        if self.numpy_vectors is None or len(self.numpy_vectors) == 0:
            return [], []

        # Inner product between matrix (N, D) and query (1, D)
        sims = np.dot(self.numpy_vectors, query_vec.T).squeeze(-1)
        # Top-k indices
        if k >= len(sims):
            top_indices = np.argsort(-sims)
        else:
            top_indices = np.argpartition(-sims, k)[:k]
            top_indices = top_indices[np.argsort(-sims[top_indices])]

        top_scores = sims[top_indices]
        return top_scores, top_indices

    def delete_document(self, doc_name: str) -> int:
        """
        Deletes all chunks belonging to a document and rebuilds index.
        Returns number of deleted chunks.
        """
        remaining_chunks = [c for c in self.metadata if c.get("document") != doc_name]
        deleted_count = len(self.metadata) - len(remaining_chunks)

        if deleted_count > 0:
            self.clear()
            if remaining_chunks:
                self.add_chunks(remaining_chunks)
            logger.info(f"Deleted {deleted_count} chunks for document: {doc_name}")

        return deleted_count

    def clear(self):
        """Clears all vectors and metadata."""
        if self.use_faiss:
            try:
                self.faiss_index = faiss.IndexFlatIP(self.dimension)
            except Exception:
                self.use_faiss = False
        self.numpy_vectors = np.empty((0, self.dimension), dtype=np.float32)
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
        if self.use_faiss and self.faiss_index is not None:
            return self.faiss_index.ntotal
        elif self.numpy_vectors is not None:
            return len(self.numpy_vectors)
        return len(self.metadata)
