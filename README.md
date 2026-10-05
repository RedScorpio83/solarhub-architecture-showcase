# SolarHub — Architecture Showcase & Interface Specification

[![Architecture: Microservices](https://img.shields.io/badge/Architecture-Discoupled%20Microservices-blue.svg)](#)
[![Protocol: MQTT & MCP](https://img.shields.io/badge/Protocols-MQTT%20%7C%20MCP-orange.svg)](#)
[![Target: Proxmox LXC](https://img.shields.io/badge/Platform-Proxmox%20VE%20%7C%20Linux-green.svg)](#)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](#)

> **Public Specification & Architectural Showcase**  
> This repository presents the architectural blueprint, data contracts, abstract interfaces, and AI/MCP orchestration layers of the **SolarHub Dual-Inverter Energy Management Platform**.  
> *Proprietary low-level hardware drivers, industrial bus routines, and production secrets are intentionally abstracted into clean interfaces.*

---

## 🏛️ System Architecture

SolarHub is an event-driven, microservices-based distributed platform designed for real-time monitoring, intelligent load management, and autonomous AI-assisted operations across multi-inverter solar topologies.

```mermaid
flowchart TD
    subgraph Hardware_Edge ["Hardware Edge Layer"]
        INV1["Photovoltaic Inverter 1 (Hybrid)"]
        INV2["Photovoltaic Inverter 2 (Off-Grid)"]
        BRIDGE["BL602 / ESP32 UART-TCP Bridge"]
        INV1 -->|UART/Modbus| BRIDGE
        INV2 -->|UART/Modbus| BRIDGE
    end

    subgraph Messaging_Transport ["Telemetry & Ingestion Layer"]
        MQTT["Mosquitto MQTT Message Broker"]
        BRIDGE -->|Raw Telemetry Stream (JSON)| MQTT
    end

    subgraph Proxmox_LXC ["SolarHub Core (Proxmox LXC Container)"]
        INGEST["Telemetry Ingestor Service"]
        ENGINE["State Engine & Load Balancer"]
        API["REST & SSE Gateway"]
        MQTT -->|Topic Subscription| INGEST
        INGEST --> ENGINE
        ENGINE --> API
    end

    subgraph AI_Layer ["Agentic Orchestration (Model Context Protocol)"]
        MCPSRV["SolarHub Custom MCP Server"]
        LLM["AI Agent (Antigravity / LLM)"]
        API <-->|RPC / State| MCPSRV
        MCPSRV <-->|Tool Execution| LLM
    end
```

---

## 🌟 Key Architecture Pillars

1. **Decoupled Edge Telemetry:** Microcontrollers (ESP32 / Bouffalo Lab BL602) extract raw serial metrics from inverters and publish lightweight, structured payloads over MQTT.
2. **Deterministic State Processing:** The core engine processes multi-inverter telemetry at sub-second intervals, computing combined yields, battery SoC/SoH curves, and grid feed-in states.
3. **Model Context Protocol (MCP) Integration:** Exposes audited, type-safe tooling to AI coding assistants and autonomous agents, allowing LLMs to inspect solar production, query historical performance, and recommend optimal storage discharge profiles.
4. **Lightweight Containerization:** Designed for high-density deployment on Proxmox VE (LXC containers) with minimal memory footprint and zero external cloud reliance (Local-First philosophy).

---

## 📂 Repository Structure

```text
├── README.md                  # System overview and high-level architecture
├── ARCHITECTURE.md            # In-depth architectural specification and message flows
├── LICENSE                    # Apache 2.0 Open Specification License
├── src/
│   ├── __init__.py
│   ├── models.py              # Pydantic / Data contracts for telemetry & power flows
│   ├── interfaces.py          # Abstract interfaces (Bridge, Ingestion, MCP Handler)
│   ├── stubs.py               # Concrete service stubs with documented signatures
│   └── mcp_spec.py            # Model Context Protocol tool declarations for AI agents
└── examples/
    └── simulated_demo.py      # Standalone runnable demo with simulated multi-inverter telemetry
```

---

## 🚀 Running the Quick Simulation

You can verify the data structures and simulated telemetry without any hardware:

```bash
# Clone the repository
git clone https://github.com/RedScorpio83/solarhub-architecture-showcase.git
cd solarhub-architecture-showcase

# Run the standalone demonstration (no external dependencies needed)
python examples/simulated_demo.py
```

### Example Simulation Output:
```text
[SolarHub] Initializing Dual-Inverter Bridge (Inverter A: Hybrid, Inverter B: Off-Grid)...
[SolarHub] Subscribed to telemetry topic: 'solarhub/telemetry/inverters/live'
[Telemetry Ingest] Inverter A: PV=3450W | Battery=92.4% (Charging) | Load=820W
[Telemetry Ingest] Inverter B: PV=1820W | Battery=88.1% (Idle)     | Load=410W
[State Engine] Total Solar Production: 5270 W | Combined Battery Reserve: 90.25%
[MCP Tool Execution] Agent invoked 'solarhub_status' -> Health: OPTIMAL (Grid Feed-in: 4040 W)
```

---

## 🛡️ Intellectual Property & Interface Isolation

* **What is public:** Architectural designs, data schemas, abstract class hierarchies, MCP tool schemas, and simulated test benches.
* **What is encapsulated:** Hardware-specific registers, proprietary RS485/Modbus driver timings, and private network credentials.

---

## 👨‍💻 Author

**Alessandro Caliciotti**  
*Lead Enterprise Solutions & AI Systems Architect*  
* [GitHub: @RedScorpio83](https://github.com/RedScorpio83)
