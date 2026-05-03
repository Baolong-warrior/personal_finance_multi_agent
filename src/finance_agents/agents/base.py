from __future__ import annotations

from abc import ABC, abstractmethod

from finance_agents.models import AgentResult, Blackboard


class BaseAgent(ABC):
    name: str = "BaseAgent"

    @abstractmethod
    def run(self, blackboard: Blackboard) -> AgentResult:
        raise NotImplementedError
