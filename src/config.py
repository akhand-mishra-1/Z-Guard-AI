"""
Z-Guard AI: Configuration and Constants
IBM Z Datathon 2026
"""

# Core metric columns expected across ingestion sources
FEATURE_COLUMNS = [
    "cpu_pct",
    "memory_pct",
    "disk_pct",
    "network_mbps"
]

METRIC_LABELS = {
    "cpu_pct": "CPU Usage (%)",
    "memory_pct": "Memory Usage (%)",
    "disk_pct": "Disk I/O Utilization (%)",
    "network_mbps": "Network Throughput (Mbps)"
}

METRIC_UNITS = {
    "cpu_pct": "%",
    "memory_pct": "%",
    "disk_pct": "%",
    "network_mbps": "Mbps"
}

# Operational baseline reference thresholds (for rule-assisted attribution)
OPERATIONAL_THRESHOLDS = {
    "cpu_pct": {"warning": 80.0, "critical": 92.0},
    "memory_pct": {"warning": 80.0, "critical": 92.0},
    "disk_pct": {"warning": 85.0, "critical": 95.0},
    "network_mbps": {"warning": 700.0, "critical": 900.0}
}

# Isolation Forest Defaults
DEFAULT_CONTAMINATION = 0.05
DEFAULT_N_ESTIMATORS = 150
DEFAULT_RANDOM_STATE = 42

# IBM Carbon Design inspired color tokens
COLOR_IBM_BLUE = "#0f62fe"
COLOR_CYAN = "#1192e8"
COLOR_ANOMALY = "#da1e28"      # IBM Red 60
COLOR_NORMAL = "#24a148"       # IBM Green 50
COLOR_WARNING = "#f1c21b"      # IBM Yellow 30
COLOR_BG_CARD = "#1f232b"
COLOR_GRID = "#2e3440"

# Application Metadata
APP_NAME = "Z-Guard AI"
APP_SUBTITLE = "Real-Time Server Anomaly Detection"
HACKATHON_EVENT = "IBM Z Datathon 2026"
PLATFORM_TARGET = "IBM LinuxONE & zSystems (s390x) / Enterprise Cloud"
