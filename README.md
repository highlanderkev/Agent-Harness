# Agent-Harness

Generic starter project for building and running simple agent workflows.

## Project structure

- `src/agent.py` - base `Agent` interface
- `src/harness.py` - small harness runner
- `examples/simple_agent.py` - runnable starter example
- `tests/test_harness.py` - focused harness behavior tests

## Quick start

Run the example:

```bash
python examples/simple_agent.py
```

Run tests:

```bash
python -m unittest discover -s tests -v
```