"""
Unit tests for document ingestion and text cleaning.
"""

import pytest
from pathlib import Path
import tempfile
from app.ingestion.loader import DocumentLoader
from app.ingestion.cleaner import DocumentCleaner

def test_cleaner_removes_whitespace_and_hyphens():
    cleaner = DocumentCleaner()
    dirty_text = "This is a multi-\nline word and    extra   spaces.\n\n\n\nNew paragraph."
    cleaned = cleaner.clean_text(dirty_text)
    
    assert "multiline" in cleaned
    assert "extra spaces." in cleaned
    assert "\n\n\n" not in cleaned

def test_cleaner_detects_headings():
    cleaner = DocumentCleaner()
    text = "ABSTRACT\nThis is the abstract.\n\n1. INTRODUCTION\nIntro content.\n\n3. METHODOLOGY\nMethod content."
    headings = cleaner.detect_headings(text)
    
    heading_names = [h[0] for h in headings]
    assert any("ABSTRACT" in h for h in heading_names)
    assert any("1. INTRODUCTION" in h for h in heading_names)
    assert any("3. METHODOLOGY" in h for h in heading_names)

def test_loader_parses_text_file():
    loader = DocumentLoader()
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("Section 1\nThis is a sample test document for ResearchPilot Edge.")
        temp_path = Path(f.name)

    try:
        pages = loader.load_document(temp_path)
        assert len(pages) >= 1
        assert "sample test document" in pages[0]["text"]
        assert pages[0]["page"] == 1
    finally:
        temp_path.unlink()

def test_loader_rejects_unsupported_format():
    loader = DocumentLoader()
    with tempfile.NamedTemporaryFile("w", suffix=".xyz", delete=False) as f:
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError):
            loader.load_document(temp_path)
    finally:
        temp_path.unlink()
