"""
ResearchPilot Edge - Paper Comparison Component
Generates a side-by-side scientific comparison matrix across multiple uploaded papers.
"""

import streamlit as st
import pandas as pd
from app.backend.service import service

def render_compare():
    """Renders multi-paper side-by-side comparison table."""
    st.markdown("### ⚖️ Multi-Paper Scientific Comparison")
    st.markdown("Compare methodologies, hardware architectures, datasets, and performance results across multiple documents.")

    doc_list = service.vector_store.get_document_list()
    if len(doc_list) < 2:
        st.info("Please index at least 2 research papers to enable comparative analysis. Click 'Load Demo Dataset' in the Dashboard to test immediately.")
        return

    doc_names = [d["document"] for d in doc_list]
    
    # Default select first 2
    default_selection = doc_names[:min(3, len(doc_names))]
    selected_docs = st.multiselect(
        "Select 2 or more research documents to compare:",
        options=doc_names,
        default=default_selection
    )

    if len(selected_docs) < 2:
        st.warning("Select at least 2 documents to view comparison.")
        return

    if st.button("🚀 Generate Comparison Matrix", type="primary"):
        with st.spinner("Analyzing and constructing scientific comparison matrix..."):
            matrix = service.compare_documents(selected_docs)
            st.session_state.comparison_matrix = matrix
            st.session_state.compared_docs = selected_docs

    if "comparison_matrix" in st.session_state:
        st.markdown("---")
        st.markdown(f"#### 📊 Comparative Matrix: {', '.join(st.session_state.get('compared_docs', []))}")
        
        df = pd.DataFrame(st.session_state.comparison_matrix)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Export Options
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        col_csv, col_md = st.columns(2)
        with col_csv:
            csv_data = df.to_csv(index=False)
            st.download_button(
                "📥 Export Matrix as CSV",
                data=csv_data,
                file_name="paper_comparison_matrix.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_md:
            md_table = df.to_markdown(index=False)
            st.download_button(
                "📥 Export Matrix as Markdown",
                data=md_table,
                file_name="paper_comparison_matrix.md",
                mime="text/markdown",
                use_container_width=True
            )
