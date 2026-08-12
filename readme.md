# Network Intrusion Detection System (NIDS)
Real-time unsupervised anomaly detection for network traffic

---

## 📌 TL;DR
NIDS adalah sistem deteksi intrusi jaringan yang bekerja secara real-time menggunakan pendekatan unsupervised anomaly detection. Sistem ini menganalisis lalu lintas jaringan, mengelompokkan paket data menjadi flows, mengekstrak fitur statistik, dan menggunakan 3 metode scoring untuk mengidentifikasi pola mencurigakan—tanpa memerlukan database signature atau labeled data.

Output utama: Alert real-time yang diklasifikasikan berdasarkan jenis serangan (PORT_SCAN, SYN_FLOOD, BRUTE_FORCE, GENERIC_ANOMALY) dengan severity (LOW/MEDIUM/HIGH), dikirim ke console dan Slack.

---

## 🎯 Problem

### Current Problem

| Masalah | Dampak |
|---------|--------|
| Signature-based detection (Snort/Suricata) memerlukan update rule terus-menerus | Tidak dapat mendeteksi serangan baru (zero-day) |
| Anomaly detection berbasis supervised membutuhkan labeled data | Sulit mendapatkan dataset attack yang lengkap |
| Tools monitoring menghasilkan terlalu banyak false positive | Analyst kewalahan dan serangan terlewat |
| Deteksi reaktif, bukan proaktif | Serangan baru terdeteksi setelah terjadi kerusakan |

### Why Existing Process Is Difficult

**Signature-based** → Hanya mendeteksi pola yang sudah dikenal, butuh maintenance terus-menerus.

**Supervised ML** → Membutuhkan dataset attack yang lengkap dan berlabel—sulit didapat di dunia nyata.

**Rule-based** → Sulit di-tune, sering menghasilkan false positive atau false negative.

**Manual monitoring** → Tidak scalable untuk traffic volume tinggi.

---

## 💡 Solution

NIDS mengatasi masalah ini dengan pendekatan unsupervised anomaly detection:

