"""
Frontend view components.
"""
from app.frontend.components.dashboard_view import render_dashboard
from app.frontend.components.documents_view import render_documents
from app.frontend.components.chat_view import render_chat
from app.frontend.components.summary_view import render_summary
from app.frontend.components.compare_view import render_compare
from app.frontend.components.search_view import render_search
from app.frontend.components.benchmark_view import render_benchmark
from app.frontend.components.privacy_view import render_privacy

__all__ = [
    "render_dashboard",
    "render_documents",
    "render_chat",
    "render_summary",
    "render_compare",
    "render_search",
    "render_benchmark",
    "render_privacy",
]
