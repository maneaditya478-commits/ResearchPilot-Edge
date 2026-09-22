"""
ResearchPilot Edge - Document Chunker
Splits documents into semantically coherent chunks with citation-grade metadata.
"""

import re
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logger import logger
from app.ingestion.cleaner import DocumentCleaner

class DocumentChunker:
    """
    Slices documents into windowed text segments with full metadata preservation
    for precise RAG retrieval and citation referencing.
    """

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.cleaner = DocumentCleaner()

    def chunk_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes a list of page objects and segments each into structured chunks.
        
        Chunk schema:
        {
            "chunk_id": "paper_p001_c001",
            "document": "paper.pdf",
            "file_path": "...",
            "page": 1,
            "total_pages": 12,
            "section": "Abstract",
            "text": "...",
            "char_count": 480
        }
        """
        all_chunks = []
        current_section = "General"

        for page_data in pages:
            doc_name = page_data["document"]
            page_num = page_data["page"]
            total_pages = page_data.get("total_pages", 1)
            file_path = page_data.get("file_path", "")
            raw_text = page_data["text"]

            if not raw_text.strip():
                continue

            # Detect headings on this page to update active section context
            headings = self.cleaner.detect_headings(raw_text)
            
            # Split text by paragraph boundaries
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            
            # Build sliding chunks
            chunk_buffer = []
            chunk_char_count = 0
            page_chunk_index = 1

            for para in paragraphs:
                # Check if paragraph is a section header
                for h_title, _ in headings:
                    if para.startswith(h_title[:20]):
                        current_section = h_title
                        break

                para_len = len(para)

                # If single paragraph exceeds chunk size, split it with overlap
                if para_len > self.chunk_size:
                    if chunk_buffer:
                        chunk_text = "\n\n".join(chunk_buffer)
                        chunk_id = f"{self._sanitize_name(doc_name)}_p{page_num:03d}_c{page_chunk_index:03d}"
                        all_chunks.append({
                            "chunk_id": chunk_id,
                            "document": doc_name,
                            "file_path": file_path,
                            "page": page_num,
                            "total_pages": total_pages,
                            "section": current_section,
                            "text": chunk_text,
                            "char_count": len(chunk_text),
                        })
                        page_chunk_index += 1
                        chunk_buffer = []
                        chunk_char_count = 0

                    # Sub-chunk the oversized paragraph
                    start = 0
                    while start < para_len:
                        end = min(start + self.chunk_size, para_len)
                        sub_text = para[start:end].strip()
                        if sub_text:
                            chunk_id = f"{self._sanitize_name(doc_name)}_p{page_num:03d}_c{page_chunk_index:03d}"
                            all_chunks.append({
                                "chunk_id": chunk_id,
                                "document": doc_name,
                                "file_path": file_path,
                                "page": page_num,
                                "total_pages": total_pages,
                                "section": current_section,
                                "text": sub_text,
                                "char_count": len(sub_text),
                            })
                            page_chunk_index += 1
                        start += (self.chunk_size - self.chunk_overlap)
                    continue

                if chunk_char_count + para_len > self.chunk_size and chunk_buffer:
                    chunk_text = "\n\n".join(chunk_buffer)
                    chunk_id = f"{self._sanitize_name(doc_name)}_p{page_num:03d}_c{page_chunk_index:03d}"
                    all_chunks.append({
                        "chunk_id": chunk_id,
                        "document": doc_name,
                        "file_path": file_path,
                        "page": page_num,
                        "total_pages": total_pages,
                        "section": current_section,
                        "text": chunk_text,
                        "char_count": len(chunk_text),
                    })
                    page_chunk_index += 1

                    # Retain last paragraph for contextual overlap if small enough
                    if len(chunk_buffer[-1]) <= self.chunk_overlap:
                        chunk_buffer = [chunk_buffer[-1], para]
                        chunk_char_count = len(chunk_buffer[0]) + para_len
                    else:
                        chunk_buffer = [para]
                        chunk_char_count = para_len
                else:
                    chunk_buffer.append(para)
                    chunk_char_count += para_len

            # Flush remaining buffer for this page
            if chunk_buffer:
                chunk_text = "\n\n".join(chunk_buffer)
                chunk_id = f"{self._sanitize_name(doc_name)}_p{page_num:03d}_c{page_chunk_index:03d}"
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "document": doc_name,
                    "file_path": file_path,
                    "page": page_num,
                    "total_pages": total_pages,
                    "section": current_section,
                    "text": chunk_text,
                    "char_count": len(chunk_text),
                })

        logger.info(f"Chunked into {len(all_chunks)} semantic chunks.")
        return all_chunks

    def _sanitize_name(self, filename: str) -> str:
        """Sanitizes filename for clean ID generation."""
        clean = re.sub(r'[^a-zA-Z0-9_]', '_', filename)
        return clean[:24].rstrip('_')
