"""
ResearchPilot Edge - Live Benchmarking & Snapdragon Diagnostics Component
Executes real-time latency, throughput, and hardware acceleration profiling.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from app.benchmarking.runner import BenchmarkRunner
from app.inference.device_detection import DeviceDetector

def render_benchmark():
    """Renders hardware benchmarking and NPU readiness diagnostics."""
    st.markdown("### ⚡ AI Performance Benchmarking & Snapdragon Profiling")
    st.markdown("Measure on-device latency, token throughput, vector indexing speed, and verified execution backends.")

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
        run_btn = st.button("🚀 Run Live Benchmark Suite", type="primary", use_container_width=True)
    with col_info:
        st.caption("Executes 5 benchmark workloads: Document Ingestion, Embeddings, Vector Retrieval, LLM Inference, and End-to-End RAG.")

    if run_btn:
        with st.spinner("Executing benchmark workloads and profiling system resources..."):
            runner = BenchmarkRunner()
            bench_results = runner.run_full_suite(sample_size=4)
            st.session_state.bench_results = bench_results
            st.success("Benchmark completed successfully! Results exported to `benchmarks/`")

    if "bench_results" in st.session_state:
        res = st.session_state.bench_results
        metrics = res["metrics"]
        hw = res["hardware"]

        st.markdown("---")
        st.markdown("#### 📈 Benchmark Summary Cards")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ing = metrics.get("document_ingestion", {})
            st.metric("Ingestion Speed", f"{ing.get('throughput_pages_per_sec', 0)} p/s", f"{ing.get('latency_ms', 0)} ms")
        with col2:
            emb = metrics.get("embeddings", {})
            st.metric("Embedding Speed", f"{emb.get('throughput_items_per_sec', 0)} ch/s", f"{emb.get('avg_latency_per_item_ms', 0)} ms/chunk")
        with col3:
            vr = metrics.get("vector_retrieval", {})
            st.metric("Vector Retrieval", f"{vr.get('avg_retrieval_latency_ms', 0)} ms", f"Min: {vr.get('min_retrieval_latency_ms', 0)} ms")
        with col4:
            inf = metrics.get("inference", {})
            st.metric("Inference Latency", f"{inf.get('avg_latency_ms', 0)} ms", f"{inf.get('avg_tokens_per_sec', 0)} tok/s")

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Visual Charts
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("##### ⏱️ Subsystem Latency Breakdown (ms)")
            latency_data = {
                "Subsystem": ["Doc Chunking", "Embedding (Batch)", "Vector Search", "LLM Inference", "End-to-End RAG"],
                "Latency (ms)": [
                    ing.get("latency_ms", 10),
                    emb.get("total_latency_ms", 15),
                    vr.get("avg_retrieval_latency_ms", 5),
                    inf.get("avg_latency_ms", 25),
                    metrics.get("end_to_end_rag", {}).get("avg_end_to_end_latency_ms", 45)
                ]
            }
            fig_lat = px.bar(
                latency_data,
                x="Subsystem",
                y="Latency (ms)",
                text_auto='.1f',
                color="Latency (ms)",
                color_continuous_scale="Blues"
            )
            fig_lat.update_layout(template="plotly_dark", height=320, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_lat, use_container_width=True)

        with col_c2:
            st.markdown("##### 💻 Hardware & Memory Footprint")
            hw_summary = pd.DataFrame([
                {"Metric": "Active Backend", "Value": hw["active_backend"]},
                {"Metric": "System Architecture", "Value": hw["architecture"].upper()},
                {"Metric": "Snapdragon Hardware", "Value": "✔ Verified SoC" if hw["is_snapdragon_detected"] else "x86_64 Host"},
                {"Metric": "Snapdragon NPU Ready", "Value": "✔ QNN Ready" if hw["snapdragon_npu_ready"] else "DirectML / SIMD Fallback"},
                {"Metric": "RAM Delta during Ingestion", "Value": f"{ing.get('ram_delta_mb', 0)} MB"},
                {"Metric": "Embedding Vector Dimension", "Value": str(emb.get("embedding_dimension", 384))},
            ])
            st.dataframe(hw_summary, use_container_width=True, hide_index=True)
