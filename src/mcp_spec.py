"""Model Context Protocol (MCP) Interface Specification for SolarHub.

Exposes audited tools for AI coding assistants and autonomous agents.
"""

from typing import Dict, List
from .interfaces import IMcpToolProvider
from .stubs import SolarStateEngineStub


class SolarHubMcpProvider(IMcpToolProvider):
    """Exposes high-level solar telemetry and management capabilities to LLMs."""

    def __init__(self, engine: SolarStateEngineStub):
        self.engine = engine

    def get_available_tools(self) -> List[Dict]:
        """Returns JSON schema definitions of tools exposed to the AI agent."""
        return [
            {
                "name": "solarhub_status",
                "description": "Returns consolidated health, power flow, and battery status for the dual-inverter microgrid.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "include_raw_telemetry": {
                            "type": "boolean",
                            "description": "Set to true to include individual inverter snapshots alongside aggregated metrics.",
                        }
                    },
                },
            },
            {
                "name": "solarhub_load_balance_recommendation",
                "description": "Calculates whether instantaneous solar surplus warrants triggering secondary loads or batteries.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]

    def handle_tool_call(self, tool_name: str, arguments: Dict) -> Dict:
        """Executes tool requests dispatched by the LLM."""
        if tool_name == "solarhub_status":
            flow = self.engine.compute_aggregated_power_flow()
            return {
                "status": "success",
                "total_production_w": flow.total_pv_power_w,
                "total_consumption_w": flow.total_load_power_w,
                "combined_battery_soc": f"{flow.combined_battery_soc_percent}%",
                "grid_balance_w": flow.net_grid_import_export_w,
                "health_status": flow.status_summary,
            }
        elif tool_name == "solarhub_load_balance_recommendation":
            cmd = self.engine.evaluate_load_balancing_rules()
            if cmd:
                return {
                    "recommendation_active": True,
                    "action": cmd.action,
                    "parameters": cmd.parameters,
                    "justification": "Sufficient solar surplus detected with battery capacity above reserve threshold.",
                }
            return {
                "recommendation_active": False,
                "reason": "Production matches current consumption; no excess generation available.",
            }
        raise ValueError(f"Unknown MCP Tool: {tool_name}")