```
┌─────────────────────────────────────────────────────────────────┐
│                    NIDS Pipeline                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📡 Capture Packets    →  Sniff network traffic                 │
│         │                                                       │
│         ▼                                                       │
│  🔗 Flow Aggregation   →  Group by 5-tuple (src/dst IP/port)    │
│         │                                                       │
│         ▼                                                       │
│  📊 Feature Extraction  →  Hitung fitur statistik per flow      │
│         │                                                       │
│         ▼                                                       │
│  🎯 Anomaly Scoring    →  3 metode voting                       │
│         │                                                       │
│         ▼                                                       │
│  🚨 Alert Engine       →  Klasifikasi + deduplication           │
│         │                                                       │
│         ▼                                                       │
│  📱 Notification       →  Console + Slack                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Keunggulan

| Keunggulan | Keterangan |
|-----------|-----------|
| Unsupervised | Tidak perlu labeled data attack |
| Real-time | Deteksi dalam <5 detik |
| 3 Methods Voting | Z-Score, Mahalanobis, Isolation Forest |
| Zero-day Detection | Bisa mendeteksi serangan baru tanpa signature |
| Low False Positive | Composite voting mengurangi false alarm |
| Production-ready | Threading, connection pooling, cooldown |

---

## 🔧 How It Works

### Simple View

Sistem bekerja dengan cara:

1. **Mendengarkan lalu lintas jaringan** → Menangkap setiap paket data yang lewat
2. **Mengelompokkan paket** → Paket dari IP dan port yang sama dikelompokkan sebagai satu "flow"
3. **Menghitung statistik** → Dari setiap flow, dihitung fitur seperti kecepatan paket, ukuran rata-rata, dan jumlah port unik
4. **Membandingkan dengan normal** → Sistem belajar pola traffic normal, lalu membandingkan traffic baru
5. **Memberi skor anomali** → 3 metode berbeda memberikan skor, dan voting menentukan apakah anomali
6. **Mengirim alert** → Jika terdeteksi anomali, alert dikirim ke console dan Slack

### Technical View

#### Flow Aggregation

Setiap paket yang tertangkap dikelompokkan berdasarkan 5-tuple:

- `src_ip` (IP sumber)
- `dst_ip` (IP tujuan)
- `src_port` (port sumber)
- `dst_port` (port tujuan)
- `protocol` (TCP/UDP/ICMP)

Flow dianggap selesai ketika:

- Mendapat flag TCP FIN atau RST
- Idle selama FLOW_TIMEOUT_SECONDS (default 60 detik)

#### Feature Extraction

Setiap flow yang selesai diekstrak fitur-fiturnya:

| Feature | Deskripsi | Untuk Deteksi |
|---------|-----------|---------------|
| avg_packet_size | Rata-rata ukuran paket | Serangan DDoS (paket kecil) |
| packets_per_second | Kecepatan paket | SYN flood, port scan |
| syn_count | Jumlah SYN flags | SYN flood, port scan |
| syn_ack_ratio | Rasio SYN terhadap ACK | SYN flood |
| unique_dst_ports_from_src | Jumlah port unik yang disentuh dari satu source | Port scan, brute force |

#### Anomaly Scoring (3 Methods)

| Method | Type | Cara Kerja | Kelebihan |
|--------|------|-----------|----------|
| Z-Score | Univariate | Hitung standar deviasi dari baseline untuk tiap fitur | Sederhana, cepat, interpretable |
| Mahalanobis | Multivariate | Hitung jarak dengan mempertimbangkan korelasi antar fitur | Menangkap pola kombinasi fitur |
| Isolation Forest | ML | Model isolation-based outlier detection | Bagus untuk outlier detection |

**Voting:** Minimal 2 dari 3 metode setuju → anomali.

#### Alert Classification

| Alert Type | Pattern | Severity |
|-----------|---------|----------|
| PORT_SCAN | unique_dst_ports_from_src > 20 | MEDIUM |
| SYN_FLOOD | syn_ack_ratio > 5 dan packets_per_second > 50 | HIGH |
| BRUTE_FORCE | Banyak percobaan login ke port yang sama (22, 23, 21, 3389, 3306, 5432) | MEDIUM |
| GENERIC_ANOMALY | Anomali yang tidak termasuk di atas | LOW-MEDIUM |

#### Cooldown / Deduplication

Alert dari (src_ip, alert_type) yang sama hanya dikirim 1 kali per 5 menit (default) untuk mencegah spam.

---

## ✨ Key Features

### User-facing Features

| Feature | Deskripsi |
|---------|-----------|
| Real-time Network Monitoring | Capture traffic secara langsung |
| Anomaly Detection | Deteksi pola serangan otomatis |
| Alert Classification | Klasifikasi jenis serangan |
| Severity Rating | HIGH/MEDIUM/LOW |
| Slack Notifications | Alert dikirim ke Slack |
| Console Logging | Alert muncul di terminal |

### Technical Capabilities

| Capability | Implementasi |
|-----------|-------------|
| Packet Capture | Scapy + libpcap/Npcap |
| Flow Aggregation | 5-tuple grouping + timeout |
| Feature Engineering | Flow-level + Host-level (sliding window) |
| Baseline Statistics | Rolling mean/std dengan trimming (5% outlier) |
| Anomaly Scoring | Z-Score, Mahalanobis, Isolation Forest |
| Composite Voting | Minimal 2 dari 3 setuju |
| Alert Deduplication | Cooldown per (src_ip, alert_type) |
| Database | PostgreSQL (connection pooling) |
| Notifications | Console + Slack Webhook (async) |
| Background Model Refresh | Retrain periodik tanpa blocking |

---

## 📊 Risk Scoring

### Simple View

| Level | Arti | Tindakan |
|-------|------|---------|
| HIGH | Risiko tinggi, serangan terkonfirmasi | Perlu perhatian/review segera |
| MEDIUM | Ada pola mencurigakan | Perlu review |
| LOW | Tidak ada indikasi serangan | Tidak ada tindakan |

### Technical Detail

**Anomaly Score** = Skor composite dari 3 metode:

- **Z-Score:** |z| > 3 pada ≥ 2 fitur berbeda
- **Mahalanobis:** distance > 3.5
- **Isolation Forest:** score < -0.1

**Alert Severity:**

- **HIGH** → 3 dari 3 metode setuju
- **MEDIUM** → 2 dari 3 metode setuju
- **LOW** → 1 dari 3 metode setuju (tidak jadi alert, kecuali BRUTE_FORCE)

---

## 🏗️ Architecture

### Simple Architecture Explanation

Sistem terdiri dari 3 lapisan utama:

1. **Capture Layer** → Menangkap paket jaringan dan mengelompokkan menjadi flow
2. **Analysis Layer** → Mengekstrak fitur, menghitung baseline, dan menilai anomali
3. **Alert Layer** → Mengklasifikasi alert, mencegah spam, dan mengirim notifikasi

### Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            NIDS SYSTEM                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     CAPTURE LAYER                                   │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │    │
│  │  │ PacketSniffer│───▶│ PacketParser │───▶│ FlowTable           │   │    │
│  │  │ (Scapy)      │    │ (IP/TCP/UDP) │    │ (5-tuple grouping)   │   │    │
│  │  └──────────────┘    └──────────────┘    └──────────────────────┘   │    │
│  │                              │                    │                 │    │
│  │                              ▼                    ▼                 │    │
│  │                    ┌──────────────────────────────────────────┐     │    │
│  │                    │ FlowTimeoutManager (background thread)   │     │    │
│  │                    └──────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     ANALYSIS LAYER                                  │    │
│  │  ┌──────────────────────┐    ┌──────────────────────────────────┐   │    │
│  │  │ FeatureExtractor     │───▶│ FeatureRepository (PostgreSQL)  │    │   │
│  │  │ (Flow + Host level)  │    │                                  │   │    │
│  │  └──────────────────────┘    └──────────────────────────────────┘   │    │
│  │                              │                                      │    │
│  │                              ▼                                      │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │ DetectionEngine (3 methods voting)                           │   │    │
│  │  │  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐     │   │    │
│  │  │  │ Z-Score    │  │ Mahalanobis│  │ Isolation Forest    │     │   │    │
│  │  │  │ Scorer     │  │ Scorer     │  │ Scorer              │     │   │    │
│  │  │  └────────────┘  └────────────┘  └─────────────────────┘     │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                              │                                      │    │
│  │                              ▼                                      │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │ ModelRefreshManager (background, interval 120 detik)         │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                 │                                           │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     ALERT LAYER                                     │    │
│  │  ┌──────────────────────┐    ┌──────────────────────────────────┐   │    │
│  │  │ AlertClassifier      │───▶│ AlertCooldownTracker            │   │     │
│  │  │ (PORT_SCAN/SYN_FLOOD │    │ (deduplication per 5 menit)      │   │    │
│  │  │  BRUTE_FORCE/GENERIC)│    └──────────────────────────────────┘   │    │
│  │  └──────────────────────┘                    │                      │    │
│  │                              │               ▼                      │    │
│  │  ┌──────────────────────┐    ┌──────────────────────────────────┐   │    │
│  │  │ NotificationDispatcher│───▶│ AlertRepository (PostgreSQL)   │   │    │
│  │  │  (Console + Slack)   │    └──────────────────────────────────┘   │    │
│  │  └──────────────────────┘                                           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow

### User Flow

1. **Start Capture** → Jalankan `python scripts/run_capture.py`
2. **System Learns** → Traffic normal membentuk baseline (≈30-60 detik)
3. **Attack Simulation** → Jalankan `python scripts/traffic_generator_portscan.py`
4. **Alert** → Alert muncul di console dan Slack dalam <5 detik
5. **Verification** → Cek database: `SELECT * FROM alerts ORDER BY id DESC;`

### Internal Processing Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INTERNAL DATA FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Packet (Scapy)                                                             │
│         │                                                                   │
│         ▼                                                                   │
│  parse_packet() → PacketInfo (src_ip, dst_ip, src_port, dst_port, flags)    │
│         │                                                                   │
│         ▼                                                                   │
│  FlowTable.ingest() → Group by 5-tuple                                      │
│         │                                                                   │
│         ├── New flow → HostActivityTracker.register_connection_attempt()    │
│         │                                                                   │
│         ├── Existing flow → FlowState.register_packet()                     │
│         │                                                                   │
│         └── FIN/RST → _close_flow() → callback                              │
│         │                                                                   │
│         ▼                                                                   │
│  handle_flow_closed():                                                      │
│    1. FlowRepository.save(flow) → PostgreSQL (flows table)                  │
│    2. extract_flow_features() → FlowFeatures                                │
│    3. FeatureRepository.save() → PostgreSQL (flow_features table)           │
│    4. detection_engine.evaluate() → CompositeVerdict                        │
│         │                                                                   │
│         ▼                                                                   │
│  DetectionEngine.evaluate():                                                │
│    1. ZScoreScorer.score() → z-score per feature, vote                      │
│    2. MahalanobisScorer.score() → distance, vote                            │
│    3. IsolationForestScorer.score() → decision function, vote               │
│    4. Vote count ≥ 2 → is_anomaly = True                                    │
│         │                                                                   │
│         ▼                                                                   │
│  AlertEngine:                                                               │
│    1. classify_alert() → alert_type, severity                               │
│    2. cooldown_tracker.should_trigger() → check dedup                       │
│    3. AlertRepository.save() → PostgreSQL (alerts table)                    │
│    4. notification_dispatcher.dispatch() → Console + Slack                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Technology | Role | Why It Is Used |
|-----------|------|---|
| Python 3.11+ | Main language | Ecosystem untuk networking, ML, dan database |
| Scapy | Packet capture & manipulation | Library standar untuk manipulasi paket di Python |
| NumPy | Numerical computation | Efisien untuk operasi matriks (Mahalanobis) |
| SciPy | Mahalanobis distance | scipy.spatial.distance.mahalanobis |
| Scikit-learn | Isolation Forest | Implementasi Isolation Forest yang mature |
| psycopg2-binary | PostgreSQL driver | Connection pooling + performa tinggi |
| PostgreSQL 16 | Database | Reliable, JSONB support, indexing |
| Docker | Containerization | Reproducible environment, mudah dijalankan |
| pytest | Testing | Framework testing standard Python |
| requests | Slack webhook | HTTP client untuk kirim notifikasi |

---

## 📋 Requirements

### Required

| Requirement | Version | Keterangan |
|-------------|---------|-----------|
| Python | 3.11+ | Main language |
| Docker | 24.0+ | Untuk PostgreSQL |
| Docker Compose | 2.0+ | Untuk orchestration |
| Git | - | Version control |

### Recommended

| Requirement | Version | Keterangan |
|-------------|---------|-----------|
| RAM | 8GB+ | Untuk running capture + database |
| Npcap | 1.79+ | Windows packet capture (libpcap alternative) |
| libpcap | - | Linux packet capture (biasanya sudah terinstall) |

---

## 🚀 Quick Start

### Option A — Quick Start (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/your-username/nids.git
cd nids

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start PostgreSQL
docker compose -f docker/docker-compose.yml up -d postgres

# 4. Run migrations
cat db/migrations/*.sql | docker exec -i nids-postgres psql -U nids_user -d nids_db

# 5. Configure .env (copy from .env.example)
cp .env.example .env

# 6. Start capture (Administrator on Windows)
# Windows: Buka PowerShell sebagai Administrator
python scripts/run_capture.py

# 7. Generate traffic (di terminal lain)
python scripts/traffic_generator_normal.py
python scripts/traffic_generator_portscan.py
```

