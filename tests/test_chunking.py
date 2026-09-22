"""
Unit tests for semantic and page-aware document chunking.
"""

import pytest
from app.ingestion.chunker import DocumentChunker

def test_chunker_generates_metadata_schema():
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=30)
    pages = [
        {
            "document": "test_paper.pdf",
            "file_path": "/path/to/test_paper.pdf",
            "page": 1,
            "total_pages": 2,
            "text": "1. Introduction\n\nRetrieval-Augmented Generation executes on edge devices using local vector stores."
        },
        {
            "document": "test_paper.pdf",
            "file_path": "/path/to/test_paper.pdf",
            "page": 2,
            "total_pages": 2,
            "text": "3. Methodology\n\nWe benchmark Snapdragon Hexagon NPU using INT4 quantization."
        }
    ]

    chunks = chunker.chunk_pages(pages)
    assert len(chunks) >= 2

    first_chunk = chunks[0]
    assert "chunk_id" in first_chunk
    assert first_chunk["document"] == "test_paper.pdf"
    assert first_chunk["page"] == 1
    assert "text" in first_chunk
    assert "char_count" in first_chunk
    assert first_chunk["char_count"] == len(first_chunk["text"])

def test_chunker_handles_empty_page():
    chunker = DocumentChunker()
    pages = [{"document": "empty.pdf", "page": 1, "text": "   "}]
    chunks = chunker.chunk_pages(pages)
    assert len(chunks) == 0
