"""
Unit tests for local embedding generation.
"""

import numpy as np
from app.retrieval.embeddings import EmbeddingEngine

def test_embedding_engine_output_shape():
    engine = EmbeddingEngine(dimension=384)
    texts = [
        "Qualcomm Snapdragon Hexagon NPU acceleration.",
        "Local vector search with FAISS."
    ]
    embeddings = engine.encode(texts)

    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 384)
    assert embeddings.dtype == np.float32

def test_embedding_engine_l2_normalization():
    engine = EmbeddingEngine(dimension=384)
    embeddings = engine.encode(["Test embedding normalization"])
    
    norm = np.linalg.norm(embeddings[0])
    assert np.isclose(norm, 1.0, atol=1e-3)

def test_embedding_empty_input():
    engine = EmbeddingEngine(dimension=384)
    empty_vecs = engine.encode([])
    assert empty_vecs.shape == (0, 384)
