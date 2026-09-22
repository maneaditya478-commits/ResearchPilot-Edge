"""
ResearchPilot Edge - Document Loader
Extracts text and page-level metadata from PDF, TXT, and DOCX research documents.
"""

from pathlib import Path
from typing import List, Dict, Any
import pypdf
from app.core.logger import logger
from app.ingestion.cleaner import DocumentCleaner

class DocumentLoader:
    """Loads and parses diverse document formats into structured page-level entities."""

    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx", ".md"}

    def __init__(self):
        self.cleaner = DocumentCleaner()

    def load_document(self, file_path: str | Path) -> List[Dict[str, Any]]:
        """
        Loads a document and returns a list of page/section dictionaries:
        [
            {
                "document": "paper.pdf",
                "page": 1,
                "text": "...",
                "char_count": 1200
            },
            ...
        ]
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found at path: {path}")

        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format: {suffix}. Supported: {self.SUPPORTED_EXTENSIONS}")

        logger.info(f"Loading document: {path.name} ({path.stat().st_size / 1024:.1f} KB)")

        if suffix == ".pdf":
            return self._load_pdf(path)
        elif suffix == ".docx":
            return self._load_docx(path)
        elif suffix in (".txt", ".md"):
            return self._load_text(path)
        else:
            raise ValueError(f"No handler configured for {suffix}")

    def _load_pdf(self, path: Path) -> List[Dict[str, Any]]:
        """Extracts text page-by-page from PDF files."""
        pages = []
        try:
            reader = pypdf.PdfReader(str(path))
            total_pages = len(reader.pages)
            
            for idx, page in enumerate(reader.pages):
                raw_text = page.extract_text() or ""
                cleaned_text = self.cleaner.clean_text(raw_text)
                
                # If page has extractable text, record it
                if cleaned_text.strip():
                    pages.append({
                        "document": path.name,
                        "file_path": str(path),
                        "page": idx + 1,
                        "total_pages": total_pages,
                        "text": cleaned_text,
                        "char_count": len(cleaned_text),
                    })
            
            # Fallback if PDF was image-only or empty
            if not pages:
                pages.append({
                    "document": path.name,
                    "file_path": str(path),
                    "page": 1,
                    "total_pages": 1,
                    "text": f"[PDF: {path.name} contains no extractable text stream]",
                    "char_count": 0,
                })
                
        except Exception as e:
            logger.error(f"Error parsing PDF {path.name}: {e}")
            raise RuntimeError(f"Corrupted or unreadable PDF: {e}")

        logger.info(f"Successfully loaded {len(pages)} pages from PDF: {path.name}")
        return pages

    def _load_docx(self, path: Path) -> List[Dict[str, Any]]:
        """Extracts text from DOCX files."""
        try:
            import docx
            doc = docx.Document(str(path))
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text)
            
            combined_text = self.cleaner.clean_text("\n\n".join(full_text))
            
            # Estimate logical pages (approx 2500 chars per standard academic page)
            page_size = 2500
            pages = []
            if len(combined_text) <= page_size:
                pages.append({
                    "document": path.name,
                    "file_path": str(path),
                    "page": 1,
                    "total_pages": 1,
                    "text": combined_text,
                    "char_count": len(combined_text)
                })
            else:
                chunks = [combined_text[i:i + page_size] for i in range(0, len(combined_text), page_size)]
                for idx, chunk in enumerate(chunks):
                    pages.append({
                        "document": path.name,
                        "file_path": str(path),
                        "page": idx + 1,
                        "total_pages": len(chunks),
                        "text": chunk,
                        "char_count": len(chunk)
                    })
            return pages
        except Exception as e:
            logger.error(f"Error parsing DOCX {path.name}: {e}")
            raise RuntimeError(f"Could not read DOCX document: {e}")

    def _load_text(self, path: Path) -> List[Dict[str, Any]]:
        """Extracts text from raw TXT/MD files."""
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            
            cleaned = self.cleaner.clean_text(content)
            page_size = 2500
            pages = []
            
            if len(cleaned) <= page_size:
                pages.append({
                    "document": path.name,
                    "file_path": str(path),
                    "page": 1,
                    "total_pages": 1,
                    "text": cleaned,
                    "char_count": len(cleaned)
                })
            else:
                chunks = [cleaned[i:i + page_size] for i in range(0, len(cleaned), page_size)]
                for idx, chunk in enumerate(chunks):
                    pages.append({
                        "document": path.name,
                        "file_path": str(path),
                        "page": idx + 1,
                        "total_pages": len(chunks),
                        "text": chunk,
                        "char_count": len(chunk)
                    })
            return pages
        except Exception as e:
            logger.error(f"Error parsing TXT {path.name}: {e}")
            raise RuntimeError(f"Could not read text document: {e}")
