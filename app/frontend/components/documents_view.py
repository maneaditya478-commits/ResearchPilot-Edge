"""
ResearchPilot Edge - Document Management Component
Handles file uploading (PDF, TXT, DOCX), chunk inspection, deletion, and previewing.
"""

import streamlit as st
import pandas as pd
from app.backend.service import service
from app.core.config import UPLOADS_DIR

def render_documents():
    """Renders document management and ingestion interface."""
    st.markdown("### 📂 Research Document Library")
    st.markdown("Upload research papers, technical notes, or lab documentation. All data is processed **strictly on-device**.")

    col_upload, col_demo = st.columns([3, 1])

    with col_upload:
        uploaded_files = st.file_uploader(
            "Select research documents (PDF, TXT, DOCX, MD)",
            type=["pdf", "txt", "docx", "md"],
            accept_multiple_files=True
        )

        if uploaded_files:
            if st.button(f"📥 Process & Index {len(uploaded_files)} File(s)", type="primary"):
                progress_bar = st.progress(0)
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        file_bytes = uploaded_file.read()
                        with st.spinner(f"Ingesting '{uploaded_file.name}'..."):
                            res = service.ingest_uploaded_file(uploaded_file.name, file_bytes)
                            st.toast(f"✔ Indexed {res['document']} ({res['chunks']} chunks)")
                    except Exception as e:
                        st.error(f"Failed to process {uploaded_file.name}: {e}")
                    progress_bar.progress((i + 1) / len(uploaded_files))
                st.success("All selected documents successfully indexed into local vector database!")
                st.rerun()

    with col_demo:
        st.markdown("**Sample Dataset**")
        st.caption("Pre-loaded with 3 edge AI & Snapdragon research papers.")
        if st.button("✨ Load Demo Papers", key="doc_demo_btn", use_container_width=True):
            with st.spinner("Ingesting demo papers..."):
                added = service.load_demo_dataset()
                if added:
                    st.success(f"Indexed {len(added)} demo papers!")
                else:
                    st.info("Demo papers already indexed.")
            st.rerun()

    st.markdown("---")

    # Document Library Table
    doc_list = service.vector_store.get_document_list()
    
    if not doc_list:
        st.info("No documents are currently indexed. Upload a file above or click 'Load Demo Papers' to get started.")
        return

    st.markdown(f"#### 📚 Indexed Documents ({len(doc_list)})")

    df_docs = pd.DataFrame([
        {
            "Document Name": d["document"],
            "Pages": d["page_count"],
            "Semantic Chunks": d["chunk_count"],
            "Total Characters": f"{d['total_chars']:,}",
            "Status": "✔ Active (Local)"
        }
        for d in doc_list
    ])
    st.dataframe(df_docs, use_container_width=True, hide_index=True)

    # Document Actions & Previewer
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🔍 Document Inspector & Actions")
    
    col_sel, col_del = st.columns([3, 1])
    doc_names = [d["document"] for d in doc_list]
    
    with col_sel:
        selected_doc = st.selectbox("Select document to inspect:", options=doc_names)
    
    with col_del:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button(f"🗑️ Delete Document", key="del_doc_btn", use_container_width=True):
            chunks_deleted = service.delete_document(selected_doc)
            st.success(f"Removed '{selected_doc}' ({chunks_deleted} chunks purged).")
            st.rerun()

    if selected_doc:
        chunks = service.vector_store.get_document_chunks(selected_doc)
        with st.expander(f"📖 View Extracted Semantic Chunks for '{selected_doc}' ({len(chunks)} chunks)", expanded=False):
            for c in chunks:
                st.markdown(
                    f"""
                    <div style="background: #111827; border: 1px solid #1f2937; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;">
                        <div style="color: #60a5fa; font-weight: 600; font-size: 12px; margin-bottom: 4px;">
                            Chunk ID: {c['chunk_id']} | Page: {c['page']} | Section: {c.get('section', 'General')} | {c.get('char_count', len(c['text']))} chars
                        </div>
                        <div style="color: #e5e7eb; font-size: 13px; line-height: 1.5;">
                            {c['text']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
