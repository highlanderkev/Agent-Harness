import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable


class HarnessState(str, Enum):
    IDLE = "idle"
    OBSERVING = "observing"
    INVOKING_MODEL = "invoking-model"
    DISPATCHING_TOOL = "dispatching-tool"
    AWAITING_TOOL_RESULT = "awaiting-tool-result"
    COMMITTING_STATE = "committing-state"
    TERMINATED = "terminated"


@dataclass
class HarnessConfig:
    max_steps: int = 7
    context_window_size: int = 10
    offload_threshold: int = 2000
    state_path: str | None = None


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, handler: Callable[..., Any]) -> None:
        self._tools[name] = handler

    def invoke(self, name: str, *args: Any, **kwargs: Any) -> Any:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered.")
        return self._tools[name](*args, **kwargs)


class ContextManager:
    def __init__(self, window_size: int, offload_threshold: int) -> None:
        self._window_size = window_size
        self._offload_threshold = offload_threshold
        self._turns: list[dict[str, str]] = []

    def add_turn(self, role: str, content: Any) -> None:
        normalized = self._normalize(content)
        self._turns.append({"role": role, "content": normalized})
        self._compact()

    def snapshot(self) -> list[dict[str, str]]:
        return list(self._turns)

    def _compact(self) -> None:
        if len(self._turns) > self._window_size:
            overflow = len(self._turns) - self._window_size
            self._turns = self._turns[overflow:]

    def _normalize(self, content: Any) -> str:
        text = str(content)
        if len(text) <= self._offload_threshold:
            return text
        head = text[:200]
        tail = text[-200:]
        return f"{head}...[offloaded {len(text)} chars]...{tail}"


class StateStore:
    def __init__(self, state_path: str | None) -> None:
        self._path = Path(state_path) if state_path else None

    def save(self, state: dict[str, Any]) -> None:
        if self._path is None:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", delete=False, dir=str(self._path.parent), encoding="utf-8") as tmp_file:
            json.dump(state, tmp_file, indent=2, sort_keys=True)
            tmp_name = tmp_file.name
        Path(tmp_name).replace(self._path)

    def load(self) -> dict[str, Any]:
        if self._path is None:
            return {}
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text(encoding="utf-8"))


class LifecycleHooks:
    def __init__(self) -> None:
        self._session_start: list[Callable[[], None]] = []
        self._before_step: list[Callable[[HarnessState], None]] = []
        self._after_step: list[Callable[[HarnessState], None]] = []
        self._on_error: list[Callable[[Exception], None]] = []

    def register_session_start(self, hook: Callable[[], None]) -> None:
        self._session_start.append(hook)

    def register_before_step(self, hook: Callable[[HarnessState], None]) -> None:
        self._before_step.append(hook)

    def register_after_step(self, hook: Callable[[HarnessState], None]) -> None:
        self._after_step.append(hook)

    def register_on_error(self, hook: Callable[[Exception], None]) -> None:
        self._on_error.append(hook)

    def on_session_start(self) -> None:
        for hook in self._session_start:
            hook()

    def on_before_step(self, state: HarnessState) -> None:
        for hook in self._before_step:
            hook(state)

    def on_after_step(self, state: HarnessState) -> None:
        for hook in self._after_step:
            hook(state)

    def on_error(self, error: Exception) -> None:
        for hook in self._on_error:
            hook(error)


@dataclass
class EvaluationInterface:
    events: list[dict[str, Any]] = field(default_factory=list)

    def record(self, event_type: str, state: HarnessState, payload: dict[str, Any] | None = None) -> None:
        self.events.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "state": state.value,
                "payload": payload or {},
            }
        )
