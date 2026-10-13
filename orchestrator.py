"""
GuardianFleet - Master Multi-Agent Orchestrator (orchestrator.py)
------------------------------------------------------------------
Chains IngestionAgent, AuditorAgent, RemediationAgent, and GatekeeperAgent 
into a robust, fault-tolerant Google ADK SequentialAgent pipeline.

Handles:
- Sequential agent delegation and trajectory logging
- Edge-case protection (timeouts, missing data, schema fallbacks)
- Self-healing retry metric tracking from custom tools
- State persistence into audit_state.json for Memory Bank & Dashboard UI
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from google.adk import SequentialAgent
from google.adk.runners import Runner

# Import sub-agent instances
from agents.ingestion_agent import ingestion_agent_instance
from agents.auditor_agent import auditor_agent_instance
from agents.remediation_agent import remediation_agent_instance
from agents.gatekeeper_agent import gatekeeper_agent_instance

# Import telemetry metrics from custom tools
from tools import get_tool_metrics, reset_tool_metrics

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("GuardianOrchestrator")


class GuardianFleetOrchestrator:
    """
    Master Orchestration Engine governing the lifecycle of the enterprise compliance fleet.
    """

    def __init__(self, state_file_path: str = "audit_state.json"):
        self.state_file_path = state_file_path
        
        logger.info("Initializing GuardianFleet Orchestrator with 4 Sub-Agents...")
        
        # 1. Compose the 4-Agent Pipeline into a Google ADK SequentialAgent
        self.sequential_pipeline = SequentialAgent(
            name="GuardianFleetMasterPipeline",
            agents=[
                ingestion_agent_instance,
                auditor_agent_instance,
                remediation_agent_instance,
                gatekeeper_agent_instance
            ]
        )
        
        # 2. Instantiate the Google ADK AgentRunner
        self.runner = Runner(agent=self.sequential_pipeline)
        logger.info("Google ADK SequentialAgent Pipeline initialized successfully.")

    async def execute_workflow(self, policy_id: str = "policy_ca_labour_2026") -> Dict[str, Any]:
        """
        Executes the end-to-end multi-agent audit, remediation, and gatekeeping workflow.
        
        Args:
            policy_id (str): Target enterprise policy asset identifier.
            
        Returns:
            Dict[str, Any]: Structured execution state log for persistence and UI rendering.
        """
        start_time = datetime.now()
        reset_tool_metrics()  # Reset metrics for clean telemetry tracking
        
        logger.info(f"Starting execution workflow for policy asset: '{policy_id}'...")
        
        # Construct explicit, deterministic prompt context for the ADK runner
        input_prompt = (
            f"Execute an end-to-end legal compliance audit and self-healing remediation workflow. "
            f"Target Policy Asset ID: '{policy_id}'. "
            f"Jurisdiction: California State Laws (CA Labor Code Sec 512). "
            f"1. Ingest policy rules. 2. Audit for non-compliance. "
            f"3. Generate and validate self-healing patch. 4. Hold for Gatekeeper approval."
        )

        trace_log: Dict[str, Any] = {
            "session_id": f"session_{int(start_time.timestamp())}",
            "policy_id": policy_id,
            "status": "PROCESSING",
            "start_time": start_time.isoformat(),
            "execution_steps": [],
            "error_details": None,
            "metrics": {},
            "final_payload": None
        }

        try:
            # --- EXECUTE MULTI-AGENT ADK RUNNER ---
            logger.info("Dispatching prompt to Google ADK Runner...")
            pipeline_result = await self.runner.run_async(input_prompt)
            
            end_time = datetime.utcnow()
            latency_sec = round((end_time - start_time).total_seconds(), 2)
            
            # Retrieve self-healing telemetry counters from tool state
            metrics = get_tool_metrics()
            self_healing_retries = max(0, metrics.get("patch_validation_attempts", 1) - 1)
            
            # Construct structured output state payload
            trace_log.update({
                "status": "PENDING_HUMAN_APPROVAL",
                "end_time": end_time.isoformat(),
                "latency_seconds": latency_sec,
                "metrics": {
                    "database_lookups": metrics.get("db_lookups", 1),
                    "patch_validation_attempts": metrics.get("patch_validation_attempts", 2),
                    "self_healing_retries": self_healing_retries,
                    "self_healed_status": True if self_healing_retries > 0 else False
                },
                "final_payload": pipeline_result.output if hasattr(pipeline_result, "output") else str(pipeline_result)
            })
            
            logger.info(f"Workflow executed successfully in {latency_sec}s. Self-Healing Retries: {self_healing_retries}")

        except Exception as e:
            end_time = datetime.utcnow()
            logger.error(f"Workflow execution encountered an error: {str(e)}", exc_info=True)
            
            # Deterministic Fallback Guardrail (Prevents app crashes on edge errors)
            trace_log.update({
                "status": "REQUIRES_MANUAL_INTERVENTION",
                "end_time": end_time.isoformat(),
                "latency_seconds": round((end_time - start_time).total_seconds(), 2),
                "error_details": str(e),
                "metrics": get_tool_metrics(),
                "final_payload": {
                    "error_summary": "Agent pipeline encountered an unhandled exception or rate limit.",
                    "fallback_action": "Flagged for manual compliance review."
                }
            })

        # --- PERSIST STATE TO MEMORY BANK STORE ---
        self._persist_state(trace_log)
        return trace_log

    def _persist_state(self, state_data: Dict[str, Any]) -> None:
        """Writes current execution trajectory safely to JSON state store for Memory Bank & Streamlit UI."""
        try:
            temp_file = f"{self.state_file_path}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2, default=str)
            os.replace(temp_file, self.state_file_path)
            logger.info(f"State telemetry persisted successfully to '{self.state_file_path}'.")
        except Exception as e:
            logger.error(f"Failed to persist state memory file: {str(e)}")


# Singleton instance generator
def get_orchestrator() -> GuardianFleetOrchestrator:
    return GuardianFleetOrchestrator()


if __name__ == "__main__":
    # Test execution when run directly
    orchestrator = get_orchestrator()
    asyncio.run(orchestrator.execute_workflow("policy_ca_labour_2026"))
