# Copyright (c) Microsoft. All rights reserved.

import argparse
import asyncio
import json
import signal
import threading
import time
import uuid
from datetime import datetime
from typing import NoReturn

import sseclient
from print_color import print

from node_engine.client import NodeEngineClient
from node_engine.models.flow_definition import FlowDefinition

parser = argparse.ArgumentParser(description="Chat client")
parser.add_argument("user_name", help="user name")
parser.add_argument("session_id", help="session ID")
parser.add_argument(
    "--tunnel-authorization", help="tunnel authorization", dest="tunnel_authorization"
)
parser.add_argument(
    "--log-level", help="log level", dest="log_level", default="warning"
)
parser.add_argument(
    "--stream-log", help="stream log", dest="stream_log", action="store_true"
)
parser.add_argument(
    "--chat-definition", help="chat definition file name", dest="chat_definition"
)
args = parser.parse_args()

default_chat_definition_file_name = "examples/definitions/chat-client.json"
chat_client_definition_file_name = (
    args.chat_definition if args.chat_definition else default_chat_definition_file_name
)

with open(chat_client_definition_file_name, "rt") as definition_file:
    definition_from_file = json.load(definition_file)


async def sse_listener() -> None:
    # attach to session via SSE to receive messages
    connection_id = str(uuid.uuid4())
    url = "http://localhost:8000/sse?session_id={session_id}&connection_id={connection_id}".format(
        session_id=args.session_id, connection_id=connection_id
    )
    print("Connecting to SSE at {}".format(url), color="blue")
    messages = sseclient.SSEClient(url)
    print("Connected to SSE", color="blue")

    for message in messages:
        if message.event == "message" and message.data == "":
            # handle ping message

            if args.log_level == "debug":
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(":ping - {}".format(timestamp), tag="sse", tag_color="magenta")
            else:
                break

        elif message.event == "log":
            # handle log message

            data = json.loads(message.data)

            # skip if log level is not met
            if data["level"] not in ["debug", "info", "warning", "error", "critical"]:
                continue
            if args.log_level == "info" and data["level"] not in [
                "info",
                "warning",
                "error",
                "critical",
            ]:
                continue
            if args.log_level == "warning" and data["level"] not in [
                "warning",
                "error",
                "critical",
            ]:
                continue
            if args.log_level == "error" and data["level"] not in ["error", "critical"]:
                continue
            if args.log_level == "critical" and data["level"] != ["critical"]:
                continue

            # pretty print message
            try:
                data_message = json.dumps(data["message"], indent=2)
            except Exception:
                data_message = data["message"]

            log = "[{namespace}] {level}: {message}".format(
                namespace=data["namespace"],
                level=data["level"],
                message=data_message,
            )
            if args.log_level == "debug":
                log += "\n" + json.dumps(data["flow_definition"], indent=2)
            print(
                log,
                tag="sse",
                tag_color="purple",
            )

        else:
            # handle other messages

            print(
                "[{event}] {data}".format(event=message.event, data=message.data),
                tag="sse",
                tag_color="purple",
            )


def quit_handler(signal_received, frame) -> NoReturn:
    print("Exiting...")
    quit()


async def chat_client() -> None:
    # start chat client
    while True:
        message = input("Enter message: ")

        if message == "exit" or message == "quit":
            break

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
                    "input": [
                        {
                            "sender": args.user_name,
                            "timestamp": int(time.time()),
                            "content": message,
                        },
                    ],
                },
            }
        )

        result = await NodeEngineClient().invoke(
            flow_definition=flow_definition,
            tunnel_authorization=args.tunnel_authorization,
        )

        if args.log_level == "debug":
            print(json.dumps(result, indent=2), tag="debug", tag_color="purple")

        if result.status.error:
            print(result.status.error, tag="error", tag_color="red")

        if "response" in result.context:
            print(
                result.context["response"]["content"],
                tag="response",
                tag_color="green",
            )


async def main() -> None:
    print("Starting chat client...", color="blue")
    print(
        "Log level: {log_level} / Stream log: {stream_log}".format(
            log_level=args.log_level,
            stream_log=args.stream_log,
        ),
        color="blue",
    )

    # register signal handler
    signal.signal(signal.SIGINT, quit_handler)

    # start SSE listener in a separate thread
    sse_thread = threading.Thread(target=asyncio.run, args=(sse_listener(),))
    sse_thread.daemon = True
    sse_thread.start()

    # sleep for a bit to allow SSE listener to start
    await asyncio.sleep(4)

    # start chat client
    await chat_client()

    print("Exiting...")


asyncio.run(main())
