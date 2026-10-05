"""Data Contracts and Telemetry Models for SolarHub Platform."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class InverterType(str, Enum):
    HYBRID = "HYBRID"
    OFF_GRID = "OFF_GRID"
    GRID_TIE = "GRID_TIE"


class BatteryState(str, Enum):
    CHARGING = "CHARGING"
    DISCHARGING = "DISCHARGING"
    IDLE = "IDLE"
    FAULT = "FAULT"


@dataclass
class InverterTelemetry:
    """Represents an instantaneous snapshot of a single physical inverter."""
    inverter_id: str
    inverter_type: InverterType
    timestamp: datetime
    pv_input_power_w: float
    pv_voltage_v: float
    battery_soc_percent: float
    battery_power_w: float
    battery_state: BatteryState
    output_load_power_w: float
    grid_feed_power_w: float
    inverter_temperature_c: float
    active_alarms: List[str] = field(default_factory=list)


@dataclass
class AggregatedPowerFlow:
    """Consolidated energy flow across the entire multi-inverter microgrid."""
    timestamp: datetime
    total_pv_power_w: float
    total_load_power_w: float
    total_battery_power_w: float
    combined_battery_soc_percent: float
    net_grid_import_export_w: float
    is_self_sufficient: bool
    status_summary: str


@dataclass
class ControlCommand:
    """Defines a validated instruction dispatched to the edge hardware layer."""
    command_id: str
    target_inverter_id: str
    action: str  # e.g., 'SET_CHARGING_CURRENT', 'FORCE_GRID_BYPASS', 'TOGGLE_RELAY'
    parameters: Dict[str, float]
    issued_by: str  # e.g., 'MCP_AI_AGENT', 'AUTOMATION_CRON', 'USER'
    timestamp: datetime = field(default_factory=datetime.utcnow)
