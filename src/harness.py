from typing import Any

from .agent import Agent
from .governance import (
    ContextManager,
    EvaluationInterface,
    HarnessConfig,
    HarnessState,
    LifecycleHooks,
    StateStore,
    ToolRegistry,
)


class Harness:
    def __init__(
        self,
        agent: Agent,
        config: HarnessConfig | None = None,
        tool_registry: ToolRegistry | None = None,
        context_manager: ContextManager | None = None,
        state_store: StateStore | None = None,
        lifecycle_hooks: LifecycleHooks | None = None,
        evaluator: EvaluationInterface | None = None,
    ) -> None:
        self.agent = agent
        self.config = config or HarnessConfig()
        self.tool_registry = tool_registry or ToolRegistry()
        self.context_manager = context_manager or ContextManager(
            window_size=self.config.context_window_size,
            offload_threshold=self.config.offload_threshold,
        )
        self.state_store = state_store or StateStore(self.config.state_path)
        self.lifecycle_hooks = lifecycle_hooks or LifecycleHooks()
        self.evaluator = evaluator or EvaluationInterface()
        self.tool_registry.register("agent.execute", self.agent.execute)
        self.state = HarnessState.IDLE

    def run(self, input_data: Any) -> Any:
        result: Any = None
        step_count = 0
        self.lifecycle_hooks.on_session_start()
        try:
            while self.state != HarnessState.TERMINATED:
                if step_count >= self.config.max_steps:
                    raise RuntimeError("Max steps exceeded before termination.")

                self.lifecycle_hooks.on_before_step(self.state)
                self.evaluator.record("state.enter", self.state, {"step": step_count})

                if self.state == HarnessState.IDLE:
                    self.state = HarnessState.OBSERVING
                elif self.state == HarnessState.OBSERVING:
                    self.context_manager.add_turn("input", input_data)
                    self.state = HarnessState.INVOKING_MODEL
                elif self.state == HarnessState.INVOKING_MODEL:
                    self.state = HarnessState.DISPATCHING_TOOL
                elif self.state == HarnessState.DISPATCHING_TOOL:
                    result = self.tool_registry.invoke("agent.execute", input_data)
                    self.state = HarnessState.AWAITING_TOOL_RESULT
                elif self.state == HarnessState.AWAITING_TOOL_RESULT:
                    self.context_manager.add_turn("output", result)
                    self.state = HarnessState.COMMITTING_STATE
                elif self.state == HarnessState.COMMITTING_STATE:
                    self.state_store.save(
                        {
                            "input": str(input_data),
                            "output": str(result),
                            "context": self.context_manager.snapshot(),
                            "steps": step_count + 1,
                        }
                    )
                    self.state = HarnessState.TERMINATED
                else:
                    raise RuntimeError(f"Unexpected harness state: {self.state}")

                self.evaluator.record("state.exit", self.state, {"step": step_count})
                self.lifecycle_hooks.on_after_step(self.state)
                step_count += 1
        except Exception as error:
            self.lifecycle_hooks.on_error(error)
            self.evaluator.record("error", self.state, {"message": str(error)})
            raise
        finally:
            self.state = HarnessState.TERMINATED

        return result
