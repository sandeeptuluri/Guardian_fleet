"""
GuardianFleet - Agent 4: GatekeeperAgent
Evaluates patch risk, enforces Human-in-the-Loop (HITL) holds, and outputs approval action payloads.
"""

from base_agent import BaseAgent
from schemas import ApprovalActionPayload
from prompts import AgentPrompts


class GatekeeperAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="GatekeeperAgent",
            instruction=AgentPrompts.Gatekeeper_prompt,
            tools=[],
            output_schema=ApprovalActionPayload,
        )


# Export standalone ADK instance
gatekeeper_agent_instance = GatekeeperAgent().get_adk_agent()