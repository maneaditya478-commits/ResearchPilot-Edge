"""
Unit tests for benchmark execution and metric serialization (JSON, CSV, MD).
"""

import tempfile
import shutil
from pathlib import Path
from app.benchmarking.runner import BenchmarkRunner

def test_benchmark_runner_full_suite():
    temp_dir = Path(tempfile.mkdtemp())
    try:
        runner = BenchmarkRunner(output_dir=temp_dir)
        results = runner.run_full_suite(sample_size=2)

        assert "timestamp" in results
        assert "hardware" in results
        assert "metrics" in results

        metrics = results["metrics"]
        assert "document_ingestion" in metrics
        assert "embeddings" in metrics
        assert "vector_retrieval" in metrics
        assert "model_loading" in metrics
        assert "inference" in metrics
        assert "end_to_end_rag" in metrics

        # Verify export files exist
        assert (temp_dir / "benchmark_results.json").exists()
        assert (temp_dir / "benchmark_results.csv").exists()
        assert (temp_dir / "benchmark_report.md").exists()

    finally:
        shutil.rmtree(temp_dir)
