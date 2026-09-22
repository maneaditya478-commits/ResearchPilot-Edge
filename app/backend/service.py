"""
ResearchPilot Edge - Core RAG Orchestration Service
Coordinates document ingestion, vector storage, hybrid semantic retrieval, citation synthesis, and LLM inference.
"""

import time
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.core.config import (
    settings,
    UPLOADS_DIR,
    SAMPLE_PAPERS_DIR,
    VECTOR_STORE_DIR
)
from app.core.logger import logger
from app.ingestion.loader import DocumentLoader
from app.ingestion.chunker import DocumentChunker
from app.retrieval.embeddings import EmbeddingEngine
from app.retrieval.vector_store import VectorStore
from app.retrieval.hybrid_search import HybridRetriever
from app.inference import get_inference_engine, InferenceEngine, InferenceResult, DeviceDetector

class ResearchPilotService:
    """
    Unified application backend service.
    Orchestrates the complete offline edge RAG pipeline for research intelligence.
    """

    def __init__(self, backend_override: Optional[str] = None):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.embedding_engine = EmbeddingEngine()
        self.vector_store = VectorStore(
            storage_dir=VECTOR_STORE_DIR,
            embedding_engine=self.embedding_engine
        )
        self.retriever = HybridRetriever(self.vector_store)
        self.inference_engine: InferenceEngine = get_inference_engine(backend_override)
        
        # Telemetry & Metrics state
        self.query_history: List[Dict[str, Any]] = []
        self.total_queries = 0
        self.total_latency_ms = 0.0

    def set_inference_backend(self, backend_type: str):
        """Switches the active inference backend on the fly."""
        self.inference_engine = get_inference_engine(backend_type)
        logger.info(f"Switched active inference backend to: {self.inference_engine.backend_name}")

    def ingest_file(self, file_path: Path | str, save_copy: bool = True) -> Dict[str, Any]:
        """
        Ingests a PDF, TXT, or DOCX document into the local vector database.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        start_time = time.time()
        
        # Optionally copy to local uploads directory
        target_path = path
        if save_copy and path.parent != UPLOADS_DIR:
            target_path = UPLOADS_DIR / path.name
            shutil.copy2(path, target_path)

        # 1. Parse pages
        pages = self.loader.load_document(target_path)
        
        # 2. Semantic Chunking
        chunks = self.chunker.chunk_pages(pages)
        
        # 3. Vector Indexing
        added_count = self.vector_store.add_chunks(chunks)
        
        elapsed_sec = time.time() - start_time
        logger.info(f"Ingested '{path.name}': {len(pages)} pages, {added_count} chunks in {elapsed_sec:.2f}s")

        return {
            "document": path.name,
            "pages": len(pages),
            "chunks": added_count,
            "duration_sec": round(elapsed_sec, 3),
            "status": "Indexed"
        }

    def ingest_uploaded_file(self, filename: str, file_bytes: bytes) -> Dict[str, Any]:
        """Saves uploaded byte stream to local disk and triggers full ingestion."""
        dest_path = UPLOADS_DIR / filename
        with open(dest_path, "wb") as f:
            f.write(file_bytes)
        return self.ingest_file(dest_path, save_copy=False)

    def load_demo_dataset(self) -> List[Dict[str, Any]]:
        """Populates the system with pre-packaged synthetic research papers for instant judging demo."""
        results = []
        if not SAMPLE_PAPERS_DIR.exists():
            return results

        sample_files = list(SAMPLE_PAPERS_DIR.glob("*.txt")) + list(SAMPLE_PAPERS_DIR.glob("*.pdf")) + list(SAMPLE_PAPERS_DIR.glob("*.md"))
        for sample_file in sample_files:
            try:
                # Check if already indexed
                doc_name = sample_file.name
                existing = [d for d in self.vector_store.get_document_list() if d["document"] == doc_name]
                if not existing:
                    res = self.ingest_file(sample_file, save_copy=True)
                    results.append(res)
            except Exception as e:
                logger.error(f"Failed to ingest demo paper {sample_file.name}: {e}")

        return results

    def query_rag(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_document: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes citation-aware Retrieval-Augmented Generation (RAG).
        Returns synthesis answer, retrieved source citations with page numbers, and execution telemetry.
        """
        start_time = time.time()
        top_k = top_k or settings.top_k_retrieval
        
        # 1. Hybrid Retrieval
        retrieved_chunks = self.retriever.retrieve(query=query, top_k=top_k * 2)
        
        # Optional document filter
        if filter_document and filter_document != "All Documents":
            retrieved_chunks = [c for c in retrieved_chunks if c.get("document") == filter_document]
        
        selected_chunks = retrieved_chunks[:top_k]

        # 2. Build Context String
        context_blocks = []
        sources = []
        
        for idx, chunk in enumerate(selected_chunks, start=1):
            doc = chunk.get("document", "Unknown")
            page = chunk.get("page", 1)
            cid = chunk.get("chunk_id", f"c_{idx}")
            section = chunk.get("section", "General")
            score = chunk.get("similarity_score", 0.0)
            text_snippet = chunk.get("text", "").strip()

            context_blocks.append(
                f"[Source {idx} | Document: {doc} | Page: {page} | Section: {section}]\n{text_snippet}"
            )
            
            sources.append({
                "source_id": idx,
                "document": doc,
                "page": page,
                "section": section,
                "chunk_id": cid,
                "relevance_score": score,
                "snippet": text_snippet[:220] + "..." if len(text_snippet) > 220 else text_snippet,
                "full_text": text_snippet
            })

        combined_context = "\n\n".join(context_blocks)

        # 3. Local LLM / Engine Inference
        inference_result: InferenceResult = self.inference_engine.generate(
            prompt=query,
            context=combined_context,
            max_tokens=settings.max_generation_tokens,
            temperature=settings.temperature
        )

        total_latency_ms = round((time.time() - start_time) * 1000, 2)
        
        # 4. Update Telemetry
        self.total_queries += 1
        self.total_latency_ms += total_latency_ms

        response_payload = {
            "query": query,
            "answer": inference_result.text,
            "sources": sources,
            "tokens_generated": inference_result.tokens_generated,
            "inference_latency_ms": inference_result.latency_ms,
            "total_latency_ms": total_latency_ms,
            "tokens_per_sec": inference_result.tokens_per_sec,
            "backend_used": inference_result.backend_name,
            "model_used": self.inference_engine.model_name,
            "confidence_score": inference_result.confidence_score,
            "is_fallback": inference_result.is_fallback,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        self.query_history.append(response_payload)
        return response_payload

    def summarize_document(self, document_name: str) -> Dict[str, Any]:
        """Generates a structured scientific summary for a selected document."""
        chunks = self.vector_store.get_document_chunks(document_name)
        if not chunks:
            raise ValueError(f"No indexed content found for document: {document_name}")

        full_text = "\n\n".join([c["text"] for c in chunks])
        summary = self.inference_engine.summarize(
            document_text=full_text,
            document_name=document_name,
            max_tokens=600
        )
        return summary

    def compare_documents(self, document_names: List[str]) -> List[Dict[str, Any]]:
        """Generates a multi-document side-by-side comparison matrix."""
        if len(document_names) < 2:
            raise ValueError("Select at least 2 documents to generate comparison.")

        docs_payload = []
        for doc_name in document_names:
            chunks = self.vector_store.get_document_chunks(doc_name)
            combined = "\n\n".join([c["text"] for c in chunks])
            docs_payload.append({
                "document": doc_name,
                "text": combined
            })

        return self.inference_engine.compare(docs_payload)

    def search_chunks(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Direct semantic search across all indexed chunks."""
        return self.retriever.retrieve(query=query, top_k=top_k)

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Aggregates real-time operational metrics for dashboard visualization."""
        doc_list = self.vector_store.get_document_list()
        total_docs = len(doc_list)
        total_chunks = self.vector_store.total_chunks
        
        avg_latency = (
            round(self.total_latency_ms / self.total_queries, 1)
            if self.total_queries > 0
            else 0.0
        )

        sys_info = DeviceDetector.detect_system()

        return {
            "documents_count": total_docs,
            "chunks_count": total_chunks,
            "queries_count": self.total_queries,
            "avg_latency_ms": avg_latency,
            "active_backend": self.inference_engine.backend_name,
            "active_model": self.inference_engine.model_name,
            "offline_mode": settings.offline_mode,
            "system_hardware": sys_info,
            "documents": doc_list
        }

    def delete_document(self, document_name: str) -> int:
        """Removes a document from vector index and uploads cache."""
        deleted_chunks = self.vector_store.delete_document(document_name)
        
        # Delete upload file if present
        upload_file = UPLOADS_DIR / document_name
        if upload_file.exists():
            upload_file.unlink()

        return deleted_chunks

    def clear_all(self):
        """Clears all stored documents, vectors, and uploads."""
        self.vector_store.clear()
        for f in UPLOADS_DIR.glob("*"):
            if f.is_file() and f.name != ".gitkeep":
                f.unlink()
        self.query_history.clear()
        self.total_queries = 0
        self.total_latency_ms = 0.0
        logger.info("Cleared all documents and vector index.")

# Global service instance
service = ResearchPilotService()
