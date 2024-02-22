import json
import re
from typing import Any

from node_engine.libs.debug_inspector import DebugInspector
from node_engine.models.flow_definition import FlowDefinition


def collect(
    message: str,
    flow_definition: FlowDefinition,
    component_info: dict = {},
    component_source: str | None = None,
) -> dict[str, Any]:
    """
    Collect debug information for error context responses
    """

    debug_inspector = DebugInspector(flow_definition=flow_definition, error=message)

    def strip_key(obj: dict | list, pattern: re.Pattern) -> dict | list:
        match obj:
            case dict():
                for key in list(obj.keys()):
                    if not pattern.fullmatch(key):
                        continue
                    obj.pop(key, None)

                for value in obj.values():
                    strip_key(value, pattern)

            case list():
                for item in obj:
                    strip_key(item, pattern)

        return obj

    flow_string = json.dumps(
        [
            strip_key(c.model_dump(), re.compile(r"(\w+\_)?service"))
            for c in debug_inspector.flow
        ],
        indent=2,
    )

    context_string = debug_inspector.context.json()

    num_log_messages = 4
    context_log_string = json.dumps(
        [log_item.model_dump() for log_item in debug_inspector.log(num_log_messages)],
        indent=2,
    )

    component_description = component_info.get("description")
    component_reads_from = component_info.get("reads_from")
    component_writes_to = component_info.get("writes_to")
    component_sample_input = component_info.get("sample_input")

    # Put all debug info into context.
    info = {
        "error": message,
        "error_context": context_string,
        "component_name": debug_inspector.component_name,
        "component_key": debug_inspector.component_key,
        "component_description": component_description,
        "component_reads_from": component_reads_from,
        "component_writes_to": component_writes_to,
        "component_sample_input": component_sample_input,
        "code": component_source,
        "flow": flow_string,
        "log": context_log_string,
    }
    return info
