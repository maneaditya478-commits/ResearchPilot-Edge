"""
ResearchPilot Edge - Privacy & Offline Security Hub
Provides local storage transparency, data sovereignty verification, and local cache management.
"""

import streamlit as st
import os
from pathlib import Path
import pandas as pd
from app.core.config import UPLOADS_DIR, VECTOR_STORE_DIR, DATA_DIR
from app.backend.service import service

def render_privacy():
    """Renders privacy transparency report and local storage inspector."""
    st.markdown("### 🔒 Privacy & Offline Architecture Hub")
    st.markdown("ResearchPilot Edge enforces complete data sovereignty: your research documents never leave your PC.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="summary-section">
                <div class="summary-heading" style="color: #10b981;">🛡️ Architectural Privacy Guarantees</div>
                <div class="summary-body">
                    <ul>
                        <li><b>Zero Mandatory Cloud Egress</b>: All text extraction, chunking, embedding generation, and LLM inference execute locally on the host device.</li>
                        <li><b>Local Vector Database</b>: Vectors are stored in a local binary FAISS flat index on the host SSD.</li>
                        <li><b>No External API Telemetry</b>: Does not transmit documents to OpenAI, Anthropic, Google, or any remote server.</li>
                        <li><b>Complete User Deletion Rights</b>: You can instantly purge any individual document or clear the entire database.</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="summary-section">
                <div class="summary-heading" style="color: #38bdf8;">⚙️ On-Device Security Boundary</div>
                <div class="summary-body">
                    <ul>
                        <li><b>Air-Gapped Operation</b>: Operates seamlessly in offline mode without internet connection.</li>
                        <li><b>Local Sandboxed Processing</b>: Document parsing runs in standard user-space memory.</li>
                        <li><b>Traceable Citations</b>: Every generative output links directly to on-disk chunk offsets to prevent hallucination.</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### 📁 Local File Storage Inspector")
    
    # Calculate storage sizes
    def get_dir_size(path: Path) -> int:
        return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())

    uploads_size = get_dir_size(UPLOADS_DIR)
    vector_size = get_dir_size(VECTOR_STORE_DIR)
    
    storage_df = pd.DataFrame([
        {
            "Storage Location": "Uploads Directory (`data/uploads`)",
            "File Count": len(list(UPLOADS_DIR.glob("*"))),
            "Disk Size": f"{uploads_size / 1024:.2f} KB",
            "Privacy Level": "Encrypted Local Storage"
        },
        {
            "Storage Location": "Vector Store (`data/vector_store`)",
            "File Count": len(list(VECTOR_STORE_DIR.glob("*"))),
            "Disk Size": f"{vector_size / 1024:.2f} KB",
            "Privacy Level": "Binary Vector Index (Local)"
        }
    ])
    st.dataframe(storage_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    if st.button("🗑️ Emergency Data Purge (Delete All Documents & Indices)", type="primary"):
        service.clear_all()
        st.success("All local uploads, vector indices, and conversation histories have been completely purged.")
        st.rerun()
