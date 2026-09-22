"""
Inference abstraction layer with multi-backend resolution and hardware acceleration.
"""

from typing import Optional
from app.core.config import settings
from app.inference.base import InferenceEngine, InferenceResult
from app.inference.device_detection import DeviceDetector, device_info
from app.inference.fallback_backend import DeterministicLocalInferenceEngine
from app.inference.local_backend import LocalTransformersInferenceEngine
from app.inference.onnx_backend import ONNXInferenceEngine
from app.inference.qualcomm_backend import QualcommAIHubInferenceEngine

def get_inference_engine(backend_type: Optional[str] = None) -> InferenceEngine:
    """
    Factory function resolving the optimal inference engine based on user preference and hardware.
    Options: 'auto', 'onnx', 'qualcomm_ai_hub', 'transformers', 'cpu', 'fallback'
    """
    choice = (backend_type or settings.preferred_backend).lower()

    if choice == "onnx":
        return ONNXInferenceEngine()
    elif choice in ("qualcomm", "qualcomm_ai_hub", "qnn"):
        return QualcommAIHubInferenceEngine()
    elif choice in ("transformers", "local", "pytorch"):
        return LocalTransformersInferenceEngine()
    elif choice == "fallback":
        return DeterministicLocalInferenceEngine()
    
    # Auto-resolution based on real detected hardware
    sys_info = DeviceDetector.detect_system()
    if sys_info.get("snapdragon_npu_ready"):
        return QualcommAIHubInferenceEngine()
    elif "DmlExecutionProvider" in sys_info.get("onnx_execution_providers", []):
        return ONNXInferenceEngine()
    else:
        # Default to local transformers with graceful deterministic fallback
        return LocalTransformersInferenceEngine()

__all__ = [
    "InferenceEngine",
    "InferenceResult",
    "DeviceDetector",
    "device_info",
    "DeterministicLocalInferenceEngine",
    "LocalTransformersInferenceEngine",
    "ONNXInferenceEngine",
    "QualcommAIHubInferenceEngine",
    "get_inference_engine",
]
