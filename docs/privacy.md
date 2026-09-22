# Privacy & Offline Security Architecture — ResearchPilot Edge

## 1. Core Security Principle

> **"User documents should remain on the user's computer whenever possible."**

ResearchPilot Edge is architected from the ground up to eliminate cloud transmission vulnerabilities:

```text
┌─────────────────────────────────────────────────────────────┐
│                 HOST PC SECURITY BOUNDARY                   │
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
│   ❌ ZERO External API Telemetry                            │
│   ❌ ZERO Remote Cloud Transmission                         │
│   ❌ ZERO Third-Party Data Retention                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Security Guarantees & Verification

1. **Air-Gapped Operation**: Once models are cached locally, ResearchPilot Edge requires zero active internet connection.
2. **Local Storage Transparency**:
   - Uploads stored in `data/uploads/` (User local directory).
   - Vector index stored in `data/vector_store/faiss_index.bin`.
   - Chunk metadata stored in `data/vector_store/chunks_metadata.json`.
3. **Data Deletion Rights**: Users can instantly delete individual documents or trigger an **Emergency Data Purge** to erase all vectors and uploads from memory and disk.
4. **Zero Cloud API Mandatory Dependencies**: Works without OpenAI, Anthropic, Google, or any remote subscription.
