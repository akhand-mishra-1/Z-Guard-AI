"""
Unit tests for live system metrics collector (psutil).
"""

from src.metrics_collector import SystemMetricsCollector


def test_system_info_retrieval():
    """Verify that collector captures platform info correctly."""
    collector = SystemMetricsCollector()
    info = collector.get_system_info()
    assert "os" in info
    assert "machine_arch" in info
    assert "is_s390x" in info
    assert isinstance(info["is_s390x"], bool)


def test_snapshot_schema_and_ranges():
    """Verify snapshot dictionary schema and reasonable numerical bounds."""
    collector = SystemMetricsCollector()
    snapshot = collector.capture_snapshot()

    assert "timestamp" in snapshot
    assert "cpu_pct" in snapshot
    assert "memory_pct" in snapshot
    assert "disk_pct" in snapshot
    assert "network_mbps" in snapshot

    # Values must be non-negative
    assert snapshot["cpu_pct"] >= 0.0
    assert snapshot["memory_pct"] >= 0.0
    assert snapshot["disk_pct"] >= 0.0
    assert snapshot["network_mbps"] >= 0.0

    # Percentages bounded by 100
    assert snapshot["cpu_pct"] <= 100.0
    assert snapshot["memory_pct"] <= 100.0
    assert snapshot["disk_pct"] <= 100.0
