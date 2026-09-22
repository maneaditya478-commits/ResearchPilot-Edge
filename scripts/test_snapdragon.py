"""
ResearchPilot Edge - Snapdragon Hardware Diagnostic & NPU Readiness Tool
Inspects host hardware, ARM64 architecture, Qualcomm Hexagon NPU availability, and ONNX Runtime providers.

Usage:
    python scripts/test_snapdragon.py
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.inference.device_detection import DeviceDetector

def main():
    info = DeviceDetector.detect_system()

    print("=" * 40)
    print("ResearchPilot Edge Snapdragon Report")
    print("=" * 40)
    print(f"Hardware: {info['os']} ({info['os_release']})")
    print(f"Architecture: {info['architecture'].upper()}")
    print(f"Processor: {info['processor']}")
    print(f"QNN Provider: {info.get('qnn_provider_installed', 'UNAVAILABLE')}")
    print(f"QNN Model Execution: {info.get('qnn_model_execution', 'UNAVAILABLE')}")
    if info.get('qnn_model_execution') == 'FAILED':
        print(f"  Reason: {info.get('qnn_execution_reason', 'Unknown')}")
    print(f"DirectML: {info.get('directml_provider_installed', 'UNAVAILABLE')}")
    print(f"DirectML Model Execution: {info.get('directml_model_execution', 'UNAVAILABLE')}")
    print(f"CPU: {info.get('cpu_provider_installed', 'AVAILABLE')}")
    print(f"RAM: {info['available_ram_gb']} GB available / {info['total_ram_gb']} GB total")
    print(f"CPU Cores: {info['cpu_physical_cores']} physical / {info['cpu_logical_cores']} logical")
    print(f"Active Backend: {info['active_backend']}")
    
    val_status = "Snapdragon NPU Verified" if info.get("snapdragon_npu_ready") else "Requires Snapdragon hardware validation"
    print(f"Validation Status: {val_status}")
    print("=" * 40)

    print("\n[DEPLOYMENT GUIDE FOR SNAPDRAGON HP LAPTOPS]")
    print("  To enable peak Hexagon NPU acceleration on Snapdragon X Elite:")
    print("  1. Ensure Windows 11 ARM64 is running.")
    print("  2. Install ONNX Runtime with QNN Execution Provider (e.g., onnxruntime-qnn).")
    print("  3. Run: python scripts/test_snapdragon.py")
    print("  4. Launch UI: python run.py --demo")

if __name__ == "__main__":
    main()
