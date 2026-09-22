"""
Unit tests for FAISS local vector store.
"""

import tempfile
import shutil
from pathlib import Path
from app.retrieval.vector_store import VectorStore
from app.retrieval.embeddings import EmbeddingEngine

def test_vector_store_add_and_search():
    temp_dir = Path(tempfile.mkdtemp())
    try:
        engine = EmbeddingEngine(dimension=384)
        store = VectorStore(storage_dir=temp_dir, embedding_engine=engine)

        sample_chunks = [
            {
                "chunk_id": "c1",
                "document": "snapdragon_paper.pdf",
                "page": 1,
                "text": "Snapdragon Hexagon NPU delivers 45 TOPS of AI acceleration."
            },
            {
                "chunk_id": "c2",
                "document": "biology_paper.pdf",
                "page": 3,
                "text": "Photosynthesis occurs in plant chloroplasts using sunlight."
            }
        ]

        added = store.add_chunks(sample_chunks)
        assert added == 2
        assert store.total_chunks == 2

        # Search for AI acceleration
        results = store.search("Snapdragon NPU performance", top_k=2)
        assert len(results) >= 1
        assert results[0]["document"] == "snapdragon_paper.pdf"
        assert "similarity_score" in results[0]
        assert results[0]["similarity_score"] > 0

    finally:
        shutil.rmtree(temp_dir)

def test_vector_store_delete_document():
    temp_dir = Path(tempfile.mkdtemp())
    try:
        store = VectorStore(storage_dir=temp_dir)
        store.add_chunks([
            {"chunk_id": "c1", "document": "docA.pdf", "page": 1, "text": "Content A"},
            {"chunk_id": "c2", "document": "docB.pdf", "page": 1, "text": "Content B"}
        ])

        assert store.total_chunks == 2
        deleted = store.delete_document("docA.pdf")
        assert deleted == 1
        assert store.total_chunks == 1
        assert store.metadata[0]["document"] == "docB.pdf"
    finally:
        shutil.rmtree(temp_dir)
