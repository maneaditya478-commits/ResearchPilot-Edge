"""
ResearchPilot Edge - Document Summarizer Component
Generates deep structured scientific summaries (Abstract, Methodology, Dataset, Results, Limitations).
"""

import streamlit as st
import json
from app.backend.service import service

def render_summary():
    """Renders structured document summarizer interface."""
    st.markdown("### 📝 Structured Scientific Document Summarizer")
    st.markdown("Extract core research dimensions, methodology blueprints, benchmark datasets, and findings.")

    doc_list = service.vector_store.get_document_list()
    if not doc_list:
        st.info("No documents are currently indexed. Upload a document or load demo papers first.")
        return

    doc_names = [d["document"] for d in doc_list]
    col_sel, col_btn = st.columns([3, 1])
    
    with col_sel:
        selected_doc = st.selectbox("Select document to summarize:", options=doc_names, key="sum_doc_select")
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Generate Summary", type="primary", use_container_width=True)

    if generate_btn or "last_summary" in st.session_state and st.session_state.get("last_summary_doc") == selected_doc:
        with st.spinner(f"Extracting structured scientific insights for '{selected_doc}'..."):
            summary_data = service.summarize_document(selected_doc)
            st.session_state.last_summary = summary_data
            st.session_state.last_summary_doc = selected_doc

        st.markdown("---")
        st.markdown(f"#### 📑 Research Summary: {summary_data.get('title', selected_doc)}")
        st.caption(f"⚡ Generated via `{summary_data.get('backend')}` in `{summary_data.get('latency_ms')} ms`")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div class="summary-section">
                    <div class="summary-heading">📌 Abstract & Research Question</div>
                    <div class="summary-body">{summary_data['abstract']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div class="summary-section">
                    <div class="summary-heading">⚙️ Methodology & Technical Architecture</div>
                    <div class="summary-body">{summary_data['methodology']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div class="summary-section">
                    <div class="summary-heading">📊 Evaluation Dataset & Benchmark Setup</div>
                    <div class="summary-body">{summary_data['dataset']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="summary-section">
                    <div class="summary-heading">🏆 Key Results & Performance Findings</div>
                    <div class="summary-body">{summary_data['results']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div class="summary-section">
                    <div class="summary-heading">⚠️ Limitations & Future Work</div>
                    <div class="summary-body">{summary_data['limitations']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Export actions
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        col_md, col_json = st.columns(2)
        
        md_content = f"""# Summary: {selected_doc}

## Abstract & Research Question
{summary_data['abstract']}

## Methodology & Architecture
{summary_data['methodology']}

## Evaluation Dataset
{summary_data['dataset']}

## Key Results
{summary_data['results']}

## Limitations & Future Work
{summary_data['limitations']}
"""
        with col_md:
            st.download_button(
                "📥 Export as Markdown (.md)",
                data=md_content,
                file_name=f"{selected_doc}_summary.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_json:
            st.download_button(
                "📥 Export as JSON (.json)",
                data=json.dumps(summary_data, indent=2),
                file_name=f"{selected_doc}_summary.json",
                mime="application/json",
                use_container_width=True
            )
