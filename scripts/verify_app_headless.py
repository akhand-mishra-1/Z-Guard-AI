"""
End-to-End Headless Verification Script for Z-Guard AI
Tests full pipeline: data ingestion, ML model training, prediction, metric attribution,
Plotly figure generation, and psutil telemetry capture.
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import generate_synthetic_telemetry, validate_and_clean_data
from src.detector import AnomalyDetector
from src.metrics_collector import SystemMetricsCollector
from src.visualizer import (
    create_synchronized_metrics_dashboard,
    create_time_series_chart,
    create_scatter_correlation,
    create_radar_attribution,
)

def run_verification():
    print("[1/5] Ingesting & validating sample telemetry...")
    df = pd.read_csv("data/sample_server_metrics.csv")
    cleaned_df, report = validate_and_clean_data(df)
    assert report["is_valid"], f"Validation failed: {report['errors']}"
    print(f"  -> Validated {len(cleaned_df)} records successfully.")

    print("[2/5] Training Isolation Forest model...")
    detector = AnomalyDetector(contamination=0.05, n_estimators=100, random_state=42)
    detector.fit(cleaned_df)
    assert detector.is_fitted
    print("  -> Model fitted successfully.")

    print("[3/5] Running inference & metric attribution...")
    scored_df = detector.predict(cleaned_df)
    anomalies = scored_df[scored_df["anomaly"] == True]
    assert len(anomalies) > 0, "No anomalies detected in sample data with injected anomalies!"
    print(f"  -> Detected {len(anomalies)} anomalies out of {len(scored_df)} total records ({len(anomalies)/len(scored_df)*100:.1f}%).")
    print(f"  -> Severity breakdown: CRITICAL: {(scored_df['severity'] == 'CRITICAL').sum()}, WARNING: {(scored_df['severity'] == 'WARNING').sum()}")

    print("[4/5] Testing Plotly chart generation...")
    fig_sync = create_synchronized_metrics_dashboard(scored_df)
    assert fig_sync is not None
    fig_ts = create_time_series_chart(scored_df, "cpu_pct")
    assert fig_ts is not None
    fig_scatter = create_scatter_correlation(scored_df, "cpu_pct", "memory_pct")
    assert fig_scatter is not None
    target_anomaly = anomalies.iloc[0]
    fig_radar = create_radar_attribution(target_anomaly, detector.baseline_stats)
    assert fig_radar is not None
    print("  -> All Plotly visualizations generated without errors.")

    print("[5/5] Testing host hardware metric collection (psutil)...")
    collector = SystemMetricsCollector()
    sys_info = collector.get_system_info()
    snapshot = collector.capture_snapshot()
    assert "cpu_pct" in snapshot and "memory_pct" in snapshot
    print(f"  -> Host OS: {sys_info['os']} ({sys_info['machine_arch']}), Cores: {sys_info['cpu_cores_logical']}")
    print(f"  -> Live Snapshot: CPU={snapshot['cpu_pct']}%, RAM={snapshot['memory_pct']}%, Disk={snapshot['disk_pct']}%, Net={snapshot['network_mbps']} Mbps")

    print("\n[SUCCESS] ALL VERIFICATION CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    run_verification()
