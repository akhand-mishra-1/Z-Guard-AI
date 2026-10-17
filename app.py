"""
Z-Guard AI: Real-Time Server Anomaly Detection Dashboard
IBM Z Datathon 2026

Modern, accessible, enterprise-grade server monitoring dashboard powered by
Scikit-Learn Isolation Forest and Plotly.
"""

import os
import sys
from datetime import datetime
import pandas as pd
import streamlit as st

# Ensure project root is accessible
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import (
    APP_NAME,
    APP_SUBTITLE,
    COLOR_ANOMALY,
    COLOR_IBM_BLUE,
    COLOR_NORMAL,
    COLOR_WARNING,
    DEFAULT_CONTAMINATION,
    DEFAULT_N_ESTIMATORS,
    FEATURE_COLUMNS,
    HACKATHON_EVENT,
    METRIC_LABELS,
    METRIC_UNITS,
    PLATFORM_TARGET,
)
from src.data_loader import (
    generate_synthetic_telemetry,
    validate_and_clean_data,
)
from src.detector import AnomalyDetector
from src.metrics_collector import SystemMetricsCollector
from src.visualizer import (
    create_radar_attribution,
    create_scatter_correlation,
    create_synchronized_metrics_dashboard,
    create_time_series_chart,
)

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{APP_NAME} | {APP_SUBTITLE}",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Enterprise Dark-Theme CSS (IBM Carbon Design inspired)
st.markdown("""
<style>
    /* Global Background and Typography */
    .stApp {
        background-color: #0e1117;
        color: #e6edf3;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Header Card Styling */
    .ibm-header {
        background: linear-gradient(135deg, #161b22 0%, #1f242c 100%);
        border: 1px solid #30363d;
        border-left: 5px solid #0f62fe;
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .ibm-title {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .ibm-subtitle {
        color: #8b949e;
        font-size: 14px;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .ibm-tag {
        display: inline-block;
        background-color: #0f62fe;
        color: white;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* KPI Metric Cards */
    .kpi-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px 18px;
        text-align: left;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    .kpi-title {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #8b949e;
        margin-bottom: 6px;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #f0f6fc;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 12px;
        color: #8b949e;
    }
    .badge-normal {
        color: #3fb950;
        font-weight: 600;
    }
    .badge-anomaly {
        color: #f85149;
        font-weight: 600;
    }
    .badge-warning {
        color: #d29922;
        font-weight: 600;
    }

    /* Tab enhancements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px 6px 0 0;
        color: #c9d1d9;
        padding: 10px 18px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0f62fe !important;
        color: #ffffff !important;
        border-color: #0f62fe !important;
    }

    /* Disclaimer alert banner */
    .disclaimer-banner {
        background-color: #1f232b;
        border: 1px solid #3b4252;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 12px;
        color: #a8b3cf;
        margin-top: 16px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# App State & Session Initialization
# -----------------------------------------------------------------------------
if "detector" not in st.session_state:
    st.session_state.detector = AnomalyDetector(contamination=DEFAULT_CONTAMINATION)

if "collector" not in st.session_state:
    st.session_state.collector = SystemMetricsCollector()

if "live_streaming" not in st.session_state:
    st.session_state.live_streaming = False

if "chaos_inject" not in st.session_state:
    st.session_state.chaos_inject = None

if "data" not in st.session_state:
    # Auto-load pre-packaged demo telemetry on startup
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_server_metrics.csv")
    if os.path.exists(sample_path):
        raw_df = pd.read_csv(sample_path)
        cleaned_df, _ = validate_and_clean_data(raw_df)
        st.session_state.data = cleaned_df
    else:
        st.session_state.data = generate_synthetic_telemetry(n_samples=500, random_seed=42)

if "scored_data" not in st.session_state or st.session_state.scored_data is None:
    # Initial model training
    st.session_state.detector.fit(st.session_state.data)
    st.session_state.scored_data = st.session_state.detector.predict(st.session_state.data)


# -----------------------------------------------------------------------------
# Top Header Banner
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="ibm-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
            <div class="ibm-title">
                <span>🛡️ {APP_NAME}</span>
                <span class="ibm-tag">{HACKATHON_EVENT}</span>
            </div>
            <p class="ibm-subtitle">{APP_SUBTITLE} &nbsp;•&nbsp; Targeted for {PLATFORM_TARGET}</p>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 12px; color: #8b949e;">Status:</span>
            <span style="color: #3fb950; font-weight: 600; font-size: 13px;">● ENGINE ACTIVE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Sidebar Configuration & Data Source Selector
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Telemetry & Ingestion")
    
    source_choice = st.radio(
        "Choose Data Source:",
        (
            "🚀 Pre-packaged Demo Telemetry",
            "🎲 Generate Custom Simulation",
            "📂 Upload Custom CSV",
            "⚡ Live Host Metrics (psutil)"
        )
    )

    st.markdown("---")

    # 1. Pre-packaged Demo Telemetry
    if source_choice == "🚀 Pre-packaged Demo Telemetry":
        st.info("Contains normal 10-hour diurnal cycles plus 5 realistic injected incident scenarios (CPU spike, memory leak, disk thrashing, DDoS traffic flood, multi-resource failure).")
        if st.button("🔄 Reset / Reload Sample Telemetry", use_container_width=True):
            with st.spinner("Loading demo telemetry..."):
                sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_server_metrics.csv")
                if os.path.exists(sample_path):
                    df = pd.read_csv(sample_path)
                else:
                    df = generate_synthetic_telemetry(n_samples=600, random_seed=42)
                cleaned, _ = validate_and_clean_data(df)
                st.session_state.data = cleaned
                st.session_state.detector.fit(cleaned)
                st.session_state.scored_data = st.session_state.detector.predict(cleaned)
                st.success("Sample telemetry loaded successfully!")
                st.rerun()

    # 2. Generate Custom Simulation
    elif source_choice == "🎲 Generate Custom Simulation":
        st.markdown("**Simulation Parameters**")
        n_samples = st.slider("Time Window (Minutes / Samples)", min_value=100, max_value=1200, value=500, step=50)
        seed = st.number_input("Random Generator Seed", min_value=1, max_value=9999, value=42)
        inject = st.checkbox("Inject Multi-Scenario Anomalies", value=True)
        
        if st.button("⚡ Generate Simulation Dataset", use_container_width=True):
            with st.spinner("Generating synthetic telemetry..."):
                sim_df = generate_synthetic_telemetry(n_samples=n_samples, random_seed=seed, inject_anomalies=inject)
                cleaned, report = validate_and_clean_data(sim_df)
                st.session_state.data = cleaned
                st.session_state.detector.fit(cleaned)
                st.session_state.scored_data = st.session_state.detector.predict(cleaned)
                st.success(f"Generated {len(cleaned)} telemetry records!")
                st.rerun()

    # 3. Upload Custom CSV
    elif source_choice == "📂 Upload Custom CSV":
        st.markdown("**Upload Server Metric CSV**")
        st.caption("Required metrics: `cpu_pct`, `memory_pct`, `disk_pct`, `network_mbps`, and optional `timestamp`.")
        
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                cleaned, report = validate_and_clean_data(uploaded_df)
                
                if report["is_valid"]:
                    st.success(f"✓ Valid dataset: {report['rows_cleaned']} records parsed.")
                    if report["warnings"]:
                        for w in report["warnings"]:
                            st.warning(f"Notice: {w}")
                    if st.button("🔍 Analyze Uploaded Dataset", use_container_width=True):
                        st.session_state.data = cleaned
                        st.session_state.detector.fit(cleaned)
                        st.session_state.scored_data = st.session_state.detector.predict(cleaned)
                        st.rerun()
                else:
                    st.error("Dataset validation failed:")
                    for err in report["errors"]:
                        st.error(f"- {err}")
            except Exception as e:
                st.error(f"Failed to read CSV: {str(e)}")

    # 4. Live Host Metrics (psutil)
    elif source_choice == "⚡ Live Host Metrics (psutil)":
        collector = st.session_state.collector
        info = collector.get_system_info()
        st.markdown(f"**Host System Info:**")
        st.caption(f"OS: `{info.get('os')} ({info.get('machine_arch')})` | Cores: `{info.get('cpu_cores_logical')}` | RAM: `{info.get('memory_total_gb')}`")
        if info.get("is_s390x"):
            st.success("🟢 IBM Z / LinuxONE s390x Architecture Detected!")
        
        st.markdown("#### 🔴 Continuous Live Streaming")
        live_toggle = st.toggle(
            "Enable Auto-Streaming",
            value=st.session_state.live_streaming,
            help="Continuously captures live system snapshots and updates dashboard in real-time."
        )
        st.session_state.live_streaming = live_toggle
        
        stream_interval = st.select_slider(
            "Stream Interval (seconds)",
            options=[1.0, 2.0, 3.0, 5.0],
            value=2.0
        )
        
        st.markdown("##### 🧪 Chaos Anomaly Injector")
        st.caption("Inject an instant anomaly into the live stream to test ML detection:")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💥 CPU Spike", use_container_width=True):
                st.session_state.chaos_inject = {"metric": "cpu_pct", "val": 99.2, "desc": "CPU Runaway Compute"}
                st.toast("Injected: CPU Spike (99.2%)")
            if st.button("💥 Disk Lock", use_container_width=True):
                st.session_state.chaos_inject = {"metric": "disk_pct", "val": 98.4, "desc": "Storage Thrashing"}
                st.toast("Injected: Disk Lock (98.4%)")
        with c2:
            if st.button("💥 RAM Leak", use_container_width=True):
                st.session_state.chaos_inject = {"metric": "memory_pct", "val": 97.8, "desc": "Out-of-Memory Surge"}
                st.toast("Injected: RAM Leak (97.8%)")
            if st.button("💥 Net Flood", use_container_width=True):
                st.session_state.chaos_inject = {"metric": "network_mbps", "val": 960.0, "desc": "DDoS Traffic Flood"}
                st.toast("Injected: Net Flood (960 Mbps)")
                
        st.markdown("---")
        if st.button("📸 Capture Single Snapshot Now", use_container_width=True):
            snap = collector.capture_snapshot()
            new_row = pd.DataFrame([snap])
            st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
            st.session_state.scored_data = st.session_state.detector.predict(st.session_state.data)
            st.success("Captured live host snapshot!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🧠 Machine Learning Tuning")
    
    # Model Hyperparameter Controls
    new_contamination = st.slider(
        "Contamination Rate (Assumed Outlier %)",
        min_value=0.01,
        max_value=0.20,
        value=float(st.session_state.detector.contamination),
        step=0.01,
        help="Proportion of outliers in the dataset expected by Isolation Forest."
    )
    
    new_n_estimators = st.select_slider(
        "Ensemble Trees (n_estimators)",
        options=[50, 100, 150, 200, 300],
        value=st.session_state.detector.n_estimators,
        help="Number of decision trees isolating sample points."
    )

    if (new_contamination != st.session_state.detector.contamination or 
        new_n_estimators != st.session_state.detector.n_estimators):
        if st.button("🔄 Retrain Isolation Forest", use_container_width=True):
            with st.spinner("Retraining Isolation Forest model..."):
                st.session_state.detector = AnomalyDetector(
                    contamination=new_contamination,
                    n_estimators=new_n_estimators
                )
                st.session_state.detector.fit(st.session_state.data)
                st.session_state.scored_data = st.session_state.detector.predict(st.session_state.data)
                st.success("Model retrained successfully!")
                st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 11px; color: #8b949e;">
        <b>Z-Guard AI v1.0.0</b><br>
        Developed for IBM Z Datathon 2026<br>
        Engineered for LinuxONE / s390x
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Live Streaming Real-Time Ingestion Loop
# -----------------------------------------------------------------------------
if source_choice == "⚡ Live Host Metrics (psutil)" and st.session_state.live_streaming:
    snap = st.session_state.collector.capture_snapshot()
    # Apply chaos anomaly if triggered
    if st.session_state.chaos_inject:
        c_info = st.session_state.chaos_inject
        snap[c_info["metric"]] = c_info["val"]
        st.session_state.chaos_inject = None
    
    new_row = pd.DataFrame([snap])
    # Keep rolling window of last 50 snapshots for responsive streaming
    if len(st.session_state.data) >= 50:
        st.session_state.data = pd.concat([st.session_state.data.iloc[1:], new_row], ignore_index=True)
    else:
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        
    st.session_state.scored_data = st.session_state.detector.predict(st.session_state.data)

# -----------------------------------------------------------------------------
# Data Verification
# -----------------------------------------------------------------------------
df = st.session_state.scored_data

if df is None or df.empty:
    st.warning("No telemetry dataset currently loaded. Please select a data source from the sidebar.")
    st.stop()


# -----------------------------------------------------------------------------
# High-Level Executive KPI Scorecards
# -----------------------------------------------------------------------------
total_records = len(df)
anomaly_count = int(df["anomaly"].sum())
normal_count = total_records - anomaly_count
anomaly_pct = (anomaly_count / total_records) * 100 if total_records > 0 else 0.0
normal_pct = 100.0 - anomaly_pct

critical_count = int((df["severity"] == "CRITICAL").sum())
warning_count = int((df["severity"] == "WARNING").sum())

# Threat assessment
if critical_count > 0:
    system_status = "CRITICAL ALERTS"
    status_class = "badge-anomaly"
    status_icon = "🔴"
elif warning_count > 0:
    system_status = "ELEVATED CONCERN"
    status_class = "badge-warning"
    status_icon = "🟡"
else:
    system_status = "OPTIMAL & SECURE"
    status_class = "badge-normal"
    status_icon = "🟢"

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Records</div>
        <div class="kpi-value">{total_records:,}</div>
        <div class="kpi-sub">Continuous Telemetry</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Normal Baseline</div>
        <div class="kpi-value badge-normal">{normal_count:,}</div>
        <div class="kpi-sub">{normal_pct:.1f}% Inlier Health</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Detected Anomalies</div>
        <div class="kpi-value badge-anomaly">{anomaly_count:,}</div>
        <div class="kpi-sub">{anomaly_pct:.1f}% Outlier Rate</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Critical Events</div>
        <div class="kpi-value badge-anomaly">{critical_count:,}</div>
        <div class="kpi-sub">{warning_count} Warning Alerts</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">System Threat State</div>
        <div class="kpi-value {status_class}" style="font-size: 18px;">{status_icon} {system_status}</div>
        <div class="kpi-sub">Isolation Forest Live</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Main Navigation Tabs
# -----------------------------------------------------------------------------
tab_telemetry, tab_alerts, tab_correlations, tab_model, tab_linuxone = st.tabs([
    "📊 Telemetry & Monitoring",
    "🚨 Anomaly Alerts & Playbook",
    "🔄 Correlation & Clustering",
    "🧠 Model Explainability",
    "🖥️ IBM LinuxONE Readiness"
])


# -----------------------------------------------------------------------------
# TAB 1: Telemetry & Monitoring
# -----------------------------------------------------------------------------
with tab_telemetry:
    st.markdown("#### 📈 Multi-Resource Telemetry Timeline")
    st.caption("Synchronized resource timeline showing CPU, Memory, Disk, and Network usage. Anomalies detected by Isolation Forest are highlighted in red diamonds.")
    
    # Synchronized 4-metric overview
    sync_fig = create_synchronized_metrics_dashboard(df)
    st.plotly_chart(sync_fig, use_container_width=True)

    st.markdown("---")
    
    # Deep dive single-metric selector
    col_metric_select, col_metric_info = st.columns([1, 2])
    with col_metric_select:
        selected_metric = st.selectbox(
            "Select Single Metric for Deep-Dive Analysis:",
            options=FEATURE_COLUMNS,
            format_func=lambda x: METRIC_LABELS[x]
        )
    with col_metric_info:
        cur_val = df[selected_metric].iloc[-1]
        mean_val = df[selected_metric].mean()
        max_val = df[selected_metric].max()
        unit = METRIC_UNITS[selected_metric]
        st.markdown(f"**Latest Snapshot:** `{cur_val:.1f}{unit}` &nbsp;|&nbsp; **Dataset Mean:** `{mean_val:.1f}{unit}` &nbsp;|&nbsp; **Peak Observed:** `{max_val:.1f}{unit}`")

    single_fig = create_time_series_chart(df, selected_metric)
    st.plotly_chart(single_fig, use_container_width=True)


# -----------------------------------------------------------------------------
# TAB 2: Anomaly Alerts & Playbook
# -----------------------------------------------------------------------------
with tab_alerts:
    st.markdown("#### 🚨 Anomaly Event Log & SysAdmin Remediation Playbook")
    st.caption("Each detected incident is attributed to its primary driving metric using standardized deviation from operational baseline.")

    anomalies_df = df[df["anomaly"] == True].copy()

    if anomalies_df.empty:
        st.success("🎉 No anomalies detected in current dataset! All metrics are within normal operational baseline boundaries.")
    else:
        # Filter controls
        f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
        with f_col1:
            severity_filter = st.selectbox("Filter by Severity:", ["ALL", "CRITICAL", "WARNING", "ELEVATED"])
        with f_col2:
            driver_filter = st.selectbox(
                "Filter by Culprit Metric:",
                ["ALL"] + list(anomalies_df["culprit_metric"].unique())
            )
        
        filtered_anomalies = anomalies_df
        if severity_filter != "ALL":
            filtered_anomalies = filtered_anomalies[filtered_anomalies["severity"] == severity_filter]
        if driver_filter != "ALL":
            filtered_anomalies = filtered_anomalies[filtered_anomalies["culprit_metric"] == driver_filter]

        # Display summary counts
        st.markdown(f"Showing **{len(filtered_anomalies)}** matching incident records (out of {len(anomalies_df)} total anomalies).")

        # Clean Table presentation
        display_cols = [
            "timestamp",
            "severity",
            "anomaly_score",
            "culprit_metric",
            "cpu_pct",
            "memory_pct",
            "disk_pct",
            "network_mbps",
            "anomaly_reason",
            "mitigation_action"
        ]

        # Style dataframe for streamlit
        styled_view = filtered_anomalies[display_cols].rename(columns={
            "timestamp": "Timestamp",
            "severity": "Severity",
            "anomaly_score": "Score (%)",
            "culprit_metric": "Primary Driver",
            "cpu_pct": "CPU (%)",
            "memory_pct": "Memory (%)",
            "disk_pct": "Disk (%)",
            "network_mbps": "Network (Mbps)",
            "anomaly_reason": "Diagnostic Detail",
            "mitigation_action": "Remediation Playbook"
        })

        st.dataframe(
            styled_view,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score (%)": st.column_config.ProgressColumn("Anomaly Score", format="%.1f%%", min_value=0, max_value=100),
                "Severity": st.column_config.TextColumn("Severity"),
                "Timestamp": st.column_config.TextColumn("Time"),
            }
        )

        # Download alerts button
        csv_alerts = styled_view.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Incident Alerts CSV",
            data=csv_alerts,
            file_name="zguard_detected_anomalies.csv",
            mime="text/csv",
        )

        st.markdown("---")
        st.markdown("#### 🎯 Incident Root-Cause Radar Deep-Dive")
        st.caption("Select an anomalous timestamp to inspect multi-metric radial dispersion against normal baseline.")

        timestamps_list = filtered_anomalies["timestamp"].tolist()
        if timestamps_list:
            selected_ts = st.selectbox("Select Timestamp to Inspect:", timestamps_list)
            target_row = filtered_anomalies[filtered_anomalies["timestamp"] == selected_ts].iloc[0]

            r_col1, r_col2 = st.columns([1, 1])
            with r_col1:
                st.markdown(f"""
                **Incident Breakdown @ `{selected_ts}`**
                - **Severity Level:** `{target_row['severity']}`
                - **Primary Driver:** `{target_row['culprit_metric']}`
                - **Severity Score:** `{target_row['anomaly_score']:.1f}%`
                - **CPU:** `{target_row['cpu_pct']:.1f}%`
                - **Memory:** `{target_row['memory_pct']:.1f}%`
                - **Disk:** `{target_row['disk_pct']:.1f}%`
                - **Network:** `{target_row['network_mbps']:.1f} Mbps`
                
                **Diagnostic:**  
                _{target_row['anomaly_reason']}_
                
                **Recommended SysAdmin Action:**  
                `{target_row['mitigation_action']}`
                """)

            with r_col2:
                radar_fig = create_radar_attribution(target_row, st.session_state.detector.baseline_stats)
                st.plotly_chart(radar_fig, use_container_width=True)


# -----------------------------------------------------------------------------
# TAB 3: Correlation & Clustering
# -----------------------------------------------------------------------------
with tab_correlations:
    st.markdown("#### 🔄 Resource Correlation & Outlier Dispersion")
    st.caption("Visualizing pairwise metric clustering. Normal operations form dense green clusters, while anomalies diverge noticeably.")

    c_col1, c_col2 = st.columns(2)
    with c_col1:
        x_metric = st.selectbox("X-Axis Metric:", FEATURE_COLUMNS, index=0, format_func=lambda x: METRIC_LABELS[x])
    with c_col2:
        y_metric = st.selectbox("Y-Axis Metric:", FEATURE_COLUMNS, index=1, format_func=lambda x: METRIC_LABELS[x])

    scatter_fig = create_scatter_correlation(df, x_metric, y_metric)
    st.plotly_chart(scatter_fig, use_container_width=True)

    st.markdown("##### 📊 Metric Statistical Summary")
    stats_df = df[FEATURE_COLUMNS].describe().T[["mean", "std", "min", "50%", "max"]]
    stats_df.columns = ["Mean", "Std Dev", "Min", "Median (50%)", "Max"]
    st.dataframe(stats_df.round(2), use_container_width=True)


# -----------------------------------------------------------------------------
# TAB 4: Model Explainability & Limitations
# -----------------------------------------------------------------------------
with tab_model:
    st.markdown("#### 🧠 Model Architecture: Isolation Forest")
    
    st.markdown("""
    ##### How Isolation Forest Works
    Unlike traditional clustering or classification algorithms that construct profiles of normal points, **Isolation Forest** isolates anomalies explicitly by taking advantage of two quantitative properties of anomalous points:
    1. **Few in number** (they are a minority in the dataset).
    2. **Attribute-value differences** (their feature values deviate substantially from normal instances).

    The algorithm recursively partitions data points using random axis-aligned splits. Because anomalous points exist in sparse regions of the multi-dimensional feature space:
    - **Anomalies require very few partitions (short tree depth)** to isolate into individual leaf nodes.
    - **Normal instances require many partitions (deep tree depth)** because they are clustered tightly together.
    """)

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown(f"""
        **Active Model Hyperparameters:**
        - **Algorithm:** `sklearn.ensemble.IsolationForest`
        - **Number of Estimators ($N$):** `{st.session_state.detector.n_estimators}`
        - **Contamination Rate ($c$):** `{st.session_state.detector.contamination:.2f}` ({st.session_state.detector.contamination*100:.0f}% expected outliers)
        - **Pre-scaling:** `sklearn.preprocessing.RobustScaler` (Median / IQR normalization)
        - **Random State:** `{st.session_state.detector.random_state}`
        """)
    with m_col2:
        st.markdown("""
        **Operational Decision Function:**
        $$\\text{Score}(x, n) = 2^{-\\frac{E(h(x))}{c(n)}}$$
        - Where $h(x)$ is the path length of observation $x$ in an isolation tree.
        - $c(n)$ is the average path length of unsuccessful searches in a Binary Search Tree (BST).
        - Observations with normalized score near $1.0$ are definite anomalies; scores below $0.5$ are normal inliers.
        """)

    st.markdown("---")
    st.markdown("##### ⚠️ Model Limitations & Engineering Considerations")
    
    st.markdown("""
    1. **Unsupervised Contamination Assumption:**  
       The contamination parameter sets an *a priori* proportion of outliers. In a dynamically shifting production workload, the true anomaly rate varies. Setting contamination too high generates false alarms; setting it too low risks missing stealthy degradations.
    
    2. **Concept Drift & Workload Seasonality:**  
       Static models trained on a single time window will degrade as server workloads shift (e.g., quarterly financial reconciliations, Black Friday traffic spikes on IBM Z mainframes). Continuous retraining pipelines or online sliding windows are recommended for production.
    
    3. **Synthetic Demonstration Notice:**  
       The pre-packaged and generated demo datasets in this dashboard are **synthetically modeled** for demonstration, testing, and evaluation purposes during the IBM Z Datathon 2026. They do **not** represent an actual proprietary production server.
    
    4. **Univariate vs. Multivariate Synergy:**  
       While the Isolation Forest detects multivariate anomalies (unusual combinations of CPU and network even if neither is individually pegged), subtle temporal sequences (e.g. slow, multi-day micro-leaks) are better complemented by recurrent temporal models (such as LSTM autoencoders or temporal convolution networks).
    """)


# -----------------------------------------------------------------------------
# TAB 5: IBM LinuxONE Readiness & Deployment
# -----------------------------------------------------------------------------
with tab_linuxone:
    st.markdown("#### 🖥️ IBM LinuxONE Community Cloud Deployment Guide")

    collector = SystemMetricsCollector()
    host_info = collector.get_system_info()

    # Host architecture badge
    arch = host_info.get("machine_arch", "Unknown")
    is_s390x = host_info.get("is_s390x", False)

    if is_s390x:
        st.success(f"🟢 Active Host Architecture: **s390x (IBM Z / LinuxONE Enterprise Server)**. Running natively on mainframe hardware!")
    else:
        st.info(f"ℹ️ Active Host Architecture: **{arch}** ({host_info.get('os')}). Application is running in development/evaluation mode and is prepared for deployment to IBM LinuxONE (s390x).")

    st.markdown("""
    ##### Why IBM LinuxONE for Enterprise AI & Anomaly Detection?
    IBM LinuxONE combines the agility of open-source Linux with enterprise mainframe reliability, scalability, and pervasive security:
    - **IBM Telum / z16 On-Chip AI Accelerator:** Ultra-low latency deep learning and anomaly detection at transactions-per-second enterprise scale.
    - **Pervasive Encryption & CPACF:** Hardware-accelerated cryptographic processing ensuring telemetry data remains encrypted in-flight and at-rest.
    - **Rock-Solid Uptime:** Up to 99.99999% availability (seven nines) for critical banking, healthcare, and enterprise workloads.
    
    ---
    ##### Deployment Instructions for IBM LinuxONE Community Cloud (s390x)
    Follow these exact commands to launch Z-Guard AI on a LinuxONE RHEL 9 or Ubuntu 22.04 / 24.04 s390x instance:
    """)

    st.code("""
# 1. SSH into your IBM LinuxONE Community Cloud VM
ssh linux1@<your-linuxone-ip>

# 2. Verify architecture (must return s390x)
uname -m
# Output: s390x

# 3. Update system and install Python 3.11+ development tools
# On RHEL / AlmaLinux on s390x:
sudo dnf install -y python3 python3-pip python3-devel git gcc gcc-c++
# On Ubuntu on s390x:
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git build-essential

# 4. Clone or copy project repository
git clone https://github.com/your-org/z-guard-ai.git
cd z-guard-ai

# 5. Create and activate a clean virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 6. Install dependencies
# Note: Streamlit, Pandas, NumPy, Scikit-learn, and Plotly have s390x wheels or build cleanly
pip install --upgrade pip
pip install -r requirements.txt

# 7. Run automated test suite to verify s390x execution
pytest tests/ -v

# 8. Launch Streamlit server on LinuxONE
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
    """, language="bash")

    st.markdown("""
    > [!NOTE]
    > **Status Disclosure:** This application has been designed with pure-Python and standard C-extension libraries (`scikit-learn`, `numpy`, `pandas`, `psutil`, `streamlit`) that are fully compatible with s390x architecture. Direct deployment testing on IBM LinuxONE Community Cloud should be performed using the verified script above.
    """)

# -----------------------------------------------------------------------------
# Bottom Footer & Live Streaming Auto-Refresh
# -----------------------------------------------------------------------------
st.markdown("""
<div class="disclaimer-banner">
    <b>IBM Z Datathon 2026 Notice:</b> Z-Guard AI is an educational and hackathon demonstration system.
    Synthetic datasets are generated algorithmically for testing and feature evaluation. Live host monitoring uses safe, read-only system calls via psutil.
</div>
""", unsafe_allow_html=True)

# Auto-refresh loop when continuous live monitoring is active
if source_choice == "⚡ Live Host Metrics (psutil)" and st.session_state.get("live_streaming", False):
    import time
    time.sleep(stream_interval)
    st.rerun()
