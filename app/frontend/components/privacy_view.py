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
    st.markdown("### 🔒 Privacy & Local Data Sovereignty Hub")
    st.markdown("ResearchPilot Edge is built to keep your research documents on your local computer.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="summary-section">
                <div class="summary-heading" style="color: #10b981;">🛡️ Architectural Privacy Guarantees</div>
                <div class="summary-body">
                    <ul>
                        <li><b>No application-level telemetry by default</b>: Your documents and queries are not sent to any remote monitoring servers.</li>
                        <li><b>Documents are processed locally</b>: Ingestion, parsing, and chunking happen entirely in memory on this machine.</li>
                        <li><b>No cloud API is required for core workflow</b>: Operates independently of external cloud subscriptions.</li>
                        <li><b>Local vector storage is used</b>: Vectors and citations are stored strictly in local application files.</li>
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
                        <li><b>Offline Capability</b>: The core RAG workflow functions when offline without active network connectivity.</li>
                        <li><b>User Data Deletion</b>: You can remove individual documents or trigger a full data purge at any time.</li>
                        <li><b>Verifiable Citations</b>: Generated answers link to on-disk chunk offsets for factual traceability.</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### 📁 Local File Storage Inspector")
    
    def get_dir_size(path: Path) -> int:
        return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())

    uploads_size = get_dir_size(UPLOADS_DIR)
    vector_size = get_dir_size(VECTOR_STORE_DIR)
    
    storage_df = pd.DataFrame([
        {
            "Storage Location": "Uploads Directory (`data/uploads`)",
            "File Count": len(list(UPLOADS_DIR.glob("*"))),
            "Disk Size": f"{uploads_size / 1024:.2f} KB",
            "Storage Type": "Local File Storage"
        },
        {
            "Storage Location": "Vector Store (`data/vector_store`)",
            "File Count": len(list(VECTOR_STORE_DIR.glob("*"))),
            "Disk Size": f"{vector_size / 1024:.2f} KB",
            "Storage Type": "Local FAISS Binary Index"
        }
    ])
    st.dataframe(storage_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    if st.button("🗑️ Emergency Data Purge (Delete All Documents & Indices)", type="primary"):
        service.clear_all()
        st.success("All local uploads, vector indices, and conversation histories have been purged.")
        st.rerun()
