"""
GuardianFleet - Main Execution Entrypoint (main.py)
---------------------------------------------------
Command-line interface and background worker runner that executes the 4-agent
orchestration loop, captures self-healing telemetry, and persists state memory.
"""

import sys
import os
import json
import asyncio
import argparse
import logging
from datetime import datetime

# Import master orchestrator
from orchestrator import GuardianFleetOrchestrator

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("guardian_fleet_execution.log", mode="a")
    ]
)
logger = logging.getLogger("GuardianFleetMain")


def parse_arguments():
    """Parses CLI arguments for custom policy asset auditing."""
    parser = argparse.ArgumentParser(
        description="GuardianFleet: Autonomous Enterprise Compliance & Self-Healing Agent Engine"
    )
    parser.add_argument(
        "--policy-id",
        type=str,
        default="policy_ca_labour_2026",
        help="Identifier of the operational policy or database asset to audit."
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="audit_state.json",
        help="Target JSON path for state memory persistence."
    )
    return parser.parse_args()


async def run_fleet_pipeline(policy_id: str, output_file: str):
    """Initializes and runs the multi-agent execution pipeline."""
    print("\n" + "=" * 70)
    print(" GUARDIAN FLEET: AUTONOMOUS ENTERPRISE COMPLIANCE ENGINE")
    print(" Track: Fortified Enterprise Fleet | Powered by Google ADK & Gemini")
    print("=" * 70 + "\n")

    logger.info(f"Initiating autonomous compliance run for target: '{policy_id}'...")
    
    # Instantiate Orchestrator
    orchestrator = GuardianFleetOrchestrator(state_file_path=output_file)
    
    # Execute workflow
    start_time = datetime.now()
    state_trace = await orchestrator.execute_workflow(policy_id=policy_id)
    execution_time = round((datetime.now() - start_time).total_seconds(), 2)

    # Print Summary to CLI
    print("\n" + "-" * 70)
    print(" 📊 EXECUTION TELEMETRY & AUDIT SUMMARY")
    print("-" * 70)
    print(f" • Session ID          : {state_trace.get('session_id')}")
    print(f" • Target Policy Asset : {state_trace.get('policy_id')}")
    print(f" • System Status       : {state_trace.get('status')}")
    print(f" • Latency             : {execution_time} seconds")
    
    metrics = state_trace.get("metrics", {})
    retries = metrics.get("self_healing_retries", 0)
    print(f" • Database Lookups    : {metrics.get('database_lookups', 0)}")
    print(f" • Validation Attempts : {metrics.get('patch_validation_attempts', 0)}")
    print(f" • Self-Healing Retries: {retries} {'(SELF-HEALED SUCCESSFULLY)' if retries > 0 else ''}")
    print("-" * 70)

    if state_trace.get("status") == "PENDING_HUMAN_APPROVAL":
        print("\n ⚠️  GATEKEEPER HOLD ENFORCED: Task paused at PENDING_HUMAN_APPROVAL.")
        print(f" 🌐 Launch Streamlit Dashboard to review and authorize patch: 'streamlit run app.py'")
    else:
        print(f"\n ❌ Execution encountered issue: {state_trace.get('error_details')}")

    print("\n" + "=" * 70 + "\n")


def main():
    args = parse_arguments()
    try:
        asyncio.run(run_fleet_pipeline(args.policy_id, args.output_file))
    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error during fleet execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()