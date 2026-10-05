"""Encapsulated Service Stubs and Specification Implementations.

Note: Proprietary hardware protocol parsing, low-level serial timings, and
production credentials are encapsulated within the production binary.
These stubs demonstrate architectural wiring, data validation, and flow contracts.
"""

from datetime import datetime
from typing import Dict, List, Optional
from .interfaces import (
    IInverterHardwareBridge,
    ITelemetryPublisher,
    ISolarStateEngine,
    IMcpToolProvider,
)
from .models import (
    InverterTelemetry,
    AggregatedPowerFlow,
    ControlCommand,
    InverterType,
    BatteryState,
)


class DualInverterBridgeStub(IInverterHardwareBridge):
    """Bridge coordinating communication with physical inverters or edge microcontrollers."""

    def __init__(self, bridge_name: str = "BL602_Bridge_Node"):
        self.bridge_name = bridge_name
        self._connected = False

    def connect_serial_bus(self, port_or_ip: str, baud_or_port: int) -> bool:
        """Connects to the physical hardware or WiFi-to-Serial bridge."""
        # Hardware communication initialized via serial/TCP socket
        self._connected = True
        return self._connected

    def read_raw_frame(self, inverter_id: str) -> bytes:
        """Simulates pull of raw RS485 frame. Production implementation uses direct UART DMA."""
        if not self._connected:
            raise ConnectionError("Bridge not connected to hardware bus.")
        return b"\xAA\x55\x01\x00\x00\x00\x00\x00\xFF"

    def parse_telemetry(self, raw_bytes: bytes) -> InverterTelemetry:
        """Parses raw frames into standardized telemetry.

        In production, this handles specific inverter CRC-16 protocols.
        """
        # Architectural stub returns mock baseline snapshot
        return InverterTelemetry(
            inverter_id="INV_A_HYBRID",
            inverter_type=InverterType.HYBRID,
            timestamp=datetime.utcnow(),
            pv_input_power_w=3200.0,
            pv_voltage_v=340.5,
            battery_soc_percent=90.0,
            battery_power_w=1500.0,
            battery_state=BatteryState.CHARGING,
            output_load_power_w=750.0,
            grid_feed_power_w=950.0,
            inverter_temperature_c=42.1,
        )


class SolarStateEngineStub(ISolarStateEngine):
    """Core state engine that aggregates multi-inverter telemetry."""

    def __init__(self):
        self._cache: Dict[str, InverterTelemetry] = {}

    def register_inverter_feed(self, telemetry: InverterTelemetry) -> None:
        """Stores most recent valid telemetry sample in memory buffer."""
        self._cache[telemetry.inverter_id] = telemetry

    def compute_aggregated_power_flow(self) -> AggregatedPowerFlow:
        """Calculates consolidated energy flow across all active inverters."""
        if not self._cache:
            return AggregatedPowerFlow(
                timestamp=datetime.utcnow(),
                total_pv_power_w=0.0,
                total_load_power_w=0.0,
                total_battery_power_w=0.0,
                combined_battery_soc_percent=0.0,
                net_grid_import_export_w=0.0,
                is_self_sufficient=False,
                status_summary="NO_TELEMETRY_CONNECTED",
            )

        total_pv = sum(t.pv_input_power_w for t in self._cache.values())
        total_load = sum(t.output_load_power_w for t in self._cache.values())
        total_batt = sum(t.battery_power_w for t in self._cache.values())
        avg_soc = sum(t.battery_soc_percent for t in self._cache.values()) / len(self._cache)
        net_grid = sum(t.grid_feed_power_w for t in self._cache.values())

        is_self_sufficient = total_pv >= total_load

        return AggregatedPowerFlow(
            timestamp=datetime.utcnow(),
            total_pv_power_w=total_pv,
            total_load_power_w=total_load,
            total_battery_power_w=total_batt,
            combined_battery_soc_percent=round(avg_soc, 2),
            net_grid_import_export_w=net_grid,
            is_self_sufficient=is_self_sufficient,
            status_summary="OPTIMAL_OPERATION" if is_self_sufficient else "DEFICIT_COVERED_BY_STORAGE",
        )

    def evaluate_load_balancing_rules(self) -> Optional[ControlCommand]:
        """Evaluates whether excess solar power justifies activating aux loads."""
        flow = self.compute_aggregated_power_flow()
        if flow.net_grid_import_export_w > 1200.0 and flow.combined_battery_soc_percent > 85.0:
            return ControlCommand(
                command_id="CMD_DYN_LOAD_01",
                target_inverter_id="INV_A_HYBRID",
                action="ENABLE_SURPLUS_WATER_HEATING",
                parameters={"target_divert_power_w": 1000.0},
                issued_by="SOLARHUB_CORE_ENGINE",
            )
        return None
