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
    print("=" * 75)
    print("  RESEARCHPILOT EDGE -- SNAPDRAGON & HARDWARE ACCELERATION DIAGNOSTIC")
    print("=" * 75)

    info = DeviceDetector.detect_system()

    print("\n[1] HOST SYSTEM & PROCESSOR PROFILE")
    print(f"  * Operating System       : {info['os']} ({info['os_release']})")
    print(f"  * Machine Architecture   : {info['architecture'].upper()}")
    print(f"  * Processor Identifier   : {info['processor']}")
    print(f"  * Is ARM64 Native        : {'YES' if info['is_arm64'] else 'NO (x86_64 / Emulated)'}")
    print(f"  * Snapdragon Detected    : {'YES (Snapdragon / Qualcomm SoC)' if info['is_snapdragon_detected'] else 'NO (Generic x86_64 Host)'}")
    print(f"  * Physical / Logical Cores: {info['cpu_physical_cores']} / {info['cpu_logical_cores']}")
    print(f"  * System RAM Available   : {info['available_ram_gb']} GB / {info['total_ram_gb']} GB")

    print("\n[2] ONNX RUNTIME EXECUTION PROVIDERS")
    providers = info['onnx_execution_providers']
    for p in providers:
        marker = "[+]" if p in ("QNNExecutionProvider", "DmlExecutionProvider") else "[-]"
        print(f"  {marker} {p}")

    print("\n[3] HARDWARE ACCELERATION STATUS")
    print(f"  * Active Backend         : {info['active_backend']}")
    print(f"  * Description            : {info['backend_description']}")
    print(f"  * Snapdragon NPU Ready   : {'YES' if info['snapdragon_npu_ready'] else 'Requires Snapdragon HP PC with QNN provider'}")
    print(f"  * Qualcomm AI Hub SDK    : {'CONNECTED' if info['qualcomm_ai_hub_ready'] else 'API Token not configured (Optional)'}")

    print("\n[4] DEPLOYMENT GUIDE FOR SNAPDRAGON-POWERED HP LAPTOPS")
    print("  To achieve peak 45 TOPS NPU acceleration on Snapdragon X Elite / Plus:")
    print("  1. Ensure Windows 11 ARM64 is running.")
    print("  2. Install ONNX Runtime with QNN Execution Provider (onnxruntime-qnn or DirectML).")
    print("  3. Set PREFERRED_BACKEND=onnx or PREFERRED_BACKEND=qualcomm in .env.")
    print("  4. Launch ResearchPilot Edge: python run.py")

    print("=" * 75)

if __name__ == "__main__":
    main()
