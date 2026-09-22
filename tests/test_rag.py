"""
Unit and integration tests for RAG pipeline, multi-chunk synthesis, anti-hallucination, and citation accuracy.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from app.backend.service import ResearchPilotService
from app.retrieval.vector_store import VectorStore
from app.retrieval.hybrid_search import HybridRetriever

@pytest.fixture
def isolated_rag_service():
    temp_dir = Path(tempfile.mkdtemp())
    service = ResearchPilotService(backend_override="fallback")
    service.vector_store = VectorStore(storage_dir=temp_dir, embedding_engine=service.embedding_engine)
    service.retriever = HybridRetriever(service.vector_store)
    yield service
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

def test_rag_query_with_citations(isolated_rag_service):
    service = isolated_rag_service
    test_pages = [
        {
            "document": "quantum_rag.pdf",
            "page": 4,
            "total_pages": 8,
            "text": "The quantum error correction model uses surface codes with a code distance of d=5."
        }
    ]
    chunks = service.chunker.chunk_pages(test_pages)
    service.vector_store.add_chunks(chunks)

    response = service.query_rag("What code distance is used in the quantum error correction model?")
    
    assert "answer" in response
    assert "sources" in response
    assert len(response["sources"]) >= 1
    
    src = response["sources"][0]
    assert src["document"] == "quantum_rag.pdf"
    assert src["page"] == 4
    assert "d=5" in response["answer"] or "surface codes" in response["answer"]

def test_rag_multi_chunk_synthesis(isolated_rag_service):
    service = isolated_rag_service
    test_pages = [
        {
            "document": "multi_part.pdf",
            "page": 1,
            "total_pages": 2,
            "text": "The experiments utilized the SQuAD 2.0 benchmark for evaluation."
        },
        {
            "document": "multi_part.pdf",
            "page": 2,
            "total_pages": 2,
            "text": "Results showed a 4.2x energy efficiency improvement on the Hexagon NPU."
        }
    ]
    chunks = service.chunker.chunk_pages(test_pages)
    service.vector_store.add_chunks(chunks)

    response = service.query_rag("What benchmark was used and what energy efficiency was achieved?")
    assert len(response["sources"]) >= 1
    assert "energy efficiency" in response["answer"].lower() or "squad" in response["answer"].lower()

def test_rag_hallucination_safe_when_not_found(isolated_rag_service):
    service = isolated_rag_service
    test_pages = [
        {
            "document": "botany.pdf",
            "page": 1,
            "total_pages": 1,
            "text": "Photosynthesis produces glucose and oxygen from carbon dioxide and water."
        }
    ]
    chunks = service.chunker.chunk_pages(test_pages)
    service.vector_store.add_chunks(chunks)

    # Question completely unrelated to botany
    response = service.query_rag("What is the maximum torque of the electric aircraft rotor?")
    
    # Anti-hallucination check: must state information could not be found or not present
    assert "could not be found" in response["answer"].lower() or "not present" in response["answer"].lower() or "no direct relevant" in response["answer"].lower()

def test_rag_handles_empty_library(isolated_rag_service):
    service = isolated_rag_service
    service.vector_store.clear()
    
    response = service.query_rag("How does NPU acceleration work?")
    assert "answer" in response
    assert len(response["sources"]) == 0
    assert "no direct relevant context" in response["answer"].lower() or "not found" in response["answer"].lower()
