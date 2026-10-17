"""
Script to generate sample telemetry datasets for Z-Guard AI.
Saves CSV files to data/ directory.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import generate_synthetic_telemetry

def main():
    os.makedirs("data", exist_ok=True)
    
    # 1. Primary demo dataset: 600 timestamps (10 hours of simulated metrics)
    print("Generating data/sample_server_metrics.csv (600 rows)...")
    df_demo = generate_synthetic_telemetry(n_samples=600, random_seed=42, inject_anomalies=True)
    df_demo.to_csv("data/sample_server_metrics.csv", index=False)
    print(f"Saved {len(df_demo)} records to data/sample_server_metrics.csv")

    # 2. Targeted test dataset: 250 timestamps
    print("Generating data/test_synthetic_scenarios.csv (250 rows)...")
    df_test = generate_synthetic_telemetry(n_samples=250, random_seed=99, inject_anomalies=True)
    df_test.to_csv("data/test_synthetic_scenarios.csv", index=False)
    print(f"Saved {len(df_test)} records to data/test_synthetic_scenarios.csv")

    # 3. Clean baseline normal dataset: 200 timestamps (no anomalies)
    print("Generating data/clean_baseline_metrics.csv (200 rows)...")
    df_clean = generate_synthetic_telemetry(n_samples=200, random_seed=123, inject_anomalies=False)
    df_clean.to_csv("data/clean_baseline_metrics.csv", index=False)
    print(f"Saved {len(df_clean)} records to data/clean_baseline_metrics.csv")

if __name__ == "__main__":
    main()
