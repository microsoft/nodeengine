# Copyright (c) Microsoft. All rights reserved.

import os
import pathlib
import time
from typing import Any
from node_engine.client import NodeEngineClient

from node_engine.models.flow_definition import FlowDefinition

# set up file locations
app_root_path = pathlib.Path(__file__).parent.parent.parent.absolute()
definitions_path = os.path.join(app_root_path, "definitions")
user_input_file_name = os.path.join(definitions_path, "user-input.json")


# load flow definitions
def load_flow_definitions() -> dict[str, Any]:
    with open(user_input_file_name, "rt") as user_input_file:
        user_input_definition = FlowDefinition.model_validate_json(
            user_input_file.read()
        )

    return {"user_input_definition": user_input_definition}


async def send_message(message, session_id, user_name) -> None:
    user_input_definition = load_flow_definitions()["user_input_definition"]
    flow_definition = user_input_definition.model_copy(
        update={
            "session_id": session_id,
            "context": {
                **user_input_definition.context,
                "input": [
                    {
                        "sender": user_name,
                        "timestamp": int(time.time()),
                        "content": message,
                    },
                ],
            },
        }
    )

    result = await NodeEngineClient().invoke(flow_definition)

    if result.status.error:
        # throw exception
        raise Exception(result.status.error)
