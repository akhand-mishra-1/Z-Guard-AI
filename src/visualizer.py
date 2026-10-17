"""
Z-Guard AI: Visualization Engine (Plotly + IBM Carbon Aesthetics)
Provides interactive, accessible, dark-themed charts for server performance metrics,
anomaly distributions, and root-cause diagnostic telemetry.
"""

from typing import Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.config import (
    COLOR_ANOMALY,
    COLOR_IBM_BLUE,
    COLOR_NORMAL,
    COLOR_WARNING,
    FEATURE_COLUMNS,
    METRIC_LABELS,
    METRIC_UNITS,
    OPERATIONAL_THRESHOLDS,
)

# Common styling configuration for consistent enterprise aesthetics
CHART_THEME = {
    "paper_bgcolor": "rgba(22, 27, 34, 0.95)",
    "plot_bgcolor": "rgba(13, 17, 23, 0.95)",
    "font_color": "#e6edf3",
    "grid_color": "rgba(110, 118, 129, 0.2)",
    "font_family": "Segoe UI, Inter, Roboto, Helvetica, Arial, sans-serif"
}


def create_time_series_chart(
    df: pd.DataFrame,
    metric_col: str,
    title: Optional[str] = None
) -> go.Figure:
    """
    Creates an interactive time-series chart for a single metric.
    Overlays normal trendline with bright red anomaly markers and warning/critical threshold lines.
    """
    label = METRIC_LABELS.get(metric_col, metric_col)
    unit = METRIC_UNITS.get(metric_col, "")
    display_title = title or f"{label} Over Time with Detected Anomalies"

    fig = go.Figure()

    # 1. Base telemetry trace (all points)
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df[metric_col],
        mode="lines",
        name=f"{label} (Normal)",
        line=dict(color=COLOR_IBM_BLUE, width=2),
        hoverinfo="skip"
    ))

    # 2. Highlighted Anomaly points
    if "anomaly" in df.columns:
        anomalies = df[df["anomaly"] == True]
        if not anomalies.empty:
            custom_data = np.stack((
                anomalies.get("anomaly_score", np.zeros(len(anomalies))),
                anomalies.get("culprit_metric", ["Unknown"] * len(anomalies)),
                anomalies.get("anomaly_reason", ["Anomaly detected"] * len(anomalies))
            ), axis=-1)

            fig.add_trace(go.Scatter(
                x=anomalies["timestamp"],
                y=anomalies[metric_col],
                mode="markers",
                name="Detected Anomaly",
                marker=dict(
                    color=COLOR_ANOMALY,
                    size=10,
                    symbol="diamond",
                    line=dict(color="#ffffff", width=1.5)
                ),
                customdata=custom_data,
                hovertemplate=(
                    "<b>ANOMALY DETECTED</b><br>"
                    + f"<b>Time:</b> %{{x}}<br>"
                    + f"<b>{label}:</b> %{{y:.1f}}{unit}<br>"
                    + "<b>Severity Score:</b> %{customdata[0]:.1f}%<br>"
                    + "<b>Driver:</b> %{customdata[1]}<br>"
                    + "<b>Diagnostic:</b> %{customdata[2]}<extra></extra>"
                )
            ))

    # 3. Operational Reference Threshold Lines (if applicable)
    thresh = OPERATIONAL_THRESHOLDS.get(metric_col)
    if thresh:
        if "critical" in thresh and thresh["critical"] <= df[metric_col].max() * 1.2:
            fig.add_hline(
                y=thresh["critical"],
                line_dash="dot",
                line_color=COLOR_ANOMALY,
                annotation_text=f"Critical Threshold ({thresh['critical']}{unit})",
                annotation_position="top right",
                annotation_font=dict(color=COLOR_ANOMALY, size=11)
            )
        if "warning" in thresh and thresh["warning"] <= df[metric_col].max() * 1.2:
            fig.add_hline(
                y=thresh["warning"],
                line_dash="dot",
                line_color=COLOR_WARNING,
                annotation_text=f"Warning Threshold ({thresh['warning']}{unit})",
                annotation_position="bottom right",
                annotation_font=dict(color=COLOR_WARNING, size=11)
            )

    fig.update_layout(
        title=dict(text=display_title, font=dict(size=15, color="#ffffff")),
        xaxis=dict(
            title="Timestamp",
            showgrid=True,
            gridcolor=CHART_THEME["grid_color"],
            color=CHART_THEME["font_color"]
        ),
        yaxis=dict(
            title=f"{label} ({unit})",
            showgrid=True,
            gridcolor=CHART_THEME["grid_color"],
            color=CHART_THEME["font_color"]
        ),
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=dict(family=CHART_THEME["font_family"], color=CHART_THEME["font_color"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        height=340
    )

    return fig


def create_synchronized_metrics_dashboard(df: pd.DataFrame) -> go.Figure:
    """
    Builds a 4-panel synchronized subplot comparing CPU, Memory, Disk, and Network telemetry.
    Allows administrators to correlate multi-metric patterns across the exact same timeline.
    """
    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=[
            f"1. {METRIC_LABELS['cpu_pct']} (%)",
            f"2. {METRIC_LABELS['memory_pct']} (%)",
            f"3. {METRIC_LABELS['disk_pct']} (%)",
            f"4. {METRIC_LABELS['network_mbps']} (Mbps)"
        ]
    )

    colors = ["#0f62fe", "#1192e8", "#8a3ffc", "#0072c3"]
    anomalies = df[df.get("anomaly", False) == True] if "anomaly" in df.columns else pd.DataFrame()

    for idx, col in enumerate(FEATURE_COLUMNS):
        row_num = idx + 1
        unit = METRIC_UNITS.get(col, "")
        
        # Telemetry trace
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[col],
                mode="lines",
                name=METRIC_LABELS[col],
                line=dict(color=colors[idx % len(colors)], width=1.8),
                hovertemplate=f"<b>Time:</b> %{{x}}<br><b>Value:</b> %{{y:.1f}}{unit}<extra></extra>"
            ),
            row=row_num,
            col=1
        )

        # Overlay anomalies on this subplot
        if not anomalies.empty:
            fig.add_trace(
                go.Scatter(
                    x=anomalies["timestamp"],
                    y=anomalies[col],
                    mode="markers",
                    name="Anomaly Point" if idx == 0 else None,
                    showlegend=(idx == 0),
                    marker=dict(color=COLOR_ANOMALY, size=7, symbol="circle"),
                    hovertemplate=f"<b>ANOMALY</b>: %{{y:.1f}}{unit}<extra></extra>"
                ),
                row=row_num,
                col=1
            )

    fig.update_layout(
        height=750,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=dict(family=CHART_THEME["font_family"], color=CHART_THEME["font_color"]),
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    for i in range(1, 5):
        fig.update_xaxes(showgrid=True, gridcolor=CHART_THEME["grid_color"], row=i, col=1)
        fig.update_yaxes(showgrid=True, gridcolor=CHART_THEME["grid_color"], row=i, col=1)

    return fig


def create_scatter_correlation(
    df: pd.DataFrame,
    x_metric: str = "cpu_pct",
    y_metric: str = "memory_pct"
) -> go.Figure:
    """
    2D correlation scatter plot showing metric clustering and outlier dispersion.
    """
    fig = go.Figure()

    normal = df[df.get("anomaly", False) == False] if "anomaly" in df.columns else df
    anomalies = df[df.get("anomaly", False) == True] if "anomaly" in df.columns else pd.DataFrame()

    x_label = METRIC_LABELS.get(x_metric, x_metric)
    y_label = METRIC_LABELS.get(y_metric, y_metric)

    # Normal cluster
    fig.add_trace(go.Scatter(
        x=normal[x_metric],
        y=normal[y_metric],
        mode="markers",
        name="Normal Operation",
        marker=dict(color=COLOR_NORMAL, size=7, opacity=0.7),
        hovertemplate=f"{x_label}: %{{x:.1f}}<br>{y_label}: %{{y:.1f}}<extra></extra>"
    ))

    # Anomalous outliers
    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies[x_metric],
            y=anomalies[y_metric],
            mode="markers",
            name="Detected Anomaly",
            marker=dict(
                color=COLOR_ANOMALY,
                size=11,
                symbol="diamond",
                line=dict(color="#ffffff", width=1.5)
            ),
            hovertemplate=f"<b>ANOMALY</b><br>{x_label}: %{{x:.1f}}<br>{y_label}: %{{y:.1f}}<extra></extra>"
        ))

    fig.update_layout(
        title=dict(text=f"Resource Cluster Analysis: {x_label} vs {y_label}", font=dict(size=14, color="#ffffff")),
        xaxis=dict(title=x_label, showgrid=True, gridcolor=CHART_THEME["grid_color"]),
        yaxis=dict(title=y_label, showgrid=True, gridcolor=CHART_THEME["grid_color"]),
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=dict(family=CHART_THEME["font_family"], color=CHART_THEME["font_color"]),
        height=380,
        margin=dict(l=40, r=40, t=50, b=40)
    )

    return fig


