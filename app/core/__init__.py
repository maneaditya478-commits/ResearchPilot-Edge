"""
Core configuration and logging module.
"""
from app.core.config import settings, BASE_DIR, DATA_DIR, UPLOADS_DIR, PROCESSED_DIR, VECTOR_STORE_DIR, SAMPLE_PAPERS_DIR, MODELS_DIR, BENCHMARKS_DIR, DOCS_DIR
from app.core.logger import get_logger, logger

__all__ = [
    "settings",
    "logger",
    "get_logger",
    "BASE_DIR",
    "DATA_DIR",
    "UPLOADS_DIR",
    "PROCESSED_DIR",
    "VECTOR_STORE_DIR",
    "SAMPLE_PAPERS_DIR",
    "MODELS_DIR",
    "BENCHMARKS_DIR",
    "DOCS_DIR",
]
