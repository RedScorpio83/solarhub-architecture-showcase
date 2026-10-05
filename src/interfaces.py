"""Core Architectural Interfaces and Abstract Base Classes for SolarHub."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from .models import InverterTelemetry, AggregatedPowerFlow, ControlCommand


class IInverterHardwareBridge(ABC):
    """Abstract interface for low-level serial/UART hardware communication."""

    @abstractmethod
    def connect_serial_bus(self, port_or_ip: str, baud_or_port: int) -> bool:
        """Establishes link with physical inverter or edge microcontroller bridge."""
        pass

    @abstractmethod
    def read_raw_frame(self, inverter_id: str) -> bytes:
        """Pulls unparsed bytes from the hardware bus."""
        pass

    @abstractmethod
    def parse_telemetry(self, raw_bytes: bytes) -> InverterTelemetry:
        """Decodes manufacturer-specific frame into a standardized InverterTelemetry model."""
        pass


class ITelemetryPublisher(ABC):
    """Event-driven messaging contract (e.g., MQTT / WebSockets)."""

    @abstractmethod
    def publish_inverter_state(self, telemetry: InverterTelemetry) -> None:
        """Publishes isolated telemetry snapshot to appropriate topic."""
        pass

    @abstractmethod
    def publish_aggregated_state(self, flow: AggregatedPowerFlow) -> None:
        """Broadcasts consolidated microgrid metrics to downstream listeners."""
        pass


class ISolarStateEngine(ABC):
    """Central analytical and balancing engine running in Proxmox container."""

    @abstractmethod
    def register_inverter_feed(self, telemetry: InverterTelemetry) -> None:
        """Ingests live telemetric sample from a registered inverter."""
        pass

    @abstractmethod
    def compute_aggregated_power_flow(self) -> AggregatedPowerFlow:
        """Calculates instantaneous multi-inverter balances and self-sufficiency indices."""
        pass

    @abstractmethod
    def evaluate_load_balancing_rules(self) -> Optional[ControlCommand]:
        """Runs rule-based or AI-assisted heuristic to determine optimal load routing."""
        pass


class IMcpToolProvider(ABC):
    """Contract for Model Context Protocol exposure to AI Agents."""

    @abstractmethod
    def get_available_tools(self) -> List[Dict]:
        """Returns JSON schema definitions of tools exposed to the LLM agent."""
        pass

    @abstractmethod
    def handle_tool_call(self, tool_name: str, arguments: Dict) -> Dict:
        """Executes audited MCP tool call requested by the AI model."""
        pass
