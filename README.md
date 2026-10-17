# 🛡️ Z-Guard AI: Real-Time Server Anomaly Detection
**Empowering Resilient Infrastructure for IBM Z & LinuxONE Enterprise Environments**
*Built for the IBM Z Datathon 2026*

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Isolation%20Forest-F7931E.svg)](https://scikit-learn.org/)
[![Architecture](https://img.shields.io/badge/Architecture-s390x%20%2F%20x86__64-0f62fe.svg)](https://www.ibm.com/it-infrastructure/linuxone)
[![Tests](https://img.shields.io/badge/Tests-10%20Passed-24a148.svg)](file:///tests/)

---

## 📌 Executive Summary
Mission-critical enterprise servers—especially IBM Z mainframes and IBM LinuxONE environments—power global banking, financial transactions, and healthcare backbones. In these systems, even minutes of unplanned downtime cost millions of dollars.

**Z-Guard AI** is an intelligent, real-time server anomaly detection web application that analyses continuous hardware telemetry (CPU, Memory, Disk I/O, and Network bandwidth), detects anomalous operational degradation using an unsupervised **Isolation Forest** tree ensemble, pinpoint-attributes the root-cause culprit metric, and equips system administrators with actionable mitigation playbooks before outages cascade.

---

## 🚀 Key Features

1. **Enterprise Monitoring Dashboard:**
   - Dark-mode, high-contrast interface inspired by the **IBM Carbon Design System**.
   - Synchronized 4-metric timeline (CPU, RAM, Disk, Network) with interactive tooltips and threshold overlays.
2. **Unsupervised Machine Learning with Isolation Forest:**
   - Detects both univariate resource exhaustion and subtle multivariate outlier interactions without requiring pre-labeled failure datasets.
   - Dynamic contamination slider (1% to 20%) allowing administrators to tune detection sensitivity on the fly.
3. **Continuous Anomaly Scoring & Metric Attribution:**
   - Calibrated 0–100% anomaly severity scoring using monotonic logistic mapping.
   - Automated root-cause diagnostics calculating standardized deviation ($\sigma$) from normal operational baseline.
   - Interactive multi-metric **Radar Attribution Chart** for deep-dive incident inspection.
4. **Actionable SysAdmin Remediation Playbook:**
   - Categorizes incidents into `CRITICAL`, `WARNING`, and `ELEVATED`.
   - Generates exact CLI triage commands (e.g., `top -c`, `iotop -o`, `free -m`, `ss -tulpn`) tailored to the specific culprit metric.
5. **Flexible Data Ingestion & Live Monitoring Deck:**
   - **Pre-packaged Demo Telemetry:** 10-hour diurnal server cycle with 5 realistic injected incident scenarios.
   - **Continuous Real-Time Live Streaming:** Direct hardware capture using `psutil` with configurable auto-streaming (1s, 2s, 3s, 5s) updating the dashboard live.
   - **Interactive Chaos Anomaly Injector:** One-click anomaly triggers (CPU Spike, RAM Leak, Disk Lock, Net Flood) to demonstrate immediate live ML detection and alert trigger during presentations.
   - **Synthetic Generator:** On-demand customizable simulation generator.
   - **Custom CSV Upload:** Forgiving schema validator with fuzzy column matching (`cpu` $\rightarrow$ `cpu_pct`, `ram` $\rightarrow$ `memory_pct`) and median imputation.
6. **IBM LinuxONE (s390x) Architecture Readiness:**
   - Built with pure-Python and standard C-extension libraries verified for cross-compilation on s390x.
   - Includes host architecture detection and automated setup scripts.

---

## 🏗️ System Architecture

```
+-------------------------------------------------------------------------+
|                  Z-Guard AI Streamlit Dashboard (app.py)                 |
|  - KPI Threat Scorecards          - Multi-Metric Synchronized Timeline  |
|  - Anomaly Alerts & Playbook      - Incident Root-Cause Radar Chart     |
|  - 2D Resource Clustering Map     - LinuxONE Deployment Guide           |
+-------------------------------------------------------------------------+
                                    |
          +-------------------------+-------------------------+
          |                                                   |
          v                                                   v
[ Data Ingestion Engine ]                           [ ML Detection Engine ]
 (src/data_loader.py)                                (src/detector.py)
 - CSV upload validator & cleaner                   - RobustScaler Normalization
 - Column fuzzy alias mapper                        - Scikit-Learn IsolationForest
 - Synthetic telemetry generator                    - Calibrated Sigmoid Anomaly Score
 - Live psutil host collector (src/metrics_collector.py) - Multi-Metric Attribution Engine
```

---

## 📂 Project Structure

```
IBMdatathon/
├── app.py                      # Main Streamlit web application & UI tabs
├── requirements.txt            # Production pinned dependencies
├── README.md                   # Complete documentation & 3-minute hackathon pitch
├── run.ps1                     # Quick start script for Windows PowerShell
├── run.sh                      # Quick start script for Linux / IBM LinuxONE (s390x)
├── run_jupyterlab.ps1          # One-click Windows JupyterLab launcher
├── run_jupyterlab.sh           # One-click Linux/s390x JupyterLab launcher
├── notebooks/
│   └── demo_walkthrough.ipynb  # Interactive Jupyter walkthrough notebook
├── src/
│   ├── __init__.py
│   ├── config.py               # Constants, metric thresholds, IBM Carbon color tokens
│   ├── data_loader.py          # CSV parsing, schema validation, synthetic data generator
│   ├── detector.py             # Isolation Forest ML pipeline, scoring & attribution
│   ├── metrics_collector.py    # Cross-platform live hardware metrics collector (psutil)
│   └── visualizer.py           # Plotly time-series, synchronized subplots & radar charts
├── data/
│   ├── sample_server_metrics.csv       # Pre-packaged 600-row demo telemetry with 5 scenarios
│   ├── test_synthetic_scenarios.csv   # 250-row test dataset
│   └── clean_baseline_metrics.csv     # 200-row normal diurnal baseline
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py     # Tests for generation, fuzzy mapping, NaN imputation
│   ├── test_detector.py        # Tests for training, outlier scoring, edge cases
│   └── test_metrics.py         # Tests for psutil snapshot schema & boundaries
├── scripts/
│   ├── generate_datasets.py    # Standalone dataset regeneration script
│   ├── generate_notebook.py    # Standalone walkthrough notebook builder
│   └── verify_app_headless.py  # End-to-end headless pipeline verifier
└── docs/
    └── LINUXONE_DEPLOYMENT.md  # Step-by-step IBM LinuxONE Community Cloud (s390x) guide
```

---

## ⚙️ Quick Start Installation

### Prerequisites
- Python 3.10 to 3.13
- Git

### Windows
```powershell
# 1. Clone repository
git clone https://github.com/akhand-mishra-1/Z-Guard-AI.git
cd Z-Guard-AI

# 2. Run automated PowerShell launcher (creates venv, installs dependencies, launches app)
.\run.ps1
```

### Linux / macOS / IBM LinuxONE (s390x)
```bash
# 1. Clone repository
git clone https://github.com/akhand-mishra-1/Z-Guard-AI.git
cd Z-Guard-AI

# 2. Run automated bash launcher
chmod +x run.sh
./run.sh
```

### Running on JupyterLab
```powershell
# Windows:
.\run_jupyterlab.ps1

# Linux / macOS / s390x:
./run_jupyterlab.sh
```
Then open `notebooks/demo_walkthrough.ipynb` and click **Run $\rightarrow$ Run All Cells**.

### Manual Setup
```bash
python3 -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Dashboard will open in your browser at: `http://localhost:8501`

---

## 🧪 Automated Testing & Verification

Run the automated test suite covering ML training, data validation, and telemetry capture:

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_data_loader.py::test_synthetic_telemetry_generation PASSED
tests/test_data_loader.py::test_fuzzy_column_mapping PASSED
tests/test_data_loader.py::test_missing_column_validation_failure PASSED
tests/test_data_loader.py::test_missing_values_imputation PASSED
tests/test_detector.py::test_detector_fit_and_predict_lifecycle PASSED
tests/test_detector.py::test_extreme_outlier_detection PASSED
tests/test_detector.py::test_unfitted_detector_raises_error PASSED
tests/test_detector.py::test_insufficient_training_data_error PASSED
tests/test_metrics.py::test_system_info_retrieval PASSED
tests/test_metrics.py::test_snapshot_schema_and_ranges PASSED

============================= 10 passed in 2.35s ==============================
```

---

## 🔍 Injected Incident Scenarios in Demo Data

The pre-packaged telemetry (`data/sample_server_metrics.csv`) demonstrates 5 real-world enterprise infrastructure incident patterns:

| Scenario | Incident Signature | Root Cause Attribution | Recommended Action |
|---|---|---|---|
| **Scenario 1** | CPU pegged at 95–99% for 25 min | CPU Runaway Thread / Heavy Compute | `top -c` or `ps -eo pid,%cpu,cmd` |
| **Scenario 2** | RAM monotonically climbing 55% $\rightarrow$ 98% | Memory Leak Accumulation | `free -m`, restart leaky container |
| **Scenario 3** | Disk utilization pinned at 94–99% | Storage Thrashing / DB Lock | `iotop -o`, `iostat -xz 1` |
| **Scenario 4** | Network bandwidth spiking to 950 Mbps | Network Influx / Traffic Flood | `ss -tulpn`, firewall ingress filtering |
| **Scenario 5** | Simultaneous saturation across all metrics | Multi-Resource System Cascade | Trigger failover, inspect core dump |

---

## 🎙️ Three-Minute Hackathon Presentation Pitch Script

Use this script during your 3-minute hackathon demo:

### ⏱️ [0:00 – 0:45] The Problem & The Mission
> *"Judges, enterprise servers—particularly IBM Z and LinuxONE systems—process trillions of dollars in transactions daily. When server anomalies occur, traditional threshold alarms fail: they either trigger hundreds of noisy false alarms, or they detect the outage too late after the service has already collapsed.*
>
> *Introducing **Z-Guard AI**: an intelligent, real-time server anomaly detection platform built specifically for the IBM Z Datathon 2026. Z-Guard AI shifts server monitoring from reactive post-mortems to proactive, machine-learning-driven defense."*

### ⏱️ [0:45 – 1:45] Live Dashboard & Anomaly Detection
> *(Open the dashboard at `http://localhost:8501`)*
>
> *"Here on the main dashboard, we monitor four foundational server metrics: CPU, Memory, Disk, and Network bandwidth. In the sidebar, we can ingest live host telemetry, upload custom datasets, or explore our pre-packaged 10-hour telemetry containing normal diurnal cycles and five injected enterprise incident scenarios.*
>
> *Notice our top KPI scorecards: our unsupervised **Isolation Forest** has continuously evaluated the telemetry, identifying 60 anomalies with zero hardcoding. When we navigate to our **Telemetry Timeline**, you immediately see red diamond markers where anomalous conditions occur—such as this distinct memory leak ramp where RAM steadily creeps to 98%.*
>
> *Next, let's open the **Anomaly Alerts & Playbook** tab. Notice we don't just say 'an anomaly occurred.' Z-Guard AI calculates metric attribution: it tells the administrator that Memory is at 96.2%, which is 3.4 standard deviations above baseline, and immediately recommends the exact command to diagnose the process."*

### ⏱️ [1:45 – 2:30] Machine Learning Engine & Root-Cause Radar
> *(Click on a timestamp in the Radar Deep-Dive)*
>
> *"In our **Radar Deep-Dive**, we can inspect any incident. The green polygon represents our normal operational baseline; the red outline shows the anomalous distortion in real time.*
>
> *Under the hood, Isolation Forest uses recursive random partitioning: anomalous points are isolated at shallow tree depths because they are few and distant. We pass all features through `RobustScaler` to ensure resilience against skewed distributions, and calculate continuous anomaly severity scores using a calibrated sigmoid function."*

### ⏱️ [2:30 – 3:00] IBM LinuxONE Synergy & Conclusion
> *(Switch to the **IBM LinuxONE Readiness** tab)*
>
> *"Z-Guard AI is designed for enterprise deployment on **IBM LinuxONE Community Cloud**. Our architecture detection automatically checks for the s390x mainframe architecture, and our deployment guide provides a zero-friction path to running as a 24/7 systemd service on LinuxONE instances.*
>
> *Z-Guard AI delivers proactive, explainable, and accessible server monitoring—protecting the mission-critical infrastructure of tomorrow. Thank you, and we welcome your questions!"*

---

## ⚖️ Model Limitations & Ethical Disclosures

1. **Synthetic Telemetry Disclaimer:**  
   The sample and generated datasets provided with this project are generated algorithmically for demonstration, benchmarking, and hackathon evaluation. They do **not** represent a proprietary live production enterprise server.
2. **IBM LinuxONE Testing Status:**  
   The application codebase and dependencies have been structured and verified for s390x architecture compatibility. In accordance with datathon integrity rules, deployment on live IBM LinuxONE Community Cloud instances should be verified following the instructions in [`docs/LINUXONE_DEPLOYMENT.md`](file:///docs/LINUXONE_DEPLOYMENT.md).
3. **Contamination Rate Parameter:**  
   Isolation Forest relies on an assumed contamination proportion ($c$). In production, continuous monitoring pipelines should incorporate adaptive thresholding or online feedback to account for seasonal workload shifts.

---

## 📜 License
Licensed under the [Apache License 2.0](LICENSE). Built for educational and competition purposes for the IBM Z Datathon 2026.
