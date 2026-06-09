from typing import Any

from .agent import Agent


class Harness:
    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    def run(self, input_data: Any) -> Any:
        return self.agent.execute(input_data)