### Option B — Manual Setup

#### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Install dependencies untuk capture
# Windows: install Npcap dari https://npcap.com (centang "Install in WinPcap API-compatible Mode")
# Linux: sudo apt-get install libpcap-dev
```

#### 2. Setup Database

```bash
# Start PostgreSQL
docker compose -f docker/docker-compose.yml up -d postgres

# Run migrations
cat db/migrations/001_*.sql | docker exec -i nids-postgres psql -U nids_user -d nids_db
cat db/migrations/002_*.sql | docker exec -i nids-postgres psql -U nids_user -d nids_db
cat db/migrations/003_*.sql | docker exec -i nids-postgres psql -U nids_user -d nids_db

# Verify
docker exec -it nids-postgres psql -U nids_user -d nids_db -c "\dt"
```

#### 3. Configure Environment

Copy `.env.example` to `.env` and adjust:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nids_db
DB_USER=nids_user
DB_PASSWORD=nids_pass
CAPTURE_INTERFACE=Software Loopback Interface 1
FLOW_TIMEOUT_SECONDS=60
ANOMALY_MIN_VOTES=2
ANOMALY_MAHALANOBIS_THRESHOLD=3.5
ANOMALY_IFOREST_THRESHOLD=-0.1
ALERT_COOLDOWN_SECONDS=300
SLACK_WEBHOOK_URL=  # Optional
```

