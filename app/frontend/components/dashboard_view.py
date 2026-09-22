"""
ResearchPilot Edge - Dashboard View Component
Displays real-time hardware telemetry, documents index stats, inference latency, and query metrics.
"""

import streamlit as st
import pandas as pd
from app.backend.service import service

def render_dashboard():
    """Renders high-level operational metrics and system telemetry."""
    metrics = service.get_dashboard_metrics()
    hw = metrics["system_hardware"]

    st.markdown("### 📊 System Overview & Operational Metrics")
    
    # Row 1: Core Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">📄 Documents Indexed</div>
                <div class="metric-value">{metrics['documents_count']}</div>
                <div class="metric-sub">Across {metrics['chunks_count']} semantic chunks</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">⚡ Execution Backend</div>
                <div class="metric-value" style="font-size: 16px; margin-top: 6px;">{metrics['active_backend']}</div>
                <div class="metric-sub">Architecture: {hw['architecture'].upper()}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">⏱️ Avg Query Latency</div>
                <div class="metric-value">{metrics['avg_latency_ms']} ms</div>
                <div class="metric-sub">{metrics['queries_count']} total queries executed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        offline_status = "● OFFLINE READY" if metrics["offline_mode"] else "● CONNECTED"
        color = "#10b981" if metrics["offline_mode"] else "#3b82f6"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">🔒 Security & Network</div>
                <div class="metric-value" style="color: {color}; font-size: 18px;">{offline_status}</div>
                <div class="metric-sub">Zero telemetry egress</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Row 2: Hardware Profile & Acceleration Status
    col_hw, col_actions = st.columns([2, 1])

    with col_hw:
        st.markdown("#### 💻 Detected Host Hardware")
        hw_df = pd.DataFrame([
            {"Parameter": "Host Operating System", "Detected Value": f"{hw['os']} {hw['os_release']}"},
            {"Parameter": "Processor Platform", "Detected Value": hw['processor']},
            {"Parameter": "CPU Architecture", "Detected Value": hw['architecture'].upper()},
            {"Parameter": "Available System RAM", "Detected Value": f"{hw['available_ram_gb']} GB / {hw['total_ram_gb']} GB"},
            {"Parameter": "CPU Cores", "Detected Value": f"{hw['cpu_physical_cores']} Physical / {hw['cpu_logical_cores']} Logical"},
            {"Parameter": "Snapdragon Hardware", "Detected Value": "✔ Qualcomm SoC Verified" if hw['is_snapdragon_detected'] else "x86_64 Host Platform"},
            {"Parameter": "Snapdragon NPU Acceleration", "Detected Value": "✔ QNN Execution Provider Ready" if hw['snapdragon_npu_ready'] else "DirectML / Multi-Threaded SIMD Fallback"},
            {"Parameter": "Active ONNX Providers", "Detected Value": ", ".join(hw['onnx_execution_providers']) or "CPU"},
        ])
        st.dataframe(hw_df, use_container_width=True, hide_index=True)

    with col_actions:
        st.markdown("#### 🚀 Quick Actions")
        
        if st.button("✨ Load Demo Research Papers", use_container_width=True):
            with st.spinner("Ingesting pre-packaged sample papers..."):
                added = service.load_demo_dataset()
                if added:
                    st.success(f"Indexed {len(added)} demo research papers!")
                else:
                    st.info("Demo papers already indexed.")
            st.rerun()

        if st.button("🔄 Refresh Hardware Telemetry", use_container_width=True):
            st.rerun()

        if st.button("🗑️ Clear All Indexed Data", use_container_width=True):
            service.clear_all()
            st.warning("Vector store and uploaded documents cleared.")
            st.rerun()

    # Row 3: Recent Queries
    if service.query_history:
        st.markdown("---")
        st.markdown("#### 📜 Recent Research Inquiries")
        history_data = []
        for q in reversed(service.query_history[-5:]):
            history_data.append({
                "Timestamp": q.get("timestamp"),
                "Query": q.get("query"),
                "Latency (ms)": q.get("total_latency_ms"),
                "Sources": len(q.get("sources", [])),
                "Backend": q.get("backend_used")
            })
        st.dataframe(pd.DataFrame(history_data), use_container_width=True, hide_index=True)