def create_radar_attribution(row: pd.Series, baseline_stats: dict) -> go.Figure:
    """
    Radar chart illustrating the relative multi-metric deviation for an anomalous sample.
    """
    categories = [METRIC_LABELS[col] for col in FEATURE_COLUMNS]
    
    # Normalized feature values (0-100 scale for comparison)
    observed_vals = []
    baseline_vals = []
    for col in FEATURE_COLUMNS:
        stat = baseline_stats.get(col, {"mean": 50.0, "std": 10.0})
        # Standardized scale 0-100 where 50 is mean
        obs = float(row[col])
        mean = float(stat["mean"])
        if col == "network_mbps":
            obs_norm = min((obs / 1000.0) * 100.0, 100.0)
            base_norm = min((mean / 1000.0) * 100.0, 100.0)
        else:
            obs_norm = obs
            base_norm = mean
        observed_vals.append(obs_norm)
        baseline_vals.append(base_norm)

    # Close the radar loop
    categories_closed = categories + [categories[0]]
    observed_closed = observed_vals + [observed_vals[0]]
    baseline_closed = baseline_vals + [baseline_vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=baseline_closed,
        theta=categories_closed,
        fill="toself",
        name="Baseline Normal Mean",
        line=dict(color=COLOR_NORMAL, width=1.5),
        fillcolor="rgba(36, 161, 72, 0.2)"
    ))
    fig.add_trace(go.Scatterpolar(
        r=observed_closed,
        theta=categories_closed,
        fill="toself",
        name="Anomalous Event",
        line=dict(color=COLOR_ANOMALY, width=2.5),
        fillcolor="rgba(218, 30, 40, 0.35)"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#a8b3cf", gridcolor=CHART_THEME["grid_color"]),
            bgcolor=CHART_THEME["plot_bgcolor"]
        ),
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        font=dict(family=CHART_THEME["font_family"], color=CHART_THEME["font_color"]),
        height=340,
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )

    return fig