#### 4. Generate Baseline

```bash
# Set PYTHONPATH
export PYTHONPATH="$(pwd)/src"  # Linux/Mac
# atau
$env:PYTHONPATH = "C:\path\to\project\src"  # PowerShell

# Generate traffic normal (20+ kali)
python scripts/traffic_generator_normal.py
python scripts/traffic_generator_normal.py
# ... repeat 20x

# Build baseline
python -c "from nids.baseline.baseline_calculator import BaselineCalculator; BaselineCalculator.compute_and_store(window_minutes=120)"
```

#### 5. Run Capture

```bash
# Windows: Buka PowerShell sebagai Administrator
python scripts/run_capture.py
```

#### 6. Test Detection

```bash
# Terminal lain
python scripts/traffic_generator_portscan.py
```

---

## 📈 Example / Sample Result

### Input: Port Scan Attack

```
┌─────────────────────────────────────────────────────────────────┐
│  Traffic Generator: SYN packet ke port 1-50 dalam <1 detik      │
├─────────────────────────────────────────────────────────────────┤
│  Source IP: 127.0.0.1                                           │
│  Destination IP: 127.0.0.1                                      │
│  Pattern: 50 unique destination ports in 0.5 detik              │
└─────────────────────────────────────────────────────────────────┘
```

