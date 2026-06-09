import unittest

from src.agent import Agent
from src.harness import Harness


class UpperAgent(Agent):
    def execute(self, input_data):
        return str(input_data).upper()


class TestHarness(unittest.TestCase):
    def test_runs_agent_execute(self):
        harness = Harness(UpperAgent())
        self.assertEqual(harness.run("starter"), "STARTER")


if __name__ == "__main__":
    unittest.main()
