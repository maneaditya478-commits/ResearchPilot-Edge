"""
ResearchPilot Edge - Base Inference Engine Interface
Defines the contract for local AI generation, summarization, and paper comparison backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class InferenceResult:
    """Standardized response payload from any local AI inference engine."""
    text: str
    tokens_generated: int = 0
    latency_ms: float = 0.0
    tokens_per_sec: float = 0.0
    backend_name: str = "Unknown"
    model_name: str = "Unknown"
    sources: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.85
    is_fallback: bool = False

class InferenceEngine(ABC):
    """Abstract base class for all on-device LLM inference backends."""

    def __init__(self, model_name: str = "default"):
        self.model_name = model_name

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Name of the active execution provider / backend."""
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2
    ) -> InferenceResult:
        """
        Generates text given a prompt and optional retrieved context.
        """
        pass

    @abstractmethod
    def summarize(
        self,
        document_text: str,
        document_name: str,
        max_tokens: int = 600
    ) -> Dict[str, Any]:
        """
        Extracts structured academic summary sections:
        Abstract, Research Objectives, Methodology, Dataset, Key Findings, Results, Limitations.
        """
        pass

    @abstractmethod
    def compare(
        self,
        docs_payload: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generates a side-by-side comparison table across standard scientific dimensions.
        """
        pass
