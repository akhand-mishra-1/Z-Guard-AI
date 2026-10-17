"""
Z-Guard AI: Machine Learning Anomaly Detection Engine
Uses Scikit-Learn Isolation Forest with RobustScaler, anomaly scoring,
and metric attribution for root-cause explainability.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler

from src.config import (
    DEFAULT_CONTAMINATION,
    DEFAULT_N_ESTIMATORS,
    DEFAULT_RANDOM_STATE,
    FEATURE_COLUMNS,
    METRIC_LABELS,
    METRIC_UNITS,
    OPERATIONAL_THRESHOLDS,
)


class AnomalyDetector:
    """
    Production-ready Isolation Forest wrapper for server telemetry anomaly detection.
    Performs unsupervised outlier scoring and multi-metric root cause attribution.
    """

    def __init__(
        self,
        contamination: float = DEFAULT_CONTAMINATION,
        n_estimators: int = DEFAULT_N_ESTIMATORS,
        random_state: int = DEFAULT_RANDOM_STATE,
    ):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.scaler = RobustScaler()
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.is_fitted = False
        self.baseline_stats: Dict[str, Dict[str, float]] = {}

    def fit(self, df: pd.DataFrame) -> "AnomalyDetector":
        """
        Fits the scaler and Isolation Forest model on historical or baseline telemetry.
        """
        if df is None or len(df) < 5:
            raise ValueError("Insufficient data points to train Isolation Forest (minimum 5 required).")

        X = df[FEATURE_COLUMNS].copy()
        
        # Calculate baseline statistics for explainability
        self.baseline_stats = {}
        for col in FEATURE_COLUMNS:
            self.baseline_stats[col] = {
                "mean": float(X[col].mean()),
                "median": float(X[col].median()),
                "std": float(X[col].std()) if X[col].std() > 0 else 1.0,
                "q25": float(X[col].quantile(0.25)),
                "q75": float(X[col].quantile(0.75)),
            }

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Runs inference on data.
        Returns the original DataFrame enriched with:
        - anomaly: True (Anomaly) or False (Normal)
        - prediction_label: 'Anomaly' or 'Normal'
        - raw_decision_score: Raw Isolation Forest decision function
        - anomaly_score: Normalized 0-100 severity score
        - culprit_metric: Name of primary driver metric
        - anomaly_reason: Human-readable diagnostic description
        - severity: 'CRITICAL', 'WARNING', or 'NORMAL'
        """
        if not self.is_fitted:
            raise RuntimeError("AnomalyDetector must be fitted before calling predict.")

        result_df = df.copy()
        X = result_df[FEATURE_COLUMNS]
        X_scaled = self.scaler.transform(X)

        # 1. Isolation Forest predictions: 1 = normal, -1 = anomaly
        raw_preds = self.model.predict(X_scaled)
        raw_scores = self.model.decision_function(X_scaled)

        # 2. Convert to intuitive flags
        result_df["anomaly"] = raw_preds == -1
        result_df["prediction_label"] = np.where(result_df["anomaly"], "Anomaly", "Normal")
        result_df["raw_decision_score"] = np.round(raw_scores, 4)

        # 3. Normalized Anomaly Severity Score (0 to 100%)
        # Logistic sigmoid centered at decision threshold (0.0).
        # Ensures consistent 0-100% scoring whether evaluating 1 snapshot or a full batch.
        # Negative decision values (outliers) produce scores from 50% to 100%.
        # Positive decision values (inliers) produce scores from 0% to 50%.
        z = -12.0 * raw_scores
        # Prevent overflow in exp
        z_clipped = np.clip(z, -30.0, 30.0)
        sigmoid_scores = 100.0 / (1.0 + np.exp(-z_clipped))
        result_df["anomaly_score"] = np.round(sigmoid_scores, 1)

        # 4. Metric Attribution and Human-Readable Diagnostic Generation
        culprits = []
        reasons = []
        severities = []
        mitigations = []

        for idx, row in result_df.iterrows():
            if not row["anomaly"]:
                culprits.append("None (Healthy)")
                reasons.append("Operational metrics within expected baseline distribution.")
                severities.append("NORMAL")
                mitigations.append("No action needed. System operating smoothly.")
                continue

            # Calculate standardized deviation per feature against baseline
            deviations = {}
            for col in FEATURE_COLUMNS:
                stat = self.baseline_stats.get(col, {"mean": 0, "std": 1})
                z_score = abs(row[col] - stat["mean"]) / stat["std"]
                deviations[col] = z_score

            # Identify the metric with maximum deviation
            primary_col = max(deviations, key=deviations.get)
            primary_val = row[primary_col]
            primary_label = METRIC_LABELS.get(primary_col, primary_col)
            unit = METRIC_UNITS.get(primary_col, "")
            z = deviations[primary_col]

            # Determine severity based on operational thresholds
            thresh = OPERATIONAL_THRESHOLDS.get(primary_col, {"warning": 80.0, "critical": 90.0})
            if primary_val >= thresh["critical"] or row["anomaly_score"] >= 80.0:
                severity = "CRITICAL"
            elif primary_val >= thresh["warning"] or row["anomaly_score"] >= 65.0:
                severity = "WARNING"
            else:
                severity = "ELEVATED"

            # Generate actionable description
            reason = (
                f"{primary_label} spiked to {primary_val:.1f}{unit} "
                f"({z:.1f}σ deviation from baseline mean of {self.baseline_stats[primary_col]['mean']:.1f}{unit})."
            )

            # Recommend SysAdmin Playbook
            if primary_col == "cpu_pct":
                action = "Inspect top processes with `top -c` or `ps -eo pid,%cpu,cmd`. Check for thread deadlocks or rogue jobs."
            elif primary_col == "memory_pct":
                action = "Verify memory leak via `free -m` and process memory logs. Consider restarting leak-prone service container."
            elif primary_col == "disk_pct":
                action = "Analyze disk I/O using `iotop -o` or `iostat -xz 1`. Review heavy database operations or runaway logging."
            elif primary_col == "network_mbps":
                action = "Inspect active sockets via `ss -tulpn` or `netstat`. Check for ingress traffic flood or unauthorized bulk data transfer."
            else:
                action = "Review system journal logs via `journalctl -xe`."

            culprits.append(primary_label)
            reasons.append(reason)
            severities.append(severity)
            mitigations.append(action)

        result_df["culprit_metric"] = culprits
        result_df["anomaly_reason"] = reasons
        result_df["severity"] = severities
        result_df["mitigation_action"] = mitigations

        return result_df

    def get_model_summary(self) -> Dict[str, any]:
        """
        Returns model parameters, baseline statistics, and diagnostic metadata.
        """
        return {
            "model_type": "Isolation Forest (Ensemble Tree-based)",
            "n_estimators": self.n_estimators,
            "contamination": self.contamination,
            "random_state": self.random_state,
            "is_fitted": self.is_fitted,
            "monitored_features": FEATURE_COLUMNS,
            "baseline_stats": self.baseline_stats,
        }
