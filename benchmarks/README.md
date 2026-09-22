# ResearchPilot Edge — Performance Benchmarking

This directory contains automated benchmark definitions, metric calculation scripts, and serialized telemetry results (`benchmark_results.json`, `benchmark_results.csv`).

---

## 1. Benchmarked Subsystems & Metrics

The benchmark suite tests five operational tiers of the on-device RAG architecture:

| Subsystem | Metric | Unit | Description |
| :--- | :--- | :--- | :--- |
| **Document Ingestion** | Throughput | `pages/sec`, `chars/sec` | Page-aware text cleaning, heading detection, and sliding window chunking |
| **Embedding Generation** | Latency & Rate | `ms/chunk`, `chunks/sec` | Dense vector extraction via ONNX Runtime / local models |
| **Vector Retrieval** | Latency | `ms/query` | FAISS Inner Product search across all indexed chunks |
| **LLM Inference** | TTFT & Speed | `ms`, `tokens/sec` | Local generative inference / structured extractive synthesis |
| **End-to-End RAG** | Composite Latency | `ms` | Full query turnaround from user prompt to citation-grounded response |

---

## 2. Hardware Acceleration Profiles

ResearchPilot Edge automatically profiles the host system and labels execution without fabricating hardware states:

- **Snapdragon Hexagon NPU (`QNNExecutionProvider`)**: Dedicated 45 TOPS tensor cores via Qualcomm QNN execution provider on Snapdragon X Elite / Plus laptops.
- **Windows DirectML (`DmlExecutionProvider`)**: Hardware-accelerated GPU / NPU execution on Windows.
- **ARM64 NEON / x86_64 CPU (`CPUExecutionProvider`)**: Optimized multi-threaded vector SIMD execution.
- **Deterministic Edge Synthesizer**: High-speed local fallback ensuring zero-lag offline operation.

---

## 3. Running Benchmarks

### Via CLI
```powershell
# Run with 5 sample iterations per test
python scripts/benchmark.py --sample-size 5
```

### Via Interactive Web Dashboard
1. Launch the UI: `python run.py`
2. Navigate to the **⚡ Benchmarking & Hardware** tab.
3. Click **🚀 Run Live Benchmark Suite**.

---

## 4. Benchmark Artifacts
- `benchmark_results.json`: Full structured telemetry dump including hardware specifications and timing breakdowns.
- `benchmark_results.csv`: Flat tabular export for spreadsheet analysis and challenge presentation slides.
