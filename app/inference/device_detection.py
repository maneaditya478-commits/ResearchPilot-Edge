"""
ResearchPilot Edge - Hardware & Execution Backend Detection
Accurately detects system processor, Snapdragon NPU presence, DirectML, and ONNX Runtime providers.
"""

import platform
import sys
import os
import psutil
from typing import Dict, Any, List
from app.core.logger import logger

class DeviceDetector:
    """
    Detects hardware capabilities and execution acceleration backends.
    Strictly reports verified hardware states without fabricating Snapdragon NPU execution.
    """

    @staticmethod
    def detect_system() -> Dict[str, Any]:
        """
        Gathers system platform, CPU, RAM, and hardware acceleration details.
        """
        system_os = platform.system()
        machine_arch = platform.machine().lower()
        processor_raw = platform.processor()
        os_release = platform.release()
        os_version = platform.version()
        
        # Memory Info
        mem = psutil.virtual_memory()
        total_ram_gb = round(mem.total / (1024 ** 3), 2)
        available_ram_gb = round(mem.available / (1024 ** 3), 2)
        cpu_cores_physical = psutil.cpu_count(logical=False) or 1
        cpu_cores_logical = psutil.cpu_count(logical=True) or 1

        # Detect Snapdragon / Qualcomm processor keywords
        is_arm64 = machine_arch in ("arm64", "aarch64") or "arm" in processor_raw.lower()
        is_snapdragon = any(k in processor_raw.lower() for k in ["snapdragon", "qualcomm", "sc8380", "x elite", "x plus", "hexagon"])
        
        # Check ONNX Runtime Execution Providers
        onnx_providers = DeviceDetector._get_onnx_providers()
        
        # Check PyTorch Backends
        pytorch_backends = DeviceDetector._get_pytorch_backends()
        
        # Determine actual active acceleration backend
        active_backend, backend_description = DeviceDetector._resolve_active_backend(
            is_snapdragon=is_snapdragon,
            is_arm64=is_arm64,
            onnx_providers=onnx_providers,
            pytorch_backends=pytorch_backends
        )

        return {
            "os": system_os,
            "os_release": os_release,
            "os_version": os_version,
            "architecture": machine_arch,
            "processor": processor_raw or "Generic Processor",
            "is_arm64": is_arm64,
            "is_snapdragon_detected": is_snapdragon,
            "total_ram_gb": total_ram_gb,
            "available_ram_gb": available_ram_gb,
            "cpu_physical_cores": cpu_cores_physical,
            "cpu_logical_cores": cpu_cores_logical,
            "onnx_execution_providers": onnx_providers,
            "pytorch_backends": pytorch_backends,
            "active_backend": active_backend,
            "backend_description": backend_description,
            "snapdragon_npu_ready": "QNNExecutionProvider" in onnx_providers or (is_snapdragon and "DmlExecutionProvider" in onnx_providers),
            "qualcomm_ai_hub_ready": bool(os.getenv("QAI_HUB_API_TOKEN")),
        }

    @staticmethod
    def _get_onnx_providers() -> List[str]:
        """Inspects ONNX Runtime for registered Execution Providers."""
        try:
            import onnxruntime as ort
            return ort.get_available_providers()
        except Exception as e:
            logger.debug(f"ONNX Runtime provider inspection error: {e}")
            return []

    @staticmethod
    def _get_pytorch_backends() -> List[str]:
        """Inspects PyTorch for CUDA / MPS / DirectML / CPU backends."""
        backends = ["CPU"]
        try:
            import torch
            if torch.cuda.is_available():
                backends.append(f"CUDA ({torch.cuda.get_device_name(0)})")
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                backends.append("Apple MPS")
            if hasattr(torch, "xpu") and torch.xpu.is_available():
                backends.append("Intel XPU")
        except Exception:
            pass
        return backends

    @staticmethod
    def _resolve_active_backend(
        is_snapdragon: bool,
        is_arm64: bool,
        onnx_providers: List[str],
        pytorch_backends: List[str]
    ) -> tuple[str, str]:
        """Determines the most optimal execution backend realistically available."""
        if "QNNExecutionProvider" in onnx_providers:
            return "Snapdragon Hexagon NPU (QNN)", "Direct on-device Qualcomm Hexagon NPU acceleration via Qualcomm QNN Execution Provider."
        elif is_snapdragon and "DmlExecutionProvider" in onnx_providers:
            return "Snapdragon DirectML (NPU/GPU)", "Windows DirectML acceleration targeting Qualcomm Adreno GPU & Hexagon NPU sub-systems."
        elif "DmlExecutionProvider" in onnx_providers:
            return "DirectML (GPU/NPU)", "DirectML Hardware Acceleration on Windows."
        elif any("CUDA" in b for b in pytorch_backends):
            return "NVIDIA CUDA GPU", "CUDA Hardware Acceleration."
        elif "CPUExecutionProvider" in onnx_providers:
            arch_label = "ARM64 Neon" if is_arm64 else "x86_64 SIMD"
            return f"ONNX Runtime ({arch_label} CPU)", f"Optimized multi-threaded CPU execution using {arch_label} vector extensions."
        else:
            return "Local CPU Fallback", "Standard CPU Python / NumPy runtime."

# Global helper singleton
device_info = DeviceDetector.detect_system()
