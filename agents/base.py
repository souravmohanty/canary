import json
import re
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


def parse_json(text: str) -> dict:
    """Parse JSON from model output, stripping markdown code fences if present."""
    text = text.strip()
    # Strip ```json ... ``` or ``` ... ``` fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


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
