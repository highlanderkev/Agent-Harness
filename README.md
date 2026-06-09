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
python /home/runner/work/Agent-Harness/Agent-Harness/highlanderkev/Agent-Harness/examples/simple_agent.py
```

Run tests:

```bash
cd /home/runner/work/Agent-Harness/Agent-Harness/highlanderkev/Agent-Harness
python -m unittest discover -s tests -v
```