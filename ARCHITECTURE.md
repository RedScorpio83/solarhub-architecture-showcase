# Technical Architecture & System Specifications

## 1. Domain Problem & Topography

Modern residential and semi-industrial solar plants frequently operate with **asymmetric dual-inverter setups**:
* **Primary Inverter (Hybrid):** Grid-tied, bidirectional battery storage management, dynamic anti-islanding.
* **Secondary Inverter (Off-Grid / Supplemental):** Dedicated auxiliary strings, discrete battery bank or DC-coupled bus.

Managing such topologies without relying on closed vendor clouds introduces several architectural challenges:
1. **Real-time telemetry synchronization:** Different inverters sample parameters at unaligned rates.
2. **Local-first autonomy:** Zero external dependency on vendor cloud services for critical load decisions.
3. **Audited AI Agent Orchestration:** Integrating Language Models into physical IoT infrastructure requires rigorous contract validation (Model Context Protocol).

---

## 2. Component Breakdown

### 2.1 Hardware Edge Bridge
* **Microcontroller:** ESP32-S3 / Bouffalo Lab BL602 RISC-V.
* **Bus Interface:** Dual RS485 / TTL UART interfaces converting proprietary framing into structured JSON frames.
* **Network Protocol:** MQTT with TLS / QoS 1 telemetry streaming.

### 2.2 Core Telemetry Engine
* **Container Runtime:** Proxmox LXC Container (Debian minimal).
* **Ingestion Pipeline:** Asynchronous event loop processing incoming frames in under `5ms`.
* **State Aggregation:** Aggregates instantaneous and accumulated metrics across all inverters.

### 2.3 Model Context Protocol (MCP) Interface
The MCP layer translates AI Agent intents into type-validated, secure read/action calls:
* `solarhub_status`: Provides instantaneous system-level health, power flow, and warnings.
* `solarhub_inspect_telemetry`: Emits granular, raw telemetry for real-time anomaly detection.
* `solarhub_execute_load_balance`: Enforces soft load thresholds and triggers automated relays based on solar surplus.

---

## 3. MQTT Topic Hierarchy

```text
solarhub/
├── telemetry/
│   ├── inverters/
│   │   ├── inverter_a/raw
│   │   └── inverter_b/raw
│   └── aggregated/live
├── control/
│   ├── inverter_a/commands
│   └── load_management/relays
└── status/
    ├── bridge/liveness
    └── system/alerts
```

---

## 4. Security & Safety Invariants

1. **Read-Heavy Isolation:** All AI Agent tools operate under read-only introspection by default.
2. **Hardware Watchdogs:** Edge bridges enforce autonomous fallback shutoff if the core engine fails to heartbeat within 15 seconds.
3. **Credential Segregation:** No private IP addresses or authentication tokens are embedded in edge binaries; secrets are injected via runtime environment variables.
