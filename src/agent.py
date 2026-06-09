from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Run the agent for a single input."""
