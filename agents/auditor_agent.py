"""
GuardianFleet - Agent 2: AuditorAgent
Audits operational policy assets against statutory rules and identifies compliance violations.
"""

from base_agent import BaseAgent
from schemas import ComplianceReport
from tools import database_lookup_tool
from prompts import AgentPrompts


class AuditorAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="AuditorAgent",
            instruction=AgentPrompts.Auditor_prompt,
            tools=[database_lookup_tool],
            output_schema=ComplianceReport,
        )


# Export standalone ADK instance
auditor_agent_instance = AuditorAgent().get_adk_agent()