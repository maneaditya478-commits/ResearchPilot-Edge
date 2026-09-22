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
    print(" ResearchPilot Edge -- Performance Benchmark Suite")
    print("=" * 70)

    runner = BenchmarkRunner()
    results = runner.run_full_suite(sample_size=args.sample_size)

    hw = results["hardware"]
    m = results["metrics"]

    # Extract metrics for standardized summary
    emb_lat = m.get("embeddings", {}).get("avg_latency_per_item_ms", "N/A")
    ret_lat = m.get("vector_retrieval", {}).get("avg_retrieval_latency_ms", "N/A")
    ttft = m.get("inference", {}).get("time_to_first_token_ms", "N/A")
    tps = m.get("inference", {}).get("avg_tokens_per_sec", "N/A")
    rag_lat = m.get("end_to_end_rag", {}).get("avg_end_to_end_latency_ms", "N/A")

    val_status = "Snapdragon NPU Verified" if hw.get("snapdragon_npu_ready") else "Requires Snapdragon hardware validation"

    print("\n" + "=" * 40)
    print("ResearchPilot Edge Snapdragon Report")
    print("=" * 40)
    print(f"Hardware: {hw['os']} ({hw['os_release']})")
    print(f"Architecture: {hw['architecture'].upper()}")
    print(f"Processor: {hw['processor']}")
    print(f"QNN Provider: {hw.get('qnn_provider_installed', 'UNAVAILABLE')}")
    print(f"QNN Model Execution: {hw.get('qnn_model_execution', 'UNAVAILABLE')}")
    print(f"DirectML: {hw.get('directml_provider_installed', 'UNAVAILABLE')}")
    print(f"CPU: {hw.get('cpu_provider_installed', 'AVAILABLE')}")
    print(f"Embedding: {emb_lat} ms/chunk")
    print(f"Retrieval: {ret_lat} ms")
    print(f"TTFT: {ttft} ms")
    print(f"Tokens/sec: {tps}")
    print(f"Total RAG Latency: {rag_lat} ms")
    print(f"RAM: {hw['total_ram_gb']} GB")
    print(f"CPU: {hw['cpu_physical_cores']} physical / {hw['cpu_logical_cores']} logical cores")
    print(f"Validation Status: {val_status}")
    print("=" * 40)

    print(f"\nBenchmark reports saved to:")
    print(f"  JSON: benchmarks/benchmark_results.json")
    print(f"  CSV:  benchmarks/benchmark_results.csv")
    print(f"  MD:   benchmarks/benchmark_report.md")

if __name__ == "__main__":
    main()
