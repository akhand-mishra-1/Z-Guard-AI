"""
Unit tests for the Machine Learning Anomaly Detector (Isolation Forest).
"""

import numpy as np
import pandas as pd
import pytest
from src.data_loader import generate_synthetic_telemetry
from src.detector import AnomalyDetector


def test_detector_fit_and_predict_lifecycle():
    """Verify Isolation Forest training, predictions, and output schema enrichment."""
    # Generate training data
    train_df = generate_synthetic_telemetry(n_samples=200, random_seed=42, inject_anomalies=True)
    detector = AnomalyDetector(contamination=0.08, n_estimators=50, random_state=42)
    
    assert not detector.is_fitted
    detector.fit(train_df)
    assert detector.is_fitted

    # Run inference
    scored_df = detector.predict(train_df)
    
    # Required output columns
    expected_cols = [
        "anomaly",
        "prediction_label",
        "raw_decision_score",
        "anomaly_score",
        "culprit_metric",
        "anomaly_reason",
        "severity",
        "mitigation_action"
    ]
    for col in expected_cols:
        assert col in scored_df.columns

    # Verify predictions are boolean / valid categories
    assert scored_df["anomaly"].dtype == bool
    assert set(scored_df["prediction_label"].unique()).issubset({"Normal", "Anomaly"})
    assert (scored_df["anomaly_score"] >= 0.0).all()
    assert (scored_df["anomaly_score"] <= 100.0).all()


def test_extreme_outlier_detection():
    """Verify that an extreme resource spike is correctly flagged as an Anomaly with High Severity."""
    # Train on normal baseline
    normal_df = generate_synthetic_telemetry(n_samples=150, random_seed=12, inject_anomalies=False)
    detector = AnomalyDetector(contamination=0.05, n_estimators=50, random_state=42)
    detector.fit(normal_df)

    # Create an extreme outlier row
    outlier_df = pd.DataFrame([{
        "timestamp": "2026-01-01 12:00:00",
        "cpu_pct": 99.8,
        "memory_pct": 98.5,
        "disk_pct": 99.1,
        "network_mbps": 995.0
    }])

    result = detector.predict(outlier_df)
    assert result.loc[0, "anomaly"] == True
    assert result.loc[0, "prediction_label"] == "Anomaly"
    assert result.loc[0, "severity"] in ["CRITICAL", "WARNING"]
    assert result.loc[0, "anomaly_score"] > 60.0


def test_unfitted_detector_raises_error():
    """Verify that calling predict on an unfitted detector raises RuntimeError."""
    detector = AnomalyDetector()
    test_df = pd.DataFrame([{
        "timestamp": "2026-01-01 12:00:00",
        "cpu_pct": 20.0,
        "memory_pct": 40.0,
        "disk_pct": 30.0,
        "network_mbps": 100.0
    }])
    with pytest.raises(RuntimeError):
        detector.predict(test_df)


def test_insufficient_training_data_error():
    """Verify that fitting with fewer than 5 records raises ValueError."""
    detector = AnomalyDetector()
    small_df = pd.DataFrame([{
        "cpu_pct": 20.0,
        "memory_pct": 40.0,
        "disk_pct": 30.0,
        "network_mbps": 100.0
    }])
    with pytest.raises(ValueError):
        detector.fit(small_df)