### Analysis Result

```
┌─────────────────────────────────────────────────────────────────┐
│  Detection Engine Evaluation                                    │
├─────────────────────────────────────────────────────────────────┤
│  Flow ID: 1105                                                  │
│  Source IP: 127.0.0.1                                           │
│  Destination Port: Various (1-50)                               │
│  Unique Destination Ports: 28                                   │
│                                                                 │
│  Z-Score:       36.786 (2 features exceeding threshold)         │
│  Mahalanobis:   23.1624 (threshold > 3.5)                       │
│  Isolation Forest: -0.144 (threshold < -0.1)                    │
│                                                                 │
│  Votes: Z-Score ✅ Mahalanobis ✅ Isolation Forest ✅          │
│  Result: ANOMALY                                                │
└─────────────────────────────────────────────────────────────────┘
```

### Alert Output

```
┌─────────────────────────────────────────────────────────────────┐
│  ALERT #5 [MEDIUM] PORT_SCAN                                    │
├─────────────────────────────────────────────────────────────────┤
│  Source: 127.0.0.1                                              │
│  Type: PORT_SCAN                                                │
│  Severity: MEDIUM                                               │
│  Detail: votes=2/3, unique_ports=28, zscore_max=1000000000.0    │
│  Triggered at: 2026-08-12 21:27:17                              │
└─────────────────────────────────────────────────────────────────┘
```

### Slack Notification

```
🚨 MEDIUM | PORT_SCAN
Source: 127.0.0.1
Detail: votes=2/3, unique_ports=28, zscore_max=1000000000.0
Alert ID: #5
```

---

## 📊 Testing

### Unit Tests

```bash
# Set PYTHONPATH
export PYTHONPATH="$(pwd)/src"
# atau PowerShell
$env:PYTHONPATH = "C:\path\to\project\src"

# Run all unit tests
pytest tests/unit -v

# Run specific test file
pytest tests/unit/test_flow_table.py -v
pytest tests/unit/test_packet_parser.py -v
pytest tests/unit/test_flow_feature_extractor.py -v
pytest tests/unit/test_host_activity_tracker.py -v
pytest tests/unit/test_zscore_scorer.py -v
pytest tests/unit/test_mahalanobis_scorer.py -v
pytest tests/unit/test_alert_classifier.py -v
pytest tests/unit/test_alert_cooldown_tracker.py -v
```

### Integration Tests

```bash
# Requires PostgreSQL running
docker compose -f docker/docker-compose.yml up -d postgres

# Run integration tests
pytest tests/integration -v
```

### Load Testing

```bash
python scripts/run_load_test.py
```

**Sample Result:**

```
============================================================
LOAD TEST DIMULAI
============================================================
Flow sebelum load test: 1645
Total packet: 10000 via 4 thread
✅ Selesai kirim 10000 packet dalam 14.30s (699 pps)
Menunggu 10 detik untuk pipeline selesai...
============================================================
LOAD TEST SELESAI
Flow setelah: 2330
Flow baru: 685
Capture rate: 6.9%
============================================================
```

**Interpretasi:** Sistem tetap stabil dengan 10,000 packet dalam 14 detik, tanpa crash. Capture rate 6.9% karena sebagian besar packet tidak membentuk flow lengkap (hanya SYN tanpa response).

---

## 📦 Docker

### Quick Docker Start

