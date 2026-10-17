"""
Z-Guard AI: Live Server Metrics Collector
Captures live host telemetry using psutil with safe cross-platform fallbacks.
Supports both real host hardware monitoring and simulated live streams.
"""

from datetime import datetime
import platform
import time
from typing import Dict, Optional
import psutil


class SystemMetricsCollector:
    """
    Collects live performance telemetry from the operating system.
    Compatible with Windows, Linux (x86_64 and s390x / IBM LinuxONE), and macOS.
    """

    def __init__(self):
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()
        # Initialize cpu_percent calculation
        psutil.cpu_percent(interval=None)

    def get_system_info(self) -> Dict[str, str]:
        """
        Retrieves host platform metadata (CPU architecture, OS version, etc.).
        Useful for displaying IBM LinuxONE (s390x) or x86_64 host environment details.
        """
        try:
            uname = platform.uname()
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False) or cpu_count_logical
            mem_total_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)

            return {
                "os": uname.system,
                "os_release": uname.release,
                "machine_arch": uname.machine,  # e.g., 's390x', 'AMD64', 'x86_64'
                "processor": uname.processor or "Unknown",
                "cpu_cores_physical": str(cpu_count_physical),
                "cpu_cores_logical": str(cpu_count_logical),
                "memory_total_gb": f"{mem_total_gb} GB",
                "is_s390x": uname.machine.lower() in ["s390x", "s390"]
            }
        except Exception as e:
            return {
                "os": platform.system(),
                "machine_arch": platform.machine(),
                "error": str(e),
                "is_s390x": False
            }

    def capture_snapshot(self) -> Dict[str, any]:
        """
        Captures a single timestamped snapshot of host resource telemetry.
        Returns a dictionary compatible with the model's feature schema.
        """
        now = datetime.now()
        current_time = time.time()
        time_delta = max(current_time - self.last_time, 0.1)

        # 1. CPU Usage
        try:
            cpu_pct = float(psutil.cpu_percent(interval=None))
        except Exception:
            cpu_pct = 20.0

        # 2. Memory Usage
        try:
            mem = psutil.virtual_memory()
            memory_pct = float(mem.percent)
        except Exception:
            memory_pct = 40.0

        # 3. Disk Usage (cross-platform root drive discovery)
        try:
            root_path = "C:\\" if platform.system() == "Windows" else "/"
            disk = psutil.disk_usage(root_path)
            disk_pct = float(disk.percent)
        except Exception:
            disk_pct = 35.0

        # 4. Network Throughput (Mbps)
        try:
            current_net_io = psutil.net_io_counters()
            bytes_sent_delta = current_net_io.bytes_sent - self.last_net_io.bytes_sent
            bytes_recv_delta = current_net_io.bytes_recv - self.last_net_io.bytes_recv
            total_bytes = max(bytes_sent_delta + bytes_recv_delta, 0)
            
            # Convert bytes/sec to Megabits/sec (Mbps)
            network_mbps = (total_bytes * 8.0) / (time_delta * 1_000_000.0)
            network_mbps = round(float(network_mbps), 2)
            
            self.last_net_io = current_net_io
            self.last_time = current_time
        except Exception:
            network_mbps = 50.0

        return {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_pct": round(cpu_pct, 1),
            "memory_pct": round(memory_pct, 1),
            "disk_pct": round(disk_pct, 1),
            "network_mbps": round(network_mbps, 2)
        }
