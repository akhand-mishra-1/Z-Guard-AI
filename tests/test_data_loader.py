"""
Unit tests for data ingestion, schema validation, and synthetic telemetry generation.
"""

import pandas as pd
import pytest
from src.config import FEATURE_COLUMNS
from src.data_loader import (
    generate_synthetic_telemetry,
    map_column_names,
    validate_and_clean_data,
)


def test_synthetic_telemetry_generation():
    """Verify synthetic generator creates the requested shape, types, and expected columns."""
    df = generate_synthetic_telemetry(n_samples=150, random_seed=42, inject_anomalies=True)
    
    assert len(df) == 150
    for col in FEATURE_COLUMNS:
        assert col in df.columns
        assert df[col].dtype in [float, int]
        # Check non-negative bounds
        assert (df[col] >= 0).all()

    # Percentage metrics must be bounded <= 100%
    assert (df["cpu_pct"] <= 100.0).all()
    assert (df["memory_pct"] <= 100.0).all()
    assert (df["disk_pct"] <= 100.0).all()

    assert "timestamp" in df.columns
    assert "ground_truth_scenario" in df.columns


def test_fuzzy_column_mapping():
    """Verify forgiving CSV column mapping for common variations."""
    raw_df = pd.DataFrame({
        "CPU": [20, 30],
        "RAM_Usage": [40, 50],
        "Disk_IO": [10, 15],
        "Bandwidth_Mbps": [100, 200],
        "Date": ["2026-01-01 10:00:00", "2026-01-01 10:01:00"]
    })

    mapped_df, mappings, missing = map_column_names(raw_df)
    assert len(missing) == 0
    assert "cpu_pct" in mapped_df.columns
    assert "memory_pct" in mapped_df.columns
    assert "disk_pct" in mapped_df.columns
    assert "network_mbps" in mapped_df.columns
    assert "timestamp" in mapped_df.columns


def test_missing_column_validation_failure():
    """Verify that an invalid CSV missing required features fails validation cleanly."""
    invalid_df = pd.DataFrame({
        "temperature": [50, 60],
        "pressure": [1013, 1014]
    })

    cleaned_df, report = validate_and_clean_data(invalid_df)
    assert cleaned_df is None
    assert report["is_valid"] is False
    assert len(report["errors"]) > 0


def test_missing_values_imputation():
    """Verify that NaN or null entries are safely imputed with medians rather than crashing."""
    df_with_nans = pd.DataFrame({
        "timestamp": ["2026-01-01 12:00:00", "2026-01-01 12:01:00", "2026-01-01 12:02:00"],
        "cpu_pct": [25.0, None, 35.0],
        "memory_pct": [50.0, 52.0, None],
        "disk_pct": [30.0, 30.0, 30.0],
        "network_mbps": [100.0, 120.0, 110.0]
    })

    cleaned, report = validate_and_clean_data(df_with_nans)
    assert report["is_valid"] is True
    assert report["missing_values_filled"] == 2
    assert cleaned["cpu_pct"].isna().sum() == 0
    assert cleaned["memory_pct"].isna().sum() == 0
    # Imputed CPU should match median (30.0)
    assert cleaned.loc[1, "cpu_pct"] == 30.0
