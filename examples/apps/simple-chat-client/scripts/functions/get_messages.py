# Copyright (c) Microsoft. All rights reserved.

import os
import pathlib
from typing import Any

from node_engine.client import NodeEngineClient
from node_engine.models.flow_definition import FlowDefinition

# set up file locations
app_root_path = pathlib.Path(__file__).parent.parent.parent.absolute()
definitions_path = os.path.join(app_root_path, "definitions")
get_messages_file_name = os.path.join(definitions_path, "get-messages.json")


# load flow definitions
def load_flow_definitions() -> dict[str, Any]:
    with open(get_messages_file_name, "rt") as get_messages_file:
        get_messages_definition = FlowDefinition.model_validate_json(
            get_messages_file.read()
        )

    return {"get_messages_definition": get_messages_definition}


async def get_messages(session_id: str) -> dict[str, dict[str, str]]:
    get_messages_definition = load_flow_definitions()["get_messages_definition"]
    flow_definition = get_messages_definition.model_copy(
        update={"session_id": session_id}
    )

    result = await NodeEngineClient().invoke(flow_definition=flow_definition)

    if result.status.error:
        # throw exception
        raise Exception(result.status.error)

    messages: dict[str, dict[str, str]] = {}
    if "messages" in result.context:
        for message in result.context["messages"]:
            message_id = "{timestamp}:{sender}".format(
                timestamp=message["timestamp"], sender=message["sender"]
            )
            messages[message_id] = message

    return messages
