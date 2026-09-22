# Privacy & Local Data Sovereignty — ResearchPilot Edge

## 1. Core Privacy Architecture

ResearchPilot Edge is designed to prioritize data privacy and local execution:

- **Local Document Processing**: Ingestion, text extraction, chunking, and embedding generation occur strictly on the local machine.
- **No Mandatory Cloud API Dependency**: The application operates completely offline without requiring OpenAI, Anthropic, or external cloud API subscriptions.
- **Local Vector Storage**: Chunk vectors and metadata are stored in a local FAISS index on the host drive.
- **No Application-Level Telemetry by Default**: The core application does not transmit document contents, query prompts, or generated answers to remote cloud endpoints.
- **User Data Control**: Users retain full control to inspect, delete specific indexed files, or perform a complete local data purge at any time.

---

## 2. On-Device Boundary

```text
┌─────────────────────────────────────────────────────────────┐
│                 LOCAL HOST SECURITY BOUNDARY                │
│                                                             │
│   Uploaded Research Papers (PDF/TXT/DOCX)                   │
│         ↓                                                   │
│   Local Document Ingestion (pypdf, python-docx)             │
│         ↓                                                   │
│   Local Embedding Engine (all-MiniLM-L6-v2 ONNX)            │
│         ↓                                                   │
│   Local Vector Database (FAISS Flat Index)                  │
│         ↓                                                   │
│   Snapdragon / ONNX / Local LLM Inference Engine            │
│                                                             │
│   ✔ No application-level telemetry by default               │
│   ✔ Documents are processed locally                         │
│   ✔ No cloud API is required for core workflow              │
│   ✔ Local vector storage is used                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Transparency & Deletion

1. **Storage Locations**:
   - `data/uploads/`: Raw uploaded document files.
   - `data/vector_store/`: FAISS index binary (`faiss_index.bin`) and metadata JSON (`chunks_metadata.json`).
2. **Data Purging**: Users can click the **Data Purge** button in the Privacy Hub to permanently delete all uploaded files and index databases from the local filesystem.
