# ResearchPilot Edge — Performance Benchmark Report

**Generated**: 2026-09-23 12:51:19  
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
| **Document Ingestion** | Throughput | 5960.4 | pages/sec |
| **Document Ingestion** | Character Rate | 12736093.2 | chars/sec |
| **Embedding Generation** | Average Latency | 0.08 | ms/chunk |
| **Embedding Generation** | Throughput | 12690.8 | chunks/sec |
| **Vector Retrieval** | Average Latency | 0.28 | ms/query |
| **Model Loading** | Backend Init Time | 0.001 | seconds |
| **LLM Inference** | Time To First Token (TTFT) | 5.0 | ms |
| **LLM Inference** | Generation Speed | 10000.0 | tokens/sec |
| **Complete RAG** | Retrieval Latency | 0.0 | ms |
| **Complete RAG** | Inference Latency | 5.0 | ms |
| **Complete RAG** | Total End-to-End Latency | 0.82 | ms |

---

## Memory & System Telemetry

- **Total System RAM**: 13.86 GB
- **Available System RAM**: 3.45 GB
- **Physical CPU Cores**: 8
- **Logical CPU Cores**: 16
- **Available ONNX Providers**: AzureExecutionProvider, CPUExecutionProvider
