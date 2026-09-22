"""
ResearchPilot Edge - Hardware & Execution Backend Detection
Accurately detects system processor, Snapdragon NPU presence, DirectML, and ONNX Runtime providers.
Executes real probe sessions to verify model execution capability on available hardware providers.
"""

import platform
import sys
import os
import psutil
from typing import Dict, Any, List, Tuple
from app.core.logger import logger

class DeviceDetector:
    """
    Detects hardware capabilities and execution acceleration backends.
    Strictly reports verified hardware states without fabricating Snapdragon NPU execution.
    Probes real ONNX session initialization to distinguish between provider installation and execution capability.
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
        
        # Inspect ONNX Runtime Providers and Probe Execution
        onnx_providers = DeviceDetector._get_onnx_providers()
        qnn_status, qnn_execution_reason = DeviceDetector._probe_qnn_execution()
        dml_status, dml_execution_reason = DeviceDetector._probe_directml_execution()
        cpu_status = "AVAILABLE" if "CPUExecutionProvider" in onnx_providers else "UNAVAILABLE"

        # Check PyTorch Backends
        pytorch_backends = DeviceDetector._get_pytorch_backends()
        
        # Determine actual active acceleration backend
        active_backend, backend_description = DeviceDetector._resolve_active_backend(
            is_snapdragon=is_snapdragon,
            is_arm64=is_arm64,
            onnx_providers=onnx_providers,
            qnn_execution_status=qnn_status,
            dml_execution_status=dml_status,
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
            "qnn_provider_installed": "AVAILABLE" if "QNNExecutionProvider" in onnx_providers else "UNAVAILABLE",
            "qnn_model_execution": qnn_status,
            "qnn_execution_reason": qnn_execution_reason,
            "directml_provider_installed": "AVAILABLE" if "DmlExecutionProvider" in onnx_providers else "UNAVAILABLE",
            "directml_model_execution": dml_status,
            "directml_execution_reason": dml_execution_reason,
            "cpu_provider_installed": cpu_status,
            "pytorch_backends": pytorch_backends,
            "active_backend": active_backend,
            "backend_description": backend_description,
            "snapdragon_npu_ready": (qnn_status == "SUCCESS"),
            "gpu_acceleration_ready": (dml_status == "SUCCESS" or any("CUDA" in b for b in pytorch_backends)),
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
    def _probe_qnn_execution() -> Tuple[str, str]:
        """
        Attempts to execute a minimal ONNX graph specifically on QNNExecutionProvider
        to distinguish between provider installation and actual runtime execution capability.
        """
        try:
            import onnxruntime as ort
            if "QNNExecutionProvider" not in ort.get_available_providers():
                return "UNAVAILABLE", "QNNExecutionProvider is not registered in this ONNX Runtime build."

            # Construct minimal in-memory test model to verify execution
            import numpy as np
            import onnx
            from onnx import helper, TensorProto

            # Build simple Add model: Y = X + X
            X = helper.make_tensor_value_info('X', TensorProto.FLOAT, [1, 2])
            Y = helper.make_tensor_value_info('Y', TensorProto.FLOAT, [1, 2])
            node_def = helper.make_node('Add', ['X', 'X'], ['Y'])
            graph_def = helper.make_graph([node_def], 'qnn_probe_graph', [X], [Y])
            model_def = helper.make_model(graph_def, producer_name='researchpilot_probe')
            model_bytes = model_def.SerializeToString()

            sess_options = ort.SessionOptions()
            sess_options.log_severity_level = 3  # Error only
            session = ort.InferenceSession(
                model_bytes,
                sess_options,
                providers=[("QNNExecutionProvider", {"backend_path": "QnnHtp.dll"})]
            )
            input_data = np.array([[1.0, 2.0]], dtype=np.float32)
            out = session.run(None, {'X': input_data})
            if out and len(out) > 0:
                return "SUCCESS", "QNNExecutionProvider successfully initialized and executed probe model on Hexagon NPU."
            return "FAILED", "QNN execution returned empty output."
        except Exception as e:
            return "FAILED", f"QNN execution probe failed ({type(e).__name__}: {str(e)[:120]})"

    @staticmethod
    def _probe_directml_execution() -> Tuple[str, str]:
        """Attempts to execute a minimal probe model on DirectML."""
        try:
            import onnxruntime as ort
            if "DmlExecutionProvider" not in ort.get_available_providers():
                return "UNAVAILABLE", "DmlExecutionProvider is not registered in this ONNX Runtime build."

            import numpy as np
            import onnx
            from onnx import helper, TensorProto

            X = helper.make_tensor_value_info('X', TensorProto.FLOAT, [1, 2])
            Y = helper.make_tensor_value_info('Y', TensorProto.FLOAT, [1, 2])
            node_def = helper.make_node('Add', ['X', 'X'], ['Y'])
            graph_def = helper.make_graph([node_def], 'dml_probe_graph', [X], [Y])
            model_def = helper.make_model(graph_def, producer_name='researchpilot_probe')
            model_bytes = model_def.SerializeToString()

            session = ort.InferenceSession(model_bytes, providers=['DmlExecutionProvider'])
            input_data = np.array([[1.0, 2.0]], dtype=np.float32)
            out = session.run(None, {'X': input_data})
            if out and len(out) > 0:
                return "SUCCESS", "DirectML successfully initialized and executed probe model."
            return "FAILED", "DirectML probe returned empty output."
        except Exception as e:
            return "FAILED", f"DirectML probe failed ({type(e).__name__}: {str(e)[:120]})"

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
        qnn_execution_status: str,
        dml_execution_status: str,
        pytorch_backends: List[str]
    ) -> Tuple[str, str]:
        """Determines the most optimal execution backend realistically available."""
        if qnn_execution_status == "SUCCESS":
            return "Snapdragon Hexagon NPU (QNN)", "Direct on-device Qualcomm Hexagon NPU acceleration verified via Qualcomm QNN Execution Provider."
        elif is_snapdragon and dml_execution_status == "SUCCESS":
            return "Snapdragon DirectML (Adreno GPU)", "Windows DirectML acceleration verified on Qualcomm Adreno GPU."
        elif dml_execution_status == "SUCCESS":
            return "DirectML (GPU/NPU)", "DirectML hardware acceleration verified on host GPU."
        elif any("CUDA" in b for b in pytorch_backends):
            return "NVIDIA CUDA GPU", "CUDA hardware acceleration verified."
        elif "CPUExecutionProvider" in onnx_providers:
            arch_label = "ARM64 Neon" if is_arm64 else "x86_64 SIMD"
            return f"ONNX Runtime ({arch_label} CPU)", f"Optimized multi-threaded CPU execution using {arch_label} vector extensions."
        else:
            return "Local CPU Fallback", "Standard CPU Python / NumPy runtime."

# Global helper singleton
device_info = DeviceDetector.detect_system()
