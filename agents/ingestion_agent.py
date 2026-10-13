"""
GuardianFleet - Agent 1: IngestionAgent
Extracts and structures raw statutory laws and operational policies into RuleSet schemas.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from base_agent import BaseAgent
from schemas import RuleSet
from tools import database_lookup_tool
from prompts import AgentPrompts


class IngestionAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="IngestionAgent",
            instruction=AgentPrompts.Ingestion_prompt,
            tools=[database_lookup_tool],
            output_schema=RuleSet,
        )


# Export standalone ADK instance
ingestion_agent_instance = IngestionAgent().get_adk_agent()