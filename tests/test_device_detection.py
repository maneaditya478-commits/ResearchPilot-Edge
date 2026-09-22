"""
Unit tests for hardware detection and execution provider diagnostics.
"""

from app.inference.device_detection import DeviceDetector

def test_device_detection_structure():
    info = DeviceDetector.detect_system()

    assert "os" in info
    assert "architecture" in info
    assert "processor" in info
    assert "is_arm64" in info
    assert "is_snapdragon_detected" in info
    assert "total_ram_gb" in info
    assert "onnx_execution_providers" in info
    assert "active_backend" in info
    assert "backend_description" in info
    assert isinstance(info["total_ram_gb"], float)
    assert info["total_ram_gb"] > 0

def test_onnx_providers_is_list():
    providers = DeviceDetector._get_onnx_providers()
    assert isinstance(providers, list)
