# Copyright (c) Microsoft. All rights reserved.

"""
This script is a CLI tool to invoke a flow definition. It has a few nice
features:

- It will stream log messages to the console at whatever log level you specify
  with --log-level.
- When the flow completes, it will print the final context.
- Sub-flows need to be passed into the InvokeFlow via context. If your flow uses
  InvokeFlow, you can add sub-flows from other files using `--subflows`.
- If you would rather POST your flow to the Node Engine Service directly, this
  script can produce the flow for you (unpacking sub-flows) by using the
  --dry-run flag.
"""

import argparse
import asyncio
import json
import os

from print_color import print

import node_engine.libs.log as log
from node_engine.client import NodeEngineClient
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_event import FlowEvent
from node_engine.models.log_item import LogItem
from node_engine.sse_listener import SSEListener

# Require a flow file name as a command line argument.
# Will also display usage message if no arguments or -h/--help is provided.
parser = argparse.ArgumentParser(description="Invoke flow via node-engine service")
parser.add_argument("definition_file", help="definition file name")
parser.add_argument(
    "--session-id", help="session ID", dest="session_id", default="123456"
)
parser.add_argument(
    "--stream-log", help="stream log", dest="stream_log", action="store_true"
)
parser.add_argument("--log-level", help="log level", dest="log_level", default="info")
parser.add_argument(
    "--sse-message",
    help="post-run SSE message to send to session",
    dest="sse_message",
    default=None,
)
parser.add_argument(
    "--child-flows",
    nargs="*",
    action="store",
    help="child flows. Any number of <flow_name>=<file path> args.",
)
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Just print out the flow definition and exit.",
)


args = parser.parse_args()

# Put child flow args into a dict.
if args.child_flows:
    flows_dict = {}
    for item in args.child_flows:
        key, value = item.split("=")
        flows_dict[key] = value
    args.child_flows = flows_dict

log_level = log.LogLevel.from_string(args.log_level)

definition_file_name = args.definition_file

# Check if the file exists
if not os.path.isfile(definition_file_name):
    raise FileNotFoundError(f"The file {definition_file_name} does not exist.")

with open(definition_file_name, "rt") as definition_file:
    definition_from_file = json.load(definition_file)


def say(message) -> None:
    print("\n🪲 " + message, color="green")


async def invoke_flow() -> FlowDefinition | None:
    if not args.dry_run:
        say("Invoking flow.")

    flow_definition = FlowDefinition(
        **{
            **definition_from_file,
            "session_id": args.session_id,
            "context": {
                **(
                    definition_from_file["context"]
                    if "context" in definition_from_file
                    else {}
                ),
                "stream_log": True if args.stream_log else False,
            },
        }
    )

    # Add child flows to context.
    if args.child_flows:
        flow_definition.context["flows"] = {}
        for flow_name, flow_file_name in args.child_flows.items():
            with open(flow_file_name, "rt") as flow_file:
                flow_from_file = json.load(flow_file)
            flow_definition.context["flows"][flow_name] = flow_from_file

    if args.dry_run:
        print(flow_definition.model_dump_json(indent=2))
        return

    result = await NodeEngineClient().invoke(flow_definition)

    # Check for error.
    if result.status.error:
        say(result.status.error)
        return

    print(result.model_dump_json(indent=2))

    # Make the output easier to read in cli.
    result.status.log = []
    result.status.trace = [result.status.trace[-1]]
    result_context = result.model_dump()["context"]
    if "flows" in result_context:
        del result_context["flows"]
    say(json.dumps(result_context, indent=2))
    return result


async def log_handler(event: FlowEvent, connection_id: str) -> None:
    data = json.loads(event.data)

    # This avoids having the message being evaluated as python code.
    data["message"] = str(data["message"])
    log_item: LogItem = LogItem(**data)

    # Skip if debug.
    data_log_level = log.LogLevel.from_string(log_item.level)
    if data_log_level < log_level:
        return

    # Pretty print message.
    try:
        data_message = json.dumps(log_item.message, indent=2)
    except Exception:
        data_message = log_item.message

    # Strip quotes.
    data_message = data_message.strip('"')

    if data_log_level == log.LogLevel.ERROR:
        print(json.dumps(log_item.flow_definition, indent=2), color="purple")
        print(data_message, color="red")
    elif data_log_level == log.LogLevel.WARNING:
        print(data_message, color="yellow")
    elif data_log_level == log.LogLevel.INFO:
        print(data_message, color="green")
    elif data_log_level == log.LogLevel.DEBUG:
        print(data_message, color="blue")
    else:
        print(data_message)


async def main() -> None:
    sse_listener: SSEListener | None = None
    if not args.dry_run:
        print(
            f"Log level: {log_level.name}",
            color="blue",
        )

        # Create sse_listener.
        sse_endpoint = "http://localhost:8000/sse"
        sse_listener = SSEListener(
            endpoint=sse_endpoint,
            session_id=args.session_id,
            log_level="error",
            stream_log=None,
            print_logs=True,
        )

        # Register event handler.
        sse_listener.on("log", log_handler)

        # Start SSE in the background.
        sse_listener.connect()

    await invoke_flow()

    if not args.dry_run:
        if sse_listener is not None:
            sse_listener.disconnect()


asyncio.run(main())
