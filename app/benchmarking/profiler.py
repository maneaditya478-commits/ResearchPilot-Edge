"""
ResearchPilot Edge - Hardware Resource Profiler
Monitors RAM, CPU utilization, thread concurrency, and accelerator metrics during execution.
"""

import time
import os
import psutil
from typing import Dict, Any

class HardwareProfiler:
    """Measures resource consumption before and after execution workloads."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self._start_time = 0.0
        self._start_cpu = 0.0
        self._start_ram_mb = 0.0

    def start(self):
        """Marks the start of a profiling window."""
        self._start_time = time.time()
        self._start_cpu = psutil.cpu_percent(interval=None)
        self._start_ram_mb = self.process.memory_info().rss / (1024 * 1024)

    def stop(self) -> Dict[str, Any]:
        """Calculates elapsed time and resource deltas."""
        elapsed_sec = time.time() - self._start_time
        end_ram_mb = self.process.memory_info().rss / (1024 * 1024)
        end_cpu = psutil.cpu_percent(interval=None)
        
        system_ram = psutil.virtual_memory()

        return {
            "elapsed_ms": round(elapsed_sec * 1000, 2),
            "process_ram_mb": round(end_ram_mb, 2),
            "ram_delta_mb": round(end_ram_mb - self._start_ram_mb, 2),
            "system_ram_used_pct": system_ram.percent,
            "cpu_utilization_pct": end_cpu,
        }
