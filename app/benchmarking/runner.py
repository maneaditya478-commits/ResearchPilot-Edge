"""
ResearchPilot Edge - Benchmark Runner
Executes comprehensive automated benchmarks across ingestion, embedding, vector retrieval, and LLM inference.
"""

import time
import json
import csv
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

from app.core.config import BENCHMARKS_DIR
from app.core.logger import logger
from app.benchmarking.profiler import HardwareProfiler
from app.ingestion.loader import DocumentLoader
from app.ingestion.chunker import DocumentChunker
from app.retrieval.embeddings import EmbeddingEngine
from app.retrieval.vector_store import VectorStore
from app.inference import get_inference_engine, DeviceDetector

class BenchmarkRunner:
    """
    Executes benchmark suites measuring latency, throughput, memory consumption,
    and actual hardware acceleration backends.
    """

    def __init__(self, output_dir: Path = None):
        self.output_dir = Path(output_dir or BENCHMARKS_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.profiler = HardwareProfiler()
        self.sys_info = DeviceDetector.detect_system()

    def run_full_suite(self, sample_size: int = 5) -> Dict[str, Any]:
        """
        Runs comprehensive benchmark suite across all subsystem components.
        """
        logger.info("Starting ResearchPilot Edge Benchmark Suite...")
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "hardware": self.sys_info,
            "metrics": {}
        }

        # 1. Benchmark Document Processing & Chunking
        logger.info("1/5 Benchmarking Document Ingestion & Chunking...")
        ingest_metrics = self._benchmark_ingestion()
        results["metrics"]["document_ingestion"] = ingest_metrics

        # 2. Benchmark Embedding Throughput
        logger.info("2/5 Benchmarking Embedding Generation...")
        embed_metrics = self._benchmark_embeddings(sample_size=sample_size)
        results["metrics"]["embeddings"] = embed_metrics

        # 3. Benchmark Vector Retrieval Latency
        logger.info("3/5 Benchmarking Vector Store Retrieval...")
        retrieval_metrics = self._benchmark_retrieval(sample_size=sample_size)
        results["metrics"]["vector_retrieval"] = retrieval_metrics

        # 4. Benchmark Local AI Inference
        logger.info("4/5 Benchmarking Local AI Inference...")
        inference_metrics = self._benchmark_inference(iterations=sample_size)
        results["metrics"]["inference"] = inference_metrics

        # 5. Benchmark End-to-End RAG Pipeline
        logger.info("5/5 Benchmarking End-to-End RAG Pipeline...")
        rag_metrics = self._benchmark_rag_pipeline(iterations=sample_size)
        results["metrics"]["end_to_end_rag"] = rag_metrics

        # Save to disk
        self._export_results(results)
        logger.info(f"Benchmark Suite completed. Results saved to {self.output_dir}")
        return results

    def _benchmark_ingestion(self) -> Dict[str, Any]:
        """Measures text cleaning and chunking throughput."""
        chunker = DocumentChunker()
        sample_pages = [
            {
                "document": "benchmark_paper.pdf",
                "page": i,
                "total_pages": 10,
                "text": (
                    f"Section {i}: Edge AI Acceleration on Snapdragon NPU. "
                    "Qualcomm Snapdragon X Elite architecture integrates Hexagon NPU capable of 45 TOPS. "
                    "In this experiment, we evaluate local retrieval-augmented generation and quantization "
                    "profiles across on-device transformer models. " * 8
                )
            }
            for i in range(1, 11)
        ]

        self.profiler.start()
        start = time.time()
        chunks = chunker.chunk_pages(sample_pages)
        duration_ms = (time.time() - start) * 1000
        prof = self.profiler.stop()

        total_chars = sum(len(p["text"]) for p in sample_pages)
        return {
            "total_pages_processed": len(sample_pages),
            "total_chunks_created": len(chunks),
            "total_characters": total_chars,
            "latency_ms": round(duration_ms, 2),
            "throughput_pages_per_sec": round(len(sample_pages) / max(0.001, duration_ms / 1000), 1),
            "throughput_chars_per_sec": round(total_chars / max(0.001, duration_ms / 1000), 1),
            "ram_delta_mb": prof["ram_delta_mb"]
        }

    def _benchmark_embeddings(self, sample_size: int = 5) -> Dict[str, Any]:
        """Measures embedding latency and batch throughput."""
        engine = EmbeddingEngine()
        sample_texts = [
            f"Qualcomm Snapdragon Hexagon NPU acceleration delivers high energy efficiency for edge AI NLP query {i}."
            for i in range(sample_size * 4)
        ]

        self.profiler.start()
        start = time.time()
        vecs = engine.encode(sample_texts, batch_size=16)
        duration_ms = (time.time() - start) * 1000
        prof = self.profiler.stop()

        return {
            "backend": engine.backend_name,
            "embedding_dimension": engine.dimension,
            "total_texts_embedded": len(sample_texts),
            "total_latency_ms": round(duration_ms, 2),
            "avg_latency_per_item_ms": round(duration_ms / len(sample_texts), 2),
            "throughput_items_per_sec": round(len(sample_texts) / max(0.001, duration_ms / 1000), 1),
            "ram_delta_mb": prof["ram_delta_mb"]
        }

    def _benchmark_retrieval(self, sample_size: int = 5) -> Dict[str, Any]:
        """Measures vector search latency against indexed chunks."""
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        vstore = VectorStore(storage_dir=temp_dir)
        
        # Populate test chunks
        test_chunks = [
            {
                "chunk_id": f"bench_chunk_{i:03d}",
                "document": f"bench_doc_{i%3}.pdf",
                "page": (i % 5) + 1,
                "section": "Experiments",
                "text": f"Experimental evaluation of Snapdragon NPU direct memory access and quantization speedup factor {i}."
            }
            for i in range(50)
        ]
        vstore.add_chunks(test_chunks)

        queries = [
            "Snapdragon NPU memory access",
            "Quantization speedup factor",
            "Experimental evaluation results",
            "Direct memory transfer latency",
            "Hexagon accelerator performance"
        ]

        latencies = []
        for q in queries[:sample_size]:
            s = time.time()
            vstore.search(q, top_k=4)
            latencies.append((time.time() - s) * 1000)

        # Cleanup
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except Exception:
            pass

        return {
            "total_indexed_chunks": len(test_chunks),
            "queries_executed": len(latencies),
            "avg_retrieval_latency_ms": round(float(np.mean(latencies)), 2),
            "min_retrieval_latency_ms": round(float(np.min(latencies)), 2),
            "max_retrieval_latency_ms": round(float(np.max(latencies)), 2)
        }

    def _benchmark_inference(self, iterations: int = 3) -> Dict[str, Any]:
        """Measures local inference time and generation throughput."""
        engine = get_inference_engine()
        prompt = "What are the primary advantages of Qualcomm Hexagon NPU for edge RAG applications?"
        context = (
            "The Qualcomm Hexagon NPU delivers dedicated 45 TOPS tensor computing for Snapdragon X Elite devices. "
            "It provides zero cloud latency, high privacy, and ultra-low thermal dissipation compared to standard CPUs."
        )

        latencies = []
        token_rates = []

        for _ in range(iterations):
            self.profiler.start()
            res = engine.generate(prompt=prompt, context=context, max_tokens=256)
            prof = self.profiler.stop()

            latencies.append(res.latency_ms)
            token_rates.append(res.tokens_per_sec)

        return {
            "model_name": engine.model_name,
            "backend_name": engine.backend_name,
            "iterations": iterations,
            "avg_latency_ms": round(float(np.mean(latencies)), 2),
            "avg_tokens_per_sec": round(float(np.mean(token_rates)), 1),
            "is_hardware_accelerated": "NPU" in engine.backend_name or "DirectML" in engine.backend_name or "CUDA" in engine.backend_name
        }

    def _benchmark_rag_pipeline(self, iterations: int = 3) -> Dict[str, Any]:
        """Measures end-to-end composite query latency."""
        from app.backend.service import ResearchPilotService
        test_service = ResearchPilotService()
        
        # Ingest a small synthetic paper
        sample_pages = [
            {
                "document": "e2e_rag_bench.pdf",
                "page": 1,
                "total_pages": 1,
                "text": "Qualcomm Snapdragon NPU powers on-device private document intelligence and offline RAG."
            }
        ]
        chunks = test_service.chunker.chunk_pages(sample_pages)
        test_service.vector_store.add_chunks(chunks)

        e2e_latencies = []
        for _ in range(iterations):
            s = time.time()
            res = test_service.query_rag("How does Snapdragon NPU power offline RAG?")
            e2e_latencies.append((time.time() - s) * 1000)

        # Clean test chunk
        test_service.vector_store.delete_document("e2e_rag_bench.pdf")

        return {
            "iterations": iterations,
            "avg_end_to_end_latency_ms": round(float(np.mean(e2e_latencies)), 2),
            "min_latency_ms": round(float(np.min(e2e_latencies)), 2),
            "max_latency_ms": round(float(np.max(e2e_latencies)), 2)
        }

    def _export_results(self, results: Dict[str, Any]):
        """Exports benchmark metrics to JSON and CSV formats."""
        json_path = self.output_dir / "benchmark_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        csv_path = self.output_dir / "benchmark_results.csv"
        rows = []
        for component, metrics in results["metrics"].items():
            if isinstance(metrics, dict):
                for metric_name, value in metrics.items():
                    rows.append({
                        "Timestamp": results["timestamp"],
                        "Component": component,
                        "Metric": metric_name,
                        "Value": str(value),
                        "Active Backend": results["hardware"]["active_backend"],
                        "Architecture": results["hardware"]["architecture"]
                    })

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Timestamp", "Component", "Metric", "Value", "Active Backend", "Architecture"])
            writer.writeheader()
            writer.writerows(rows)
