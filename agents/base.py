from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class AgentOutput(BaseModel):
    agent_name:     str
    confidence:     float          # 0.0 – 1.0
    recommendation: str
    evidence:       list[str]
    metadata:       dict[str, Any] = {}


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, state: dict) -> AgentOutput:
        """Execute the agent and return a structured output."""
        ...
