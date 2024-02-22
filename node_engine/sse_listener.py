# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
import threading
import uuid
from datetime import datetime

import sseclient
from print_color import print


class SSEListener:
    # map of event handlers: key = event name, value = handler function
    event_handlers = {}
    connection_id: str

    def __init__(
        self,
        endpoint,
        session_id,
        log_level,
        stream_log,
        print_logs=True,
        connection_id: str | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.session_id = session_id
        self.log_level = log_level
        self.stream_log = stream_log
        self.print_logs = print_logs
        self.connection_id = connection_id or str(uuid.uuid4())
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None

    def connect(self) -> None:
        # start sse_listener in a new thread
        self.thread = threading.Thread(
            target=asyncio.run, args=(self.connect_async(),), daemon=True
        )
        self.thread.start()

    def disconnect(self) -> None:
        if self.thread is None:
            raise Exception("disconnected called while sse_listener is not connected")

        print("Disconnecting from SSE...", color="blue")

        # stop sse_listener
        self.stop_event.set()

    async def connect_async(self) -> None:
        url = "{endpoint}?session_id={session_id}&connection_id={connection_id}".format(
            endpoint=self.endpoint,
            session_id=self.session_id,
            connection_id=self.connection_id,
        )
        print("Connecting to SSE at {}.".format(url), color="blue")
        try:
            messages = sseclient.SSEClient(url)
        except Exception:
            raise Exception("failed to connect to SSE, is service running?")

        print("Connected to SSE.", color="blue")

        for message in messages:
            # exit early if stop_event is set
            if self.stop_event.is_set():
                break

            if message.event == "message" and message.data == "":
                # handle ping message

                if self.log_level == "debug":
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(
                        ":ping - {}".format(timestamp),
                        tag="sse",
                        tag_color="magenta",
                    )

                # fully handled, exit early
                continue

            if self.print_logs and message.event == "log":
                # handle log message
                self.print_log(message)
            else:
                if self.log_level == "debug":
                    print(
                        "[{event}] {data}".format(
                            event=message.event, data=message.data
                        ),
                        tag="sse",
                        tag_color="purple",
                    )

            if message.event in self.event_handlers:
                # handle event message
                await self.event_handlers[message.event](message, self.connection_id)

        # remove event handlers
        self.event_handlers = {}

        # close connection
        print("Disconnected from SSE.", color="blue")

    def on(self, event, handler) -> None:
        # register event handler
        self.event_handlers[event] = handler

    def off(self, event) -> None:
        # unregister event handler
        del self.event_handlers[event]

    def print_log(self, message) -> None:
        # handle log message

        data = json.loads(message.data)

        # skip if log level is not met
        if data["level"] not in ["debug", "info", "warning", "error", "critical"]:
            return
        if self.log_level == "info" and data["level"] not in [
            "info",
            "warning",
            "error",
            "critical",
        ]:
            return
        if self.log_level == "warning" and data["level"] not in [
            "warning",
            "error",
            "critical",
        ]:
            return
        if self.log_level == "error" and data["level"] not in ["error", "critical"]:
            return
        if self.log_level == "critical" and data["level"] != ["critical"]:
            return

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
        if self.log_level == "debug":
            log += "\n" + json.dumps(data["flow_definition"], indent=2)
        print(
            log,
            tag="sse",
            tag_color="purple",
        )
