"""
ResearchPilot Edge - CLI Benchmarking Utility
Run performance benchmarks across document ingestion, vector retrieval, and local inference.

Usage:
    python scripts/benchmark.py [--sample-size 5]
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.benchmarking.runner import BenchmarkRunner
from app.core.logger import logger

def main():
    parser = argparse.ArgumentParser(description="ResearchPilot Edge Benchmark Suite")
    parser.add_argument("--sample-size", type=int, default=5, help="Number of samples/iterations per test")
    args = parser.parse_args()

    print("=" * 70)
    print(" ResearchPilot Edge — Snapdragon AI Lab Challenge Benchmark Suite")
    print("=" * 70)

    runner = BenchmarkRunner()
    results = runner.run_full_suite(sample_size=args.sample_size)

    print("\n--- System & Hardware Detection ---")
    hw = results["hardware"]
    print(f"OS: {hw['os']} ({hw['os_release']}) | Arch: {hw['architecture']}")
    print(f"Processor: {hw['processor']}")
    print(f"Detected Active Backend: {hw['active_backend']}")
    print(f"Snapdragon NPU Ready: {'YES' if hw['snapdragon_npu_ready'] else 'NO (Requires Qualcomm QNN EP / Snapdragon Target)'}")
    print(f"Available ONNX Providers: {', '.join(hw['onnx_execution_providers'])}")

    print("\n--- Benchmark Summary Metrics ---")
    metrics = results["metrics"]
    
    if "document_ingestion" in metrics:
        ing = metrics["document_ingestion"]
        print(f"[Ingestion]  {ing['throughput_pages_per_sec']} pages/sec ({ing['latency_ms']} ms for {ing['total_pages_processed']} pages)")
    
    if "embeddings" in metrics:
        emb = metrics["embeddings"]
        print(f"[Embedding]  {emb['avg_latency_per_item_ms']} ms/chunk ({emb['throughput_items_per_sec']} chunks/sec)")
        print(f"             Backend: {emb['backend']}")
    
    if "vector_retrieval" in metrics:
        vr = metrics["vector_retrieval"]
        print(f"[Retrieval]  Avg: {vr['avg_retrieval_latency_ms']} ms | Min: {vr['min_retrieval_latency_ms']} ms")
    
    if "inference" in metrics:
        inf = metrics["inference"]
        print(f"[Inference]  Avg Latency: {inf['avg_latency_ms']} ms | Tokens/sec: {inf['avg_tokens_per_sec']}")
        print(f"             Model: {inf['model_name']} | Backend: {inf['backend_name']}")
    
    if "end_to_end_rag" in metrics:
        rag = metrics["end_to_end_rag"]
        print(f"[End-to-End] Avg Total Latency: {rag['avg_end_to_end_latency_ms']} ms")

    print("\n" + "=" * 70)
    print(f"Detailed logs exported to:")
    print(f"  JSON: benchmarks/benchmark_results.json")
    print(f"  CSV:  benchmarks/benchmark_results.csv")
    print("=" * 70)

if __name__ == "__main__":
    main()