```bash
# Start PostgreSQL
docker compose -f docker/docker-compose.yml up -d postgres

# Check status
docker ps

# View logs
docker logs nids-postgres

# Stop
docker compose -f docker/docker-compose.yml down
```

### Environment Variables

Configure via `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| DB_HOST | localhost | PostgreSQL host |
| DB_PORT | 5432 | PostgreSQL port |
| DB_NAME | nids_db | Database name |
| DB_USER | nids_user | Database user |
| DB_PASSWORD | nids_pass | Database password |

### Production Configuration

Untuk production, pertimbangkan:

- **Persistent Volume** → Data tetap tersimpan setelah container restart
- **Resource Limits** → Set memory/CPU limits di docker-compose.yml
- **Logging** → Gunakan log driver production (json-file, loki, etc.)
- **Monitoring** → Integrasikan dengan Prometheus/Grafana

---

## 📁 Project Structure

```
network-intrusion-detection-system/
├── src/nids/                     # Main source code
│   ├── capture/                  # Packet capture & parsing
│   │   ├── sniffer.py            # Scapy wrapper
│   │   └── packet_parser.py      # IP/TCP/UDP parsing
│   ├── flow/                     # Flow aggregation
│   │   ├── flow_state.py         # Flow data structure
│   │   ├── flow_table.py         # In-memory flow management
│   │   └── flow_timeout_manager.py # Background timeout thread
│   ├── features/                 # Feature extraction
│   │   ├── flow_feature_extractor.py # Single-flow features
│   │   ├── feature_repository.py # Persist features
│   │   └── host_activity_tracker.py # Host-level sliding window
│   ├── persistence/              # Database operations
│   │   ├── db_connector.py       # Connection pooling
│   │   └── flow_repository.py    # Flow CRUD
│   ├── baseline/                 # Baseline statistics
│   │   ├── baseline_calculator.py # Rolling mean/std
│   │   └── baseline_repository.py # Persist baseline
│   ├── detection/                # Anomaly detection
│   │   ├── detection_engine.py   # Orchestrator
│   │   ├── zscore_scorer.py      # Univariate scoring
│   │   ├── mahalanobis_scorer.py # Multivariate scoring
│   │   ├── isolation_forest_scorer.py # ML scoring
│   │   ├── model_refresh_manager.py # Background retrain
│   │   └── classification/       # Alert classification
│   │       ├── brute_force_detector.py # Login attempt pattern
│   │       └── alert_classifier.py
│   ├── alerting/                 # Alert engine
│   │   ├── alert_cooldown_tracker.py # Deduplication
│   │   ├── alert_repository.py   # Persist alerts
│   │   └── notification_dispatcher.py # Console + Slack
│   └── config/                   # Configuration
│       └── settings.py           # Environment loading
├── scripts/                      # Executable scripts
│   ├── run_capture.py            # Main entry point
│   ├── traffic_generator_normal.py   # Normal traffic
│   ├── traffic_generator_portscan.py # Port scan attack
│   ├── traffic_generator_tcp.py      # TCP traffic
│   ├── run_baseline_update.py    # Baseline job
│   ├── run_load_test.py          # Performance test
│   └── query_flows.py            # Database query helper
├── db/                           # Database
│   ├── schema.sql                # Initial schema
│   └── migrations/               # Versioned migrations
│       ├── 001_create_flows_schema.sql
│       ├── 002_add_syn_ack_ratio_and_anomaly_scores.sql
│       └── 003_add_src_ip_to_alerts.sql
├── tests/                        # Tests
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
├── docker/                       # Docker configuration
│   └── docker-compose.yml
├── docs/                         # Documentation
│   └── demo-checklist.md
├── requirements.txt              # Python dependencies
├── Makefile                      # Common commands
└── .env.example                  # Example configuration
```

---

## ⚠️ Limitations

| Limitation | Current State | Impact | Planned Solution |
|-----------|---------------|--------|-----------------|
| Single interface capture | Hanya support 1 interface | Tidak bisa monitoring multiple network segments | Multi-interface support di roadmap |
| Non-production load testing | Load test hanya 10,000 packet | Belum tervalidasi untuk traffic volume besar | Load test dengan tools production-grade (locust) |
| Single-node deployment | Hanya berjalan di 1 instance | Tidak scalable horizontal | Distributed architecture |
| Static model refresh | Retrain setiap 120 detik | Mungkin tidak optimal untuk traffic yang sangat dinamis | Online learning / incremental update |
| No dashboard | Output hanya console + Slack | Tidak ada visualisasi real-time | React dashboard (planned) |
| No authentication | Tidak ada user authentication | Tidak aman untuk multi-user production | Auth layer (planned) |

---

## 🗺️ Roadmap

### ✅ Completed

- ☑ Packet capture & parsing
- ☑ Flow aggregation (5-tuple)
- ☑ Feature extraction (flow + host level)
- ☑ Baseline statistics (rolling mean/std)
- ☑ 3 anomaly scoring methods (Z-Score, Mahalanobis, Isolation Forest)
- ☑ Composite voting (2/3)
- ☑ Alert classification (PORT_SCAN, SYN_FLOOD, BRUTE_FORCE, GENERIC_ANOMALY)
- ☑ Alert cooldown/deduplication
- ☑ Slack notification
- ☑ Load testing
- ☑ Full documentation

### 📋 Planned

- □ Dashboard → React-based real-time visualization
- □ Multi-interface capture → Capture from multiple network interfaces
- □ Multi-node support → Distributed capture and analysis

### 🔮 Future

- □ Online learning → Model update tanpa retrain full
- □ Prometheus integration → Export metrics for monitoring
- □ Webhook support → Custom alert destinations (PagerDuty, etc.)
- □ TLS decryption → Analyze encrypted traffic
- □ Machine learning model persistence → Save/load trained models

---

## 🔧 Troubleshooting

### ModuleNotFoundError: No module named 'nids'

**Problem:** Python tidak menemukan module nids.

**Solution:** Set PYTHONPATH ke folder src.

```bash
# Linux/Mac
export PYTHONPATH="$(pwd)/src"

