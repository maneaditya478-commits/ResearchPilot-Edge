"""
ResearchPilot Edge - Research Chat Component (Conversational RAG)
Interactive Q&A backed by local vector retrieval, grounded context, and verifiable citations.
"""

import streamlit as st
from app.backend.service import service

def render_chat():
    """Renders the conversational RAG research assistant."""
    st.markdown("### 💬 Research Assistant Chat")
    st.markdown("Ask deep questions regarding your indexed research papers. Every answer is grounded with citations.")

    # Initialize chat history in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am **ResearchPilot Edge**, your local AI research assistant. "
                    "You can ask me questions about your uploaded papers, methodology details, datasets, "
                    "or performance benchmarks. All inference is computed locally on your device."
                ),
                "sources": [],
                "telemetry": None
            }
        ]

    # Scope Filter
    doc_list = service.vector_store.get_document_list()
    doc_options = ["All Documents"] + [d["document"] for d in doc_list]
    
    col_filter, col_clear = st.columns([4, 1])
    with col_filter:
        selected_scope = st.selectbox("Search Scope:", options=doc_options, key="chat_scope")
    with col_clear:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🧹 Clear Chat", key="clear_chat_btn", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    # Starter Questions Pills
    st.markdown("**Sample Research Questions:**")
    starters = [
        "What methodology and hardware was used on Snapdragon X Elite?",
        "What are the privacy guarantees and network audit findings?",
        "What are the throughput and latency results for quantized models?",
        "What are the stated limitations and constraints?"
    ]
    
    cols = st.columns(len(starters))
    clicked_prompt = None
    for i, prompt_text in enumerate(starters):
        with cols[i]:
            if st.button(f"💡 {prompt_text[:28]}...", key=f"starter_{i}", help=prompt_text, use_container_width=True):
                clicked_prompt = prompt_text

    # Render Conversation History
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # Render Sources
            if msg.get("sources"):
                st.markdown("**📄 Verified Source Citations:**")
                for src in msg["sources"]:
                    with st.expander(f"📄 {src['document']} — Page {src['page']} ({src['section']}) | Relevance: {int(src['relevance_score']*100)}%"):
                        st.markdown(f"**Chunk ID**: `{src['chunk_id']}`")
                        st.markdown(f"**Full Excerpt**:\n\n> {src['full_text']}")

            # Render Telemetry Badge
            if msg.get("telemetry"):
                t = msg["telemetry"]
                st.caption(
                    f"⚡ Backend: `{t['backend']}` | Total Latency: `{t['latency_ms']} ms` | Speed: `{t['tokens_sec']} tok/s` | Confidence: `{int(t['confidence']*100)}%`"
                )

    # Chat Input Handling
    user_query = st.chat_input("Ask a research question about your documents...") or clicked_prompt

    if user_query:
        # Append User Message
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("Retrieving relevant context and generating grounded answer..."):
                response = service.query_rag(
                    query=user_query,
                    filter_document=selected_scope
                )

            st.markdown(response["answer"])

            # Render Sources
            if response["sources"]:
                st.markdown("**📄 Verified Source Citations:**")
                for src in response["sources"]:
                    with st.expander(f"📄 {src['document']} — Page {src['page']} ({src['section']}) | Relevance: {int(src['relevance_score']*100)}%"):
                        st.markdown(f"**Chunk ID**: `{src['chunk_id']}`")
                        st.markdown(f"**Full Excerpt**:\n\n> {src['full_text']}")

            telemetry = {
                "backend": response["backend_used"],
                "latency_ms": response["total_latency_ms"],
                "tokens_sec": response["tokens_per_sec"],
                "confidence": response["confidence_score"]
            }
            st.caption(
                f"⚡ Backend: `{telemetry['backend']}` | Total Latency: `{telemetry['latency_ms']} ms` | Speed: `{telemetry['tokens_sec']} tok/s` | Confidence: `{int(telemetry['confidence']*100)}%`"
            )

            # Store in session state
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response["sources"],
                "telemetry": telemetry
            })
