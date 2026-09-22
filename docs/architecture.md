# System Architecture — ResearchPilot Edge

## 1. High-Level Modular Architecture

```text
                           ResearchPilot Edge
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
    Documents                    Research                   Hardware
    Ingestion                    RAG                        Detection
    Chunking                     Retrieval                  QNN / DirectML
    Embeddings                   Local LLM                  CPU SIMD
    FAISS Storage                Answer + Sources           Live Metrics
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                            Private Local AI
```

---

## 2. Component Pipeline & Data Flow

```mermaid
flowchart TD
    subgraph UI_Layer["🖥️ Desktop User Interface (Streamlit)"]
        UI_DASH["📊 Dashboard & Telemetry"]
        UI_DOCS["📂 Document Ingestion (PDF/TXT/DOCX)"]
        UI_CHAT["💬 Research Chat (Citation RAG)"]
        UI_SUMM["📝 Structured Summarizer"]
        UI_COMP["⚖️ Multi-Paper Comparison"]
        UI_BENCH["⚡ Hardware Benchmarking"]
        UI_PRIV["🔒 Privacy Hub"]
    end

    subgraph Core_Pipeline["⚙️ Core Pipeline (app/backend/, app/ingestion/, app/retrieval/)"]
        LOAD["DocumentLoader (Page Extraction)"]
        CLEAN["DocumentCleaner (Normalization & Headings)"]
        CHUNK["DocumentChunker (500-char Window + Metadata)"]
        EMBED["EmbeddingEngine (384-d Dense L2 Normalized)"]
        FAISS_DB["VectorStore (FAISS IndexFlatIP)"]
        HYBRID["HybridRetriever (Dense Similarity + BM25 Fusion)"]
    end

    subgraph Acceleration["⚡ Snapdragon & Hardware Acceleration (app/inference/)"]
        DEV["DeviceDetector (Real Hardware Telemetry)"]
        QNN["QNNExecutionProvider (Qualcomm Hexagon NPU)"]
        DML["DmlExecutionProvider (Qualcomm Adreno GPU)"]
        CPU_EP["CPUExecutionProvider (ARM64 NEON / x86_64)"]
        SYNTH["Deterministic Local Edge Synthesizer"]
    end

    UI_Layer --> Core_Pipeline
    Core_Pipeline --> Acceleration
    Acceleration --> DEV
```

---

## 3. Detailed Component Breakdown

### 3.1 Document Ingestion & Page-Aware Chunking (`app/ingestion/`)
- **`DocumentLoader`**: Extracts text page-by-page from PDF (via `pypdf`), TXT, and DOCX (`python-docx`).
- **`DocumentCleaner`**: Removes spurious whitespace, fixes broken hyphenations across line breaks, and preserves markdown headers.
- **`DocumentChunker`**: Generates 500-character semantic chunks with 80-character overlap, attaching rich citation metadata: `{"document": str, "page": int, "chunk_id": str, "section": str, "text": str}`.

### 3.2 Local Retrieval & Vector Storage (`app/retrieval/`)
- **`EmbeddingEngine`**: Generates 384-dimensional dense vectors using local models and deterministic edge vectorizers.
- **`VectorStore`**: Employs FAISS `IndexFlatIP` on normalized vectors for exact cosine similarity with disk persistence (`faiss_index.bin` & `chunks_metadata.json`).
- **`HybridRetriever`**: Fuses dense vector similarity with sparse BM25 term-frequency scores for precision on technical terms.

### 3.3 Hardware Acceleration & Inference (`app/inference/`)
- **`DeviceDetector`**: Real-time system inspection testing OS, ARM64 architecture, processor signature, and probing ONNX execution providers.
- **`QualcommAIHubInferenceEngine`**: Abstraction for Qualcomm AI Hub model integration and QNN compilation.
- **`ONNXInferenceEngine`**: Hardware-accelerated execution with provider priority: `QNNExecutionProvider` $\rightarrow$ `DmlExecutionProvider` $\rightarrow$ `CPUExecutionProvider`.
- **`DeterministicLocalInferenceEngine`**: Ultra-fast offline extractive NLP engine guaranteeing 100% offline uptime and anti-hallucination answers.
