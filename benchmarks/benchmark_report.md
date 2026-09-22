# ResearchPilot Edge — Performance Benchmark Report

**Generated**: 2026-09-22 20:29:00  
**Platform**: Windows (11)  
**Architecture**: AMD64  
**Processor**: AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD  
**Active Backend**: ONNX Runtime (x86_64 SIMD CPU)  
**Snapdragon NPU Status**: Requires Snapdragon hardware validation  
**DirectML Acceleration**: UNAVAILABLE  

---

## Subsystem Performance Metrics

| Subsystem Component | Metric | Measured Value | Unit |
| :--- | :--- | :--- | :--- |
| **Document Ingestion** | Throughput | 5675.6 | pages/sec |
| **Document Ingestion** | Character Rate | 12127725.0 | chars/sec |
| **Embedding Generation** | Average Latency | 0.06 | ms/chunk |
| **Embedding Generation** | Throughput | 12000.0 | chunks/sec |
| **Vector Retrieval** | Average Latency | 0.08 | ms/query |
| **Model Loading** | Backend Init Time | 0.001 | seconds |
| **LLM Inference** | Time To First Token (TTFT) | 5.0 | ms |
| **LLM Inference** | Generation Speed | 13000.0 | tokens/sec |
| **Complete RAG** | Retrieval Latency | 0.0 | ms |
| **Complete RAG** | Inference Latency | 5.0 | ms |
| **Complete RAG** | Total End-to-End Latency | 0.84 | ms |

---

## Memory & System Telemetry

- **Total System RAM**: 13.86 GB
- **Available System RAM**: 1.86 GB
- **Physical CPU Cores**: 8
- **Logical CPU Cores**: 16
- **Available ONNX Providers**: AzureExecutionProvider, CPUExecutionProvider
