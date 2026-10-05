#!/usr/bin/env python3
"""SolarHub Architectural Showcase - Standalone Simulation Demo.

This script simulates a dual-inverter setup:
- Inverter A (Hybrid, with High-Voltage Battery)
- Inverter B (Off-grid, supplemental string)
It ingests simulated telemetry, runs the aggregation engine, and executes an MCP tool call.
"""

import os
import sys
from datetime import datetime

# Allow execution from root or examples folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.models import InverterTelemetry, InverterType, BatteryState
from src.stubs import SolarStateEngineStub, DualInverterBridgeStub
from src.mcp_spec import SolarHubMcpProvider


def run_simulation():
    print("=" * 70)
    print("  SOLARHUB ARCHITECTURAL SHOWCASE -- SIMULATION DEMO")
    print("  Author: Alessandro Caliciotti (@RedScorpio83)")
    print("=" * 70)

    # 1. Initialize Hardware Bridge & State Engine
    print("\n[1/4] Initializing Hardware Bridge and State Engine...")
    bridge = DualInverterBridgeStub(bridge_name="ESP32_BL602_Gateway")
    bridge.connect_serial_bus("192.168.10.120", 8899)
    print("      [OK] Serial-over-TCP bus connected successfully.")

    engine = SolarStateEngineStub()
    mcp_provider = SolarHubMcpProvider(engine)

    # 2. Simulate Telemetry Stream from Inverter A (Hybrid)
    print("\n[2/4] Ingesting Live Telemetry from Inverter A (Hybrid)...")
    inv_a = InverterTelemetry(
        inverter_id="INV_A_HYBRID",
        inverter_type=InverterType.HYBRID,
        timestamp=datetime.utcnow(),
        pv_input_power_w=3450.0,
        pv_voltage_v=360.2,
        battery_soc_percent=92.5,
        battery_power_w=1200.0,
        battery_state=BatteryState.CHARGING,
        output_load_power_w=850.0,
        grid_feed_power_w=1400.0,
        inverter_temperature_c=39.4,
    )
    engine.register_inverter_feed(inv_a)
    print(f"      • Inverter A: PV={inv_a.pv_input_power_w}W | Battery={inv_a.battery_soc_percent}% | Grid Feed={inv_a.grid_feed_power_w}W")

    # 3. Simulate Telemetry Stream from Inverter B (Supplemental Off-Grid)
    print("\n[3/4] Ingesting Live Telemetry from Inverter B (Supplemental)...")
    inv_b = InverterTelemetry(
        inverter_id="INV_B_OFFGRID",
        inverter_type=InverterType.OFF_GRID,
        timestamp=datetime.utcnow(),
        pv_input_power_w=1820.0,
        pv_voltage_v=185.0,
        battery_soc_percent=88.0,
        battery_power_w=600.0,
        battery_state=BatteryState.CHARGING,
        output_load_power_w=420.0,
        grid_feed_power_w=0.0,
        inverter_temperature_c=36.8,
    )
    engine.register_inverter_feed(inv_b)
    print(f"      • Inverter B: PV={inv_b.pv_input_power_w}W | Battery={inv_b.battery_soc_percent}% | Load={inv_b.output_load_power_w}W")

    # 4. Compute State Balance
    flow = engine.compute_aggregated_power_flow()
    print("\n---------------- AGGREGATED MICROGRID BALANCE ----------------")
    print(f"  • Total Solar Generation:   {flow.total_pv_power_w:.1f} W")
    print(f"  • Total Household Demand:   {flow.total_load_power_w:.1f} W")
    print(f"  • Combined Battery Storage: {flow.combined_battery_soc_percent:.1f}%")
    print(f"  • Net Grid Balance:         {flow.net_grid_import_export_w:.1f} W (Exporting)")
    print(f"  • Self-Sufficiency Index:   {'YES (100% Autonomous)' if flow.is_self_sufficient else 'NO'}")
    print(f"  • System Status:            {flow.status_summary}")

    # 5. Model Context Protocol (MCP) Execution by AI Agent
    print("\n[4/4] Model Context Protocol (MCP) Tool Execution by AI Agent...")
    print("      Agent invokes: 'solarhub_status'")
    status_response = mcp_provider.handle_tool_call("solarhub_status", {})
    print(f"      Result: {status_response}")

    print("\n      Agent invokes: 'solarhub_load_balance_recommendation'")
    recommendation = mcp_provider.handle_tool_call("solarhub_load_balance_recommendation", {})
    print(f"      Recommendation: {recommendation}")

    print("\n" + "=" * 70)
    print("  SIMULATION COMPLETED WITH SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    run_simulation()
