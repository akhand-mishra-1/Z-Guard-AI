# IBM LinuxONE (s390x) Deployment Guide
**Z-Guard AI: Real-Time Server Anomaly Detection**
*Prepared for IBM Z Datathon 2026*

---

## 1. Executive Summary & Hardware Context

IBM LinuxONE is an enterprise-class Linux server powered by IBM mainframe hardware (IBM z16 / LinuxONE Emperor 4 & Rockhopper 4). Unlike standard commodity x86 servers, LinuxONE is built upon the **s390x (big-endian 64-bit)** architecture, offering:

- **Ultra-low latency inference:** On-chip integrated AI accelerator (IBM Telum processor) capable of handling enterprise transactions at speed.
- **Pervasive Encryption:** Hardware Cryptographic Coprocessors (CPACF & Crypto Express) delivering line-rate encryption for in-flight and at-rest telemetry data.
- **Unrivaled Reliability:** 99.99999% availability ("seven nines"), preventing downtime during mission-critical operations.

Z-Guard AI is designed from the ground up to monitor LinuxONE LPARs (Logical Partitions) and KVM virtual guests, detecting anomalies in CPU utilization, memory leakage, storage I/O lockup, and network flooding.

---

## 2. Operating System & Architecture Compatibility

Before deploying, verify that your environment is running the s390x architecture:

```bash
# Verify system architecture
uname -m
# Expected output on LinuxONE:
# s390x
```

### Dependency Architecture Analysis on s390x:
| Package | Architecture Support | s390x Installation Method | Notes |
|---|---|---|---|
| **Python** | Native s390x | Distribution package (`dnf` / `apt`) | Python 3.10, 3.11, 3.12, 3.13 supported |
| **Streamlit** | Pure Python (`py3-none-any`) | PyPI `pip install streamlit` | Universal wheel; runs on any CPU architecture |
| **NumPy & Pandas** | s390x wheels / C-extensions | `pip install` or distro repos | Pre-compiled wheels or compiled via GCC |
| **Scikit-Learn** | s390x wheels / C-extensions | `pip install` or distro repos | Uses OpenBLAS / LAPACK on s390x |
| **Plotly** | Pure Python (`py3-none-any`) | PyPI `pip install plotly` | Universal wheel |
| **psutil** | C-extension with s390x support | Compiled during `pip install` | Standard POSIX `/proc` reader on Linux |

---

## 3. Step-by-Step Deployment on IBM LinuxONE Community Cloud

The **IBM LinuxONE Community Cloud** provides free access to virtual machine instances running Linux on s390x for students and developers.

### Step 1: Provision your Virtual Server
1. Sign up / log in to [IBM LinuxONE Community Cloud](https://developer.ibm.com/articles/get-started-with-ibm-linuxone/).
2. Request a Virtual Server instance selecting **Red Hat Enterprise Linux (RHEL 9)** or **Ubuntu 22.04/24.04 LTS (s390x)**.
3. Add your SSH Public Key and note your assigned external IP address (`<LINUXONE_IP>`).

### Step 2: Connect via SSH
```bash
ssh linux1@<LINUXONE_IP>
```

### Step 3: Install System Prerequisites
On **RHEL 9 / AlmaLinux (s390x)**:
```bash
sudo dnf update -y
sudo dnf install -y python3 python3-pip python3-devel git gcc gcc-c++ openblas-devel
```

On **Ubuntu 22.04 / 24.04 (s390x)**:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git build-essential libopenblas-dev
```

### Step 4: Clone the Z-Guard AI Repository
```bash
git clone https://github.com/akhand-mishra-1/Z-Guard-AI.git
cd Z-Guard-AI
```

### Step 5: Configure Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 6: Run Automated Verification Tests
Run the test suite on the s390x instance to verify mathematical and architectural correctness:
```bash
pytest tests/ -v
```
All tests should pass without architecture-specific truncation or endianness faults.

### Step 7: Launch the Web Dashboard
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Access the dashboard via your browser:
```
http://<LINUXONE_IP>:8501
```

*(If direct port 8501 is blocked by firewall, use an SSH tunnel:*
`ssh -L 8501:localhost:8501 linux1@<LINUXONE_IP>`
*and open `http://localhost:8501` locally).*

---

## 4. Production Service Configuration (Systemd)

To run Z-Guard AI as a persistent 24/7 background service on IBM LinuxONE:

1. Create a systemd service file:
```bash
sudo tee /etc/systemd/system/zguard.service <<EOF
[Unit]
Description=Z-Guard AI Anomaly Detection Daemon
After=network.target

[Service]
Type=simple
User=linux1
WorkingDirectory=/home/linux1/z-guard-ai
ExecStart=/home/linux1/z-guard-ai/.venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF
```

2. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable zguard
sudo systemctl start zguard
sudo systemctl status zguard
```

---

## 5. Architectural Disclosure & Testing Status

> [!IMPORTANT]
> **Deployment Status:**
> Z-Guard AI is architected using portable, s390x-compatible packages (`streamlit`, `scikit-learn`, `pandas`, `numpy`, `plotly`, `psutil`). This deployment guide provides the exact configuration required to run on IBM LinuxONE Community Cloud.
>
> In accordance with datathon integrity guidelines, **this project does not claim that live LinuxONE testing was conducted unless verified directly on an active s390x instance.** Evaluators can immediately test and confirm compatibility using the steps outlined above.
