"""
Unit and integration tests for RAG pipeline and citation generation.
"""

import pytest
from app.backend.service import ResearchPilotService

def test_rag_query_with_citations():
    service = ResearchPilotService(backend_override="fallback")
    
    # Ingest test chunks
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

    try:
        response = service.query_rag("What code distance is used in the quantum error correction model?")
        
        assert "answer" in response
        assert "sources" in response
        assert len(response["sources"]) >= 1
        
        src = response["sources"][0]
        assert src["document"] == "quantum_rag.pdf"
        assert src["page"] == 4
        assert "chunk_id" in src
        assert "latency_ms" in str(response)

    finally:
        service.vector_store.delete_document("quantum_rag.pdf")

def test_rag_handles_empty_library():
    service = ResearchPilotService(backend_override="fallback")
    service.vector_store.clear()
    
    response = service.query_rag("How does NPU acceleration work?")
    assert "answer" in response
    assert len(response["sources"]) == 0
