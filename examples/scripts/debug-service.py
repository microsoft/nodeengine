# Copyright (c) Microsoft. All rights reserved.

####
# Debug agent.
# This agent subscribes to all SSE messages for a session,
# monitors for errors, and injects SSE messages to explain
# the errors while providing potential fixes.
####

import argparse
import asyncio
import json
import os
import signal
from typing import NoReturn

from print_color import print
from sseclient import Event

import node_engine.libs.log as log
from node_engine.client import NodeEngineClient, RemoteExecutor
from node_engine.libs.debug_inspector import DebugInspector
from node_engine.libs.endpoint_runner import EndpointRunner
from node_engine.libs.registry import Registry
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.log_item import LogItem
from node_engine.sse_listener import SSEListener

parser = argparse.ArgumentParser(description="Debug agent")
parser.add_argument("session_id", help="session ID")
# Levels: DEBUG INFO WARNING ERROR CRITICAL
parser.add_argument("--log-level", help="log level", dest="log_level", default="error")
args = parser.parse_args()

log_level = log.LogLevel.from_string(args.log_level)

# local files
registry_root = os.path.dirname(os.path.realpath(__file__))


def say(message) -> None:
    print("\n🪲 " + message, color="green")


async def log_handler(event: Event, sender_connection_id: str):
    data = json.loads(event.data)
    # This avoids having the message being evaluated as python code.
    data["message"] = str(data["message"])
    log_item: LogItem = LogItem(**data)
    data_log_level = log.LogLevel.from_string(log_item.level)
    is_error = data_log_level == log.ERROR

    # Skip if log level is not met.
    if data_log_level < log_level:
        return

    say("Received SSE log message...")

    # Pretty print message.
    try:
        data_message = json.dumps(log_item.message, indent=2)
    except Exception:
        data_message = log_item.message

    logMessage = "[{namespace}] {level}: {message}".format(
        namespace=log_item.namespace,
        level=log_item.level,
        message=data_message,
    )
    if log_level == log.DEBUG and log_item.flow_definition:
        logMessage += "\n" + json.dumps(log_item.flow_definition, indent=2)
    print(
        logMessage,
        tag="sse",
        tag_color="purple",
    )

    # handle error message
    if is_error:
        say("Received an error in the logs:")
        print(log_item.message, tag="error", tag_color="red")
        await get_agent_response(log_item)


async def get_agent_response(log_item: LogItem) -> None:
    say("Generating response...")

    error = log_item.message
    if log_item.flow_definition is None:
        say("No flow definition found.")
        return
    flow_definition = FlowDefinition(**log_item.flow_definition)

    debug_inspector = DebugInspector(flow_definition, error)

    say("Flow:")
    flow_string = json.dumps([c.model_dump() for c in debug_inspector.flow], indent=2)
    print(flow_string, color="purple")

    say("Context:")
    context_string = debug_inspector.context.json()
    print(context_string, color="purple")

    say("Log:")
    num_log_messages = 4
    context_log_string = json.dumps(
        [log_item.model_dump() for log_item in debug_inspector.log(num_log_messages)],
        indent=2,
    )
    print(context_log_string, color="purple")

    component = None
    if flow_definition.status.current_component:
        component = Registry(registry_root).load_component(
            flow_definition.status.current_component.name,
            flow_definition,
            flow_definition.status.current_component.key,
            RemoteExecutor(),
            None,
        )

    # Get component info
    info = None
    component_description = None
    component_reads_from = None
    component_writes_to = None
    component_sample_input = None
    if component:
        # Note: If your component is registered from an endpoint, there will be
        # no info available.
        info = component.__class__.get_info()

    if info:
        if info.get("description"):
            component_description = info.get("description")
            print("Component description:", color="blue")
            print(component_description, color="purple")

        if info.get("reads_from"):
            component_reads_from = info.get("reads_from")
            print("Component `reads_from`:", color="blue")
            print(component_reads_from, color="purple")

        if info.get("writes_to"):
            component_writes_to = info.get("writes_to")
            print("Component `writes_to`:", color="blue")
            print(component_writes_to, color="purple")

        if info.get("sample_input"):
            component_sample_input = info.get("sample_input")
            print("Component `sample_input`:", color="blue")
            print(component_sample_input, color="purple")

    code_string = None
    if component:
        if isinstance(component, EndpointRunner):
            code_string = await component._source_code()
        else:
            code_string = component._source_code()
        say("Component execute method source:")
        print(code_string, color="purple")

    # Load debug flow definition.
    debug_response_definition_filename = "examples/definitions/debug.json"
    with open(
        debug_response_definition_filename, "rt"
    ) as debug_response_definition_file:
        debug_response_definition = json.load(debug_response_definition_file)

    # Put all debug info into context.
    context = debug_response_definition.get("context", {})
    info = context.get("debug_agent", {})
    if error:
        info["error"] = error
    if context_string:
        info["error_context"] = context_string
    if debug_inspector.component_name:
        info["component_name"] = debug_inspector.component_name
    if debug_inspector.component_key:
        info["component_key"] = debug_inspector.component_key
    if component_description:
        info["component_description"] = component_description
    if component_reads_from:
        info["component_reads_from"] = component_reads_from
    if component_writes_to:
        info["component_writes_to"] = component_writes_to
    if component_sample_input:
        info["component_sample_input"] = component_sample_input
    if code_string:
        info["code"] = code_string
    if flow_string:
        info["flow"] = flow_string
    if context_log_string:
        info["log"] = context_log_string

    context["debug_agent"] = info
    flow_definition = FlowDefinition(
        **{
            **debug_response_definition,
            "session_id": args.session_id,
            "context": context,
        }
    )

    say("Looking over the error...")
    result = await NodeEngineClient().invoke(flow_definition=flow_definition)

    if log_level == log.DEBUG:
        try:
            print(result.model_dump_json(indent=2), tag="debug", tag_color="purple")
        except Exception:
            print(json.dumps(result, indent=2), tag="debug", tag_color="purple")

    if "debug_agent_response" in result.context:
        say(result.context["debug_agent_response"])
    else:
        say("[No response generated.]")

    say("Watching the logs...")


def quit_handler(signal_received, frame) -> NoReturn:
    print("Exiting...")
    quit()


async def test(error: str) -> None:
    log_item = LogItem(
        **{
            "namespace": "debug_agent",
            "level": "error",
            "message": error,
            "flow_definition": None,
        }
    )
    await get_agent_response(log_item)


async def main() -> None:
    print("Starting debug agent...", color="blue")

    print(
        f"Log level: {log_level.name}",
        color="blue",
    )

    # Register signal handler.
    signal.signal(signal.SIGINT, quit_handler)

    # Create sse_listener.
    sse_endpoint = "http://localhost:8000/sse"
    sse_listener = SSEListener(
        endpoint=sse_endpoint,
        session_id=args.session_id,
        log_level=args.log_level,
        stream_log=None,
        print_logs=False,
    )

    # Register event handler
    sse_listener.on("log", log_handler)

    # Connect to SSE
    await sse_listener.connect_async()

    say("Exiting...")


asyncio.run(main())
