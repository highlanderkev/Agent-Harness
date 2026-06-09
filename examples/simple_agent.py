import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agent import Agent
from src.harness import Harness


class EchoAgent(Agent):
    def execute(self, input_data):
        return f"Echo: {input_data}"


if __name__ == "__main__":
    harness = Harness(EchoAgent())
    print(harness.run("Hello Agent Harness!"))
