from dataclasses import dataclass
from typing import Any

import streamlit as st

from src.agent import Agent
from src.harness import Harness


@dataclass
class EchoConfig:
    name: str
    prefix: str


class ConfigurableEchoAgent(Agent):
    def __init__(self, config: EchoConfig) -> None:
        self.config = config

    def execute(self, input_data: Any) -> Any:
        return f"{self.config.prefix}{input_data}"


def create_harness(config: EchoConfig) -> Harness:
    return Harness(ConfigurableEchoAgent(config))


def main() -> None:
    st.set_page_config(page_title="Agent Harness UI", page_icon="🤖")
    st.title("Agent Harness Streamlit UI")
    st.write("Create an agent and run it through the Harness wrapper.")

    agent_name = st.text_input("Agent name", value="Echo Agent")
    response_prefix = st.text_input("Response prefix", value="Echo: ")

    if st.button("Create agent"):
        config = EchoConfig(name=agent_name, prefix=response_prefix)
        st.session_state["agent_config"] = config
        st.session_state["harness"] = create_harness(config)
        st.success(f"{config.name} created and wrapped with Harness.")

    harness = st.session_state.get("harness")
    config = st.session_state.get("agent_config")

    if harness and config:
        st.subheader(f"Interact with {config.name}")
        user_message = st.text_input("Input", value="Hello Agent Harness!")
        if st.button("Run agent"):
            st.write(harness.run(user_message))
    else:
        st.info("Create an agent to start interacting.")


if __name__ == "__main__":
    main()
