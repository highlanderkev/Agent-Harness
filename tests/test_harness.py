import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.agent import Agent
from src.governance import HarnessConfig, LifecycleHooks
from src.harness import Harness


class UpperAgent(Agent):
    def execute(self, input_data):
        return str(input_data).upper()


class TestHarness(unittest.TestCase):
    def test_runs_agent_execute(self):
        harness = Harness(UpperAgent())
        self.assertEqual(harness.run("starter"), "STARTER")

    def test_persists_state_snapshot(self):
        with TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "state.json"
            harness = Harness(UpperAgent(), config=HarnessConfig(state_path=str(state_path)))

            result = harness.run("hello")

            self.assertEqual(result, "HELLO")
            self.assertTrue(state_path.exists())
            saved_state = harness.state_store.load()
            self.assertEqual(saved_state["input"], "hello")
            self.assertEqual(saved_state["output"], "HELLO")
            self.assertGreaterEqual(len(saved_state["context"]), 2)

    def test_runs_lifecycle_hooks(self):
        checkpoints: list[str] = []
        hooks = LifecycleHooks()
        hooks.register_session_start(lambda: checkpoints.append("session-start"))
        hooks.register_before_step(lambda state: checkpoints.append(f"before:{state.value}"))
        hooks.register_after_step(lambda state: checkpoints.append(f"after:{state.value}"))
        harness = Harness(UpperAgent(), lifecycle_hooks=hooks)

        harness.run("test")

        self.assertIn("session-start", checkpoints)
        self.assertTrue(any(item.startswith("before:") for item in checkpoints))
        self.assertTrue(any(item.startswith("after:") for item in checkpoints))

    def test_emits_evaluation_events(self):
        harness = Harness(UpperAgent())

        harness.run("metrics")

        event_types = [event["event_type"] for event in harness.evaluator.events]
        self.assertIn("state.enter", event_types)
        self.assertIn("state.exit", event_types)


if __name__ == "__main__":
    unittest.main()
