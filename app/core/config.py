"""
ResearchPilot Edge - Core Configuration
Manages application settings, hardware target paths, RAG hyperparameters, and execution backend flags.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field

# Base Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
SAMPLE_PAPERS_DIR = DATA_DIR / "sample_papers"
MODELS_DIR = BASE_DIR / "models"
BENCHMARKS_DIR = BASE_DIR / "benchmarks"
DOCS_DIR = BASE_DIR / "docs"

# Ensure all critical runtime directories exist
for directory in [
    DATA_DIR,
    UPLOADS_DIR,
    PROCESSED_DIR,
    VECTOR_STORE_DIR,
    SAMPLE_PAPERS_DIR,
    MODELS_DIR,
    BENCHMARKS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


class AppSettings(BaseModel):
    """Centralized application settings loaded from environment or defaults."""
    
    app_name: str = "ResearchPilot Edge"
    tagline: str = "Private AI Research Assistant That Works Where Your Data Is."
    version: str = "1.0.0"
    author: str = "Snapdragon AI Lab Challenge Participant"
    
    # Offline & Network Policy
    offline_mode: bool = Field(
        default=os.getenv("OFFLINE_MODE", "true").lower() in ("true", "1", "yes"),
        description="Enforces 100% on-device execution with zero external data telemetry."
    )
    
    # Preferred Inference Backend ('auto', 'onnx', 'qualcomm_ai_hub', 'transformers', 'cpu', 'fallback')
    preferred_backend: str = Field(
        default=os.getenv("PREFERRED_BACKEND", "auto")
    )
    
    # Local LLM Generation Parameters
    # Default model: Qwen/Qwen2.5-0.5B-Instruct or lightweight onnx/local model
    local_llm_model: str = Field(
        default=os.getenv("LOCAL_LLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
    )
    max_generation_tokens: int = Field(
        default=int(os.getenv("MAX_GENERATION_TOKENS", "512"))
    )
    temperature: float = Field(
        default=float(os.getenv("TEMPERATURE", "0.2"))
    )
    
    # Embedding Model Parameters
    embedding_model_name: str = Field(
        default=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    )
    embedding_dimension: int = Field(
        default=int(os.getenv("EMBEDDING_DIMENSION", "384"))
    )
    
    # Document Chunking Hyperparameters
    chunk_size: int = Field(
        default=int(os.getenv("CHUNK_SIZE", "500")),
        description="Target characters per chunk (calibrated for academic paragraphs)."
    )
    chunk_overlap: int = Field(
        default=int(os.getenv("CHUNK_OVERLAP", "80")),
        description="Character overlap to preserve boundary context."
    )
    
    # Retrieval Hyperparameters
    top_k_retrieval: int = Field(
        default=int(os.getenv("TOP_K_RETRIEVAL", "4")),
        description="Number of relevant chunks to retrieve per query."
    )
    similarity_threshold: float = Field(
        default=float(os.getenv("SIMILARITY_THRESHOLD", "0.25")),
        description="Minimum cosine similarity cutoff."
    )

    # Qualcomm AI Hub Integration (Optional)
    qai_hub_api_token: str = Field(
        default=os.getenv("QAI_HUB_API_TOKEN", "")
    )


# Global settings singleton
settings = AppSettings()