# Windows PowerShell
$env:PYTHONPATH = "C:\path\to\project\src"
```

### RuntimeError: Sniffing and sending packets is not available at layer 2

**Problem:** Scapy tidak bisa capture karena Npcap/libpcap tidak terinstall.

**Solution:**

- **Windows:** Install Npcap dari https://npcap.com (centang "Install in WinPcap API-compatible Mode")
- **Linux:** `sudo apt-get install libpcap-dev`

### Interface not found

**Problem:** Interface name di .env tidak sesuai.

**Solution:** Cek interface yang tersedia:

```bash
python -c "from scapy.all import show_interfaces; show_interfaces()"
```

Update `.env` dengan interface yang benar.

### Database connection failed

**Problem:** PostgreSQL tidak berjalan atau konfigurasi salah.

**Solution:**

```bash
# Check PostgreSQL status
docker ps

# Start PostgreSQL
docker compose -f docker/docker-compose.yml up -d postgres

# Check logs
docker logs nids-postgres

# Test connection
docker exec -it nids-postgres psql -U nids_user -d nids_db -c "\dt"
```

### Capture rate low in load test

**Problem:** Banyak packet tidak menjadi flow lengkap (hanya SYN).

**Reason:** Normal karena packet dikirim ke localhost dan banyak yang tidak mendapat response.

**Impact:** Tidak mempengaruhi deteksi anomali. Yang penting sistem tetap stabil.

---

## 🤝 Contributing

### Development Workflow

1. Fork repository
2. Clone fork: `git clone https://github.com/Tricke2D/nids.git`
3. Create branch: `git checkout -b feature/your-feature`
4. Make changes dan commit: `git commit -m "Description"`
5. Push: `git push origin feature/your-feature`
6. Create Pull Request

### Guidelines

- **Code style:** Black (`black src/ scripts/`)
- **Linting:** Ruff (`ruff check src/ scripts/`)
- **Tests:** Unit test untuk setiap new feature (`pytest tests/unit/ -v`)
- **Documentation:** Update README jika ada perubahan fitur
- **Commit messages:** Gunakan format descriptive

### Development Commands

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/ -v

# Format code
black src/ scripts/

# Lint code
ruff check src/ scripts/

# Run all checks
make test lint format
```

---

## 📄 License

MIT License

Copyright (c) 2026 [Muhamad Syukron Zakka]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...

[Full license text in LICENSE file]

---

## 👨‍💻 Author

Muhamad Syukron Zakka

- GitHub: @Tricke2D
- LinkedIn: mhdsyukronzakka

---

## 🙏 Acknowledgments

- **Scapy** - Packet manipulation library
- **Scikit-learn** - Isolation Forest implementation
- **PostgreSQL** - Reliable database
- **Slack** - Notification platform
