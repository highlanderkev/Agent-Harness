# Agent-Harness

Generic starter project for building and running simple agent workflows.

## Project structure

- `src/agent.py` - base `Agent` interface
- `src/governance.py` - execution loop governance components (E/T/C/S/L/V)
- `src/harness.py` - harness runtime wired to governance components
- `examples/simple_agent.py` - runnable starter example
- `tests/test_harness.py` - focused harness behavior tests

## Quick start

Run the example:

```bash
python examples/simple_agent.py
```

Run the Streamlit UI:

```bash
pip install streamlit
streamlit run streamlit_app.py
```

Run tests:

```bash
python -m unittest discover -s tests -v
```