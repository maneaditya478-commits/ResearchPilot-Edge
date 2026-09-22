"""
ResearchPilot Edge - Main Application User Interface
Desktop-grade Streamlit application for Snapdragon-optimized AI document intelligence and RAG.
"""

import streamlit as st
from pathlib import Path
import sys

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings
from app.frontend.styles import CUSTOM_CSS
from app.backend.service import service
from app.inference.device_detection import DeviceDetector
from app.frontend.components import (
    render_dashboard,
    render_documents,
    render_chat,
    render_summary,
    render_compare,
    render_search,
    render_benchmark,
    render_privacy,
)

# Streamlit Page Setup
st.set_page_config(
    page_title="ResearchPilot Edge — Private AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom Styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def main():
    # Detect System Telemetry
    sys_info = DeviceDetector.detect_system()

    # Top Hero Header
    backend_badge = sys_info["active_backend"]
    npu_badge = "SNAPDRAGON NPU (QNN)" if sys_info["snapdragon_npu_ready"] else f"ARCH: {sys_info['architecture'].upper()}"
    offline_badge = "OFFLINE AIR-GAPPED" if settings.offline_mode else "ONLINE"

    st.markdown(
        f"""
        <div class="hero-banner">
            <div class="hero-title">
                <span>🔬 ResearchPilot Edge</span>
            </div>
            <div class="hero-tagline">
                Private AI Research Assistant That Works Where Your Data Is. Designed for Snapdragon HP PCs.
            </div>
            <div class="badge-row">
                <span class="badge badge-offline">● {offline_badge}</span>
                <span class="badge badge-snapdragon">⚡ {npu_badge}</span>
                <span class="badge badge-backend">⚙️ {backend_badge}</span>
                <span class="badge badge-privacy">🛡️ 100% LOCAL STORAGE</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar Configuration
    with st.sidebar:
        st.markdown("### ⚙️ Engine Settings")
        
        backend_choices = ["Auto-Detect", "ONNX Runtime", "Transformers (Local)", "Qualcomm AI Hub", "Fallback Synthesizer"]
        current_choice = st.selectbox(
            "Inference Backend:",
            backend_choices,
            index=0,
            help="Select the local execution provider or let the system auto-detect the fastest available backend."
        )

        mapping = {
            "Auto-Detect": "auto",
            "ONNX Runtime": "onnx",
            "Transformers (Local)": "transformers",
            "Qualcomm AI Hub": "qualcomm",
            "Fallback Synthesizer": "fallback"
        }
        selected_backend_key = mapping[current_choice]
        if st.session_state.get("last_backend_key") != selected_backend_key:
            service.set_inference_backend(selected_backend_key)
            st.session_state.last_backend_key = selected_backend_key

        st.markdown("---")
        st.markdown("### 💻 Hardware Telemetry")
        st.caption(f"**OS**: {sys_info['os']} ({sys_info['os_release']})")
        st.caption(f"**CPU**: {sys_info['processor'][:24]}")
        st.caption(f"**RAM**: {sys_info['available_ram_gb']} GB free / {sys_info['total_ram_gb']} GB")
        st.caption(f"**Snapdragon**: {'✔ Verified' if sys_info['is_snapdragon_detected'] else 'x86_64 / Other'}")
        st.caption(f"**NPU Acceleration**: {'✔ QNN Ready' if sys_info['snapdragon_npu_ready'] else 'DirectML / CPU'}")

        st.markdown("---")
        st.markdown("### 📖 About Challenge")
        st.caption(
            "Submitted to **Snapdragon AI Lab Build & Present Challenge**.\n"
            "Brings private document intelligence and RAG inference to Snapdragon-powered HP PCs."
        )

    # Navigation Tabs
    tabs = st.tabs([
        "📊 Dashboard",
        "📂 Documents",
        "💬 Research Chat",
        "📝 Summarize",
        "⚖️ Compare Papers",
        "🔍 Semantic Search",
        "⚡ Benchmarking & Hardware",
        "🔒 Privacy Hub"
    ])

    with tabs[0]:
        render_dashboard()

    with tabs[1]:
        render_documents()

    with tabs[2]:
        render_chat()

    with tabs[3]:
        render_summary()

    with tabs[4]:
        render_compare()

    with tabs[5]:
        render_search()

    with tabs[6]:
        render_benchmark()

    with tabs[7]:
        render_privacy()

if __name__ == "__main__":
    main()
