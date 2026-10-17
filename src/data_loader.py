"""
Z-Guard AI: Data Ingestion & Synthetic Telemetry Generator
Handles CSV ingestion, schema validation, data cleaning, and realistic simulation generation.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.config import FEATURE_COLUMNS, OPERATIONAL_THRESHOLDS


# Fuzzy column aliases mapping for forgiving CSV ingestion
COLUMN_ALIASES = {
    "cpu_pct": ["cpu", "cpu_pct", "cpu_percent", "cpu_usage", "cpu_utilization", "cpu_use"],
    "memory_pct": ["mem", "memory", "memory_pct", "mem_pct", "memory_percent", "ram_pct", "ram_usage", "memory_usage"],
    "disk_pct": ["disk", "disk_pct", "disk_percent", "disk_usage", "disk_io", "disk_utilization", "storage_pct"],
    "network_mbps": ["network", "net", "network_mbps", "net_mbps", "network_usage", "bandwidth_mbps", "traffic_mbps", "net_traffic"],
    "timestamp": ["timestamp", "time", "datetime", "date", "ts"]
}


def map_column_names(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str], List[str]]:
    """
    Attempt to map input DataFrame columns to the standard schema using known aliases.
    Returns (renamed_df, mappings_found, missing_required_columns).
    """
    renamed = df.copy()
    lower_cols = {str(col).strip().lower(): col for col in df.columns}
    mappings = {}

    # Find matches for each required feature
    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lower_cols:
                original_col = lower_cols[alias]
                mappings[original_col] = standard_name
                break

    renamed = renamed.rename(columns=mappings)
    missing = [feat for feat in FEATURE_COLUMNS if feat not in renamed.columns]
    return renamed, mappings, missing


def validate_and_clean_data(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Dict[str, any]]:
    """
    Validates user-uploaded or ingested dataset.
    Ensures required metrics exist, handles missing values, and normalizes types.
    """
    report = {
        "is_valid": False,
        "errors": [],
        "warnings": [],
        "rows_raw": len(df) if df is not None else 0,
        "rows_cleaned": 0,
        "missing_values_filled": 0,
        "columns_mapped": {}
    }

    if df is None or df.empty:
        report["errors"].append("The uploaded dataset is empty.")
        return None, report

    # 1. Map columns using fuzzy aliases
    cleaned_df, mappings, missing = map_column_names(df)
    report["columns_mapped"] = mappings

    if missing:
        report["errors"].append(
            f"Missing required server metric columns: {missing}. "
            f"Expected metrics for CPU, Memory, Disk, and Network."
        )
        return None, report

    # 2. Timestamp handling: create sequential timestamps if missing
    if "timestamp" not in cleaned_df.columns:
        now = datetime.now()
        report["warnings"].append("No timestamp column found. Generated 1-minute sequential timestamps.")
        cleaned_df["timestamp"] = [
            (now - timedelta(minutes=(len(cleaned_df) - i))).strftime("%Y-%m-%d %H:%M:%S")
            for i in range(len(cleaned_df))
        ]
    else:
        # Convert timestamp to string or datetime format
        cleaned_df["timestamp"] = pd.to_datetime(cleaned_df["timestamp"], errors="coerce")
        if cleaned_df["timestamp"].isna().all():
            report["warnings"].append("Could not parse timestamp values; sequential timestamps generated.")
            now = datetime.now()
            cleaned_df["timestamp"] = [
                (now - timedelta(minutes=(len(cleaned_df) - i))).strftime("%Y-%m-%d %H:%M:%S")
                for i in range(len(cleaned_df))
            ]
        else:
            cleaned_df["timestamp"] = cleaned_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # 3. Numeric conversion & sanity bounds
    total_imputed = 0
    for col in FEATURE_COLUMNS:
        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")
        nans = cleaned_df[col].isna().sum()
        if nans > 0:
            total_imputed += int(nans)
            # Impute missing values with median
            median_val = cleaned_df[col].median()
            if pd.isna(median_val):
                median_val = 25.0
            cleaned_df[col] = cleaned_df[col].fillna(median_val)
            report["warnings"].append(f"Imputed {nans} missing values in '{col}' with median ({median_val:.1f}).")

        # Sanity clip to valid ranges
        if col in ["cpu_pct", "memory_pct", "disk_pct"]:
            cleaned_df[col] = cleaned_df[col].clip(0.0, 100.0)
        elif col == "network_mbps":
            cleaned_df[col] = cleaned_df[col].clip(lower=0.0)

    report["missing_values_filled"] = total_imputed
    report["rows_cleaned"] = len(cleaned_df)
    report["is_valid"] = True

    return cleaned_df, report


def generate_synthetic_telemetry(
    n_samples: int = 600,
    random_seed: int = 42,
    inject_anomalies: bool = True
) -> pd.DataFrame:
    """
    Generates realistic synthetic server telemetry.
    Includes normal business-hour diurnal cycles, micro-bursts, and 5 distinct anomaly scenarios.
    
    DISCLAIMER: This dataset is synthetically generated for demonstration and evaluation
    purposes and does not represent an actual live production server.
    """
    np.random.seed(random_seed)
    base_time = datetime.now() - timedelta(minutes=n_samples)
    timestamps = [(base_time + timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S") for i in range(n_samples)]

    # Time array for diurnal cycle
    t = np.linspace(0, 4 * np.pi, n_samples)

    # 1. Baseline Normal Diurnal Traffic with random jitter
    # CPU: baseline ~25% + 15% diurnal curve + Gaussian noise
    cpu = 28.0 + 12.0 * np.sin(t) + np.random.normal(0, 3.5, n_samples)
    cpu = np.clip(cpu, 8.0, 55.0)

    # Memory: baseline ~45% + slight drift + noise
    memory = 45.0 + 5.0 * np.sin(t + 0.5) + np.random.normal(0, 2.0, n_samples)
    memory = np.clip(memory, 25.0, 65.0)

    # Disk: baseline ~35% + occasional small read/write bumps
    disk = 35.0 + 4.0 * np.cos(t) + np.random.normal(0, 3.0, n_samples)
    disk = np.clip(disk, 15.0, 55.0)

    # Network: baseline ~120 Mbps + diurnal peak up to 250 Mbps + noise
    network = 120.0 + 65.0 * np.sin(t) + np.random.normal(0, 18.0, n_samples)
    network = np.clip(network, 20.0, 320.0)

    # Scenario labels (Ground truth for demo evaluation)
    scenarios = ["Normal Operation"] * n_samples

    if inject_anomalies:
        # Scenario 1: CPU Spike / Runaway Thread (Timestamps 90:115)
        # Duration: 25 mins. CPU spikes to 94-99%
        s1_start, s1_end = 90, 115
        if s1_end < n_samples:
            cpu[s1_start:s1_end] = np.random.uniform(92.0, 99.5, s1_end - s1_start)
            memory[s1_start:s1_end] += np.random.uniform(5.0, 10.0, s1_end - s1_start)
            for i in range(s1_start, s1_end):
                scenarios[i] = "Anomaly: CPU Runaway Thread / Heavy Compute"

        # Scenario 2: Memory Leak / Out-Of-Memory Ramp (Timestamps 190:235)
        # Duration: 45 mins. Gradual steady accumulation from 55% to 98%
        s2_start, s2_end = 190, 235
        if s2_end < n_samples:
            leak_ramp = np.linspace(55.0, 98.5, s2_end - s2_start) + np.random.normal(0, 1.0, s2_end - s2_start)
            memory[s2_start:s2_end] = np.clip(leak_ramp, 0.0, 99.5)
            for i in range(s2_start, s2_end):
                scenarios[i] = "Anomaly: Memory Leak Accumulation"

        # Scenario 3: Disk I/O Thrashing / Storage Lockup (Timestamps 310:335)
        # Duration: 25 mins. Disk pinned at 94-99%
        s3_start, s3_end = 310, 335
        if s3_end < n_samples:
            disk[s3_start:s3_end] = np.random.uniform(92.0, 99.0, s3_end - s3_start)
            cpu[s3_start:s3_end] += np.random.uniform(10.0, 18.0, s3_end - s3_start)
            for i in range(s3_start, s3_end):
                scenarios[i] = "Anomaly: Storage Thrashing / Database Lock"

        # Scenario 4: Network Traffic Surge / DDoS Influx (Timestamps 430:460)
        # Duration: 30 mins. Bandwidth surges to 850-980 Mbps
        s4_start, s4_end = 430, 460
        if s4_end < n_samples:
            network[s4_start:s4_end] = np.random.uniform(820.0, 985.0, s4_end - s4_start)
            cpu[s4_start:s4_end] += np.random.uniform(15.0, 25.0, s4_end - s4_start)
            for i in range(s4_start, s4_end):
                scenarios[i] = "Anomaly: Network Influx / Traffic Flood"

        # Scenario 5: Catastrophic Multi-Resource Cascade (Timestamps 530:545)
        # Duration: 15 mins. Simultaneous CPU, Memory, and Disk crisis
        s5_start, s5_end = 530, 545
        if s5_end < n_samples:
            cpu[s5_start:s5_end] = np.random.uniform(94.0, 99.0, s5_end - s5_start)
            memory[s5_start:s5_end] = np.random.uniform(91.0, 98.0, s5_end - s5_start)
            disk[s5_start:s5_end] = np.random.uniform(90.0, 97.0, s5_end - s5_start)
            for i in range(s5_start, s5_end):
                scenarios[i] = "Anomaly: Multi-Resource System Saturation"

    df = pd.DataFrame({
        "timestamp": timestamps,
        "cpu_pct": np.round(cpu, 2),
        "memory_pct": np.round(memory, 2),
        "disk_pct": np.round(disk, 2),
        "network_mbps": np.round(network, 2),
        "ground_truth_scenario": scenarios
    })

    return df
