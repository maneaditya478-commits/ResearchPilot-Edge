"""
ResearchPilot Edge - Semantic Search Component
Provides direct hybrid dense-vector and keyword retrieval across the local document collection.
"""

import streamlit as st
from app.backend.service import service

def render_search():
    """Renders direct semantic search interface."""
    st.markdown("### 🔍 Semantic & Hybrid Document Search")
    st.markdown("Query the local vector index directly to find relevant paragraphs, equations, and section references.")

    doc_list = service.vector_store.get_document_list()
    if not doc_list:
        st.info("No documents indexed. Upload papers or load demo dataset first.")
        return

    col_q, col_k = st.columns([4, 1])
    with col_q:
        search_query = st.text_input("Enter search query or keywords:", placeholder="e.g., Hexagon NPU 45 TOPS quantization")
    with col_k:
        top_k = st.slider("Results (Top-K):", min_value=1, max_value=15, value=5)

    if search_query:
        with st.spinner("Searching local vector index..."):
            results = service.search_chunks(search_query, top_k=top_k)

        if not results:
            st.warning("No matching chunks found above the similarity threshold.")
            return

        st.markdown(f"#### Found {len(results)} Relevant Passages")
        
        for r in results:
            score = r.get("similarity_score", 0.0)
            st.markdown(
                f"""
                <div class="citation-card">
                    <div class="citation-header">
                        <span>📄 {r['document']} — Page {r['page']} | Section: {r.get('section', 'General')}</span>
                        <span>Relevance Score: {int(score * 100)}%</span>
                    </div>
                    <div class="citation-snippet">
                        "{r['text']}"
                    </div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 6px;">
                        Chunk ID: <code>{r['chunk_id']}</code> | Dense Score: {r.get('dense_score', 'N/A')} | Keyword Score: {r.get('keyword_score', 'N/A')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
