# Demo & Evaluation Guide — Snapdragon AI Lab Challenge

This walkthrough guide is prepared for challenge judges and evaluators to test **ResearchPilot Edge** end-to-end in under 3 minutes.

---

## 🚀 3-Minute Quick Demo Walkthrough

### Step 1: Launch Application
```powershell
python run.py --demo
```
This automatically pre-loads the 3 sample edge AI research papers and opens the desktop interface in your browser at `http://localhost:8501`.

---

### Step 2: Explore Dashboard
1. Open the **📊 Dashboard** tab.
2. Observe the real-time operational cards:
   - **Documents Indexed**: 3 documents across 45 semantic chunks.
   - **Execution Backend**: Verified hardware backend.
   - **Security**: ● OFFLINE READY.
   - **Detected Host Hardware**: System processor, memory, and ONNX execution providers.

---

### Step 3: Interactive Research Chat with Citations
1. Open the **💬 Research Chat** tab.
2. Click any of the sample prompt pills or type:
   > *"What methodology and hardware was used on Snapdragon X Elite?"*
3. Observe:
   - Instant grounded response.
   - **Verified Source Citations**: Document name (`paper_1_snapdragon_npu_acceleration.txt`), page numbers, and chunk ID.
   - Expand the citation accordion to inspect the exact retrieved text segment.
   - Telemetry badge showing latency and token throughput.

---

### Step 4: Structured Scientific Document Summarizer
1. Open the **📝 Summarize** tab.
2. Select `paper_1_snapdragon_npu_acceleration.txt`.
3. Click **🚀 Generate Summary**.
4. Review the structured sections:
   - *Abstract & Research Question*
   - *Methodology & Architecture*
   - *Evaluation Dataset*
   - *Key Results (45 TOPS NPU, 38.6 tok/s, 4.2x energy efficiency)*
   - *Limitations & Future Work*
5. Click **📥 Export as Markdown** or **JSON**.

---

### Step 5: Side-by-Side Paper Comparison
1. Open the **⚖️ Compare Papers** tab.
2. Select all 3 indexed papers.
3. Click **🚀 Generate Comparison Matrix**.
4. Review the comparative table across: *Objective*, *Architecture*, *Dataset*, *Results*, *Hardware Acceleration*, and *Limitations*.
5. Export as CSV or Markdown.

---

### Step 6: Live Benchmarking & Hardware Profiling
1. Open the **⚡ Benchmarking & Hardware** tab.
2. Click **🚀 Run Live Benchmark Suite**.
3. View real-time latency graphs, pages/sec ingestion throughput, and memory profiling.

---

### Step 7: Local Privacy & Storage Inspection
1. Open the **🔒 Privacy Hub** tab.
2. Inspect local storage sizes for `data/uploads/` and `data/vector_store/`.
3. Verify that zero network requests were made to external cloud servers.
