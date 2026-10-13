"""
GuardianFleet - Base Agent Class
Provides shared initialization, model configuration, and Google ADK Agent wrapper logic.
"""

import os
from typing import List, Optional, Type
from pydantic import BaseModel

# Correct Google ADK / GenAI imports
from google.adk import Agent
from google.adk.tools import FunctionTool
from settings import *


class BaseAgent:
    """Base class for all GuardianFleet specialized enterprise sub-agents."""

    def __init__(
        self,
        name: str,
        instruction: str,
        tools: Optional[List[callable]] = None,
        output_schema: Optional[Type[BaseModel]] = None,
        model_name: str = "gemini-3.5-flash",
    ):
        self.name = name
        self.instruction = instruction
        self.output_schema = output_schema
        self.model = model_name

        if not gemini_api_key:
            raise ValueError(
                f"[{self.name}] GEMINI_API_KEY missing from environment!"
            )

        # Convert raw Python functions into Google ADK FunctionTools
        self.adk_tools = (
            [FunctionTool(fn) for fn in tools] if tools else []
        )

        # Instantiate Google ADK Agent
        self.adk_agent = Agent(
            name=self.name,
            model=self.model,
            instruction=self.instruction,
            tools=self.adk_tools,
            output_schema=self.output_schema,
        )

    def get_adk_agent(self) -> Agent:
        """Returns the configured underlying Google ADK Agent instance."""
        return self.adk_agent