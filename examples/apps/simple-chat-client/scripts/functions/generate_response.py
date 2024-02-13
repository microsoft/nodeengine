# Copyright (c) Microsoft. All rights reserved.

import os
import pathlib
from typing import Any

from print_color import print

from node_engine.client import invoke
from node_engine.models.flow_definition import FlowDefinition

# set up file locations
app_root_path = pathlib.Path(__file__).parent.parent.parent.absolute()
definitions_path = os.path.join(app_root_path, "definitions")
agent_response_file_name = os.path.join(definitions_path, "agent-response.json")


# load flow definitions
def load_flow_definitions() -> dict[str, Any]:
    with open(agent_response_file_name, "rt") as agent_response_file:
        agent_response_definition = FlowDefinition.model_validate_json(
            agent_response_file.read()
        )

    return {"agent_response_definition": agent_response_definition}


async def generate_response(session_id: str) -> None:
    # generate agent response
    agent_response_definition = load_flow_definitions()["agent_response_definition"]
    flow_definition = agent_response_definition.model_copy(
        update={"session_id": session_id}
    )

    result = await invoke(flow_definition)

    if result.status.error:
        print(result.status.error, tag="error", tag_color="red")

    if "response" in result.context:
        print(
            result.context["response"]["content"],
            tag="response",
            tag_color="green",
        )
