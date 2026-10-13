"""
GuardianFleet - Agent 3: RemediationAgent
Generates policy/code patches, invokes validation tools, and performs autonomous self-healing retries.
"""

from base_agent import BaseAgent
from schemas import PatchPayload
from tools import code_patch_validator
from prompts import AgentPrompts



class RemediationAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="RemediationAgent",
            instruction=AgentPrompts.Remediation_prompt,
            tools=[code_patch_validator],
            output_schema=PatchPayload,
        )


# Export standalone ADK instance
remediation_agent_instance = RemediationAgent().get_adk_agent()