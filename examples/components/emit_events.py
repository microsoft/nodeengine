# Copyright (c) Microsoft. All rights reserved.

import json

from node_engine.models.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class EmitEvents(NodeEngineComponent):
    description = "Emit events to all connected clients for the session. Supports formats of event, event with explicit data, and event with data from context by source key."

    reads_from = {
        "context": {
            "events": "see types in config",
        },
        "config": {
            "events": {
                "types": [
                    {
                        "type": "string",
                    },
                    {
                        "type": {
                            "event": "string",
                            "data": "string",
                        },
                    },
                    {
                        "type": {
                            "event": "string",
                            "source": "string",
                        },
                    },
                ],
                "description": "A list of events to emit to all connected clients for the session.  If passing source, the source key must be in the context and the value will be used as the data for the event.",
                "required": False,
            }
        },
    }

    writes_to = None

    sample_input = {
        "key": "sample",
        "context": {
            "events": ["event1", "event2"],
            "response": {
                "sender": "agent",
                "timestamp": 1629386400,
                "content": "Greetings!",
            },
        },
        "flow": [
            {
                "key": "start",
                "name": "EmitEvents",
                "config": {
                    "events": [
                        "event1",
                        {
                            "event": "event2",
                            "data": "some data",
                        },
                        {
                            "event": "user_response",
                            "source": "response",
                        },
                    ],
                },
            }
        ],
    }

    async def execute(self) -> FlowStep:
        # emit events

        self.log("Emitting events.")

        events = self.context.get("events", []) + self.config.get("events", [])

        for event in events:
            self.log(f"Emitting event: {event}")

            event_name = None
            event_data = None
            if isinstance(event, dict):
                if event.get("event") and event.get("data"):
                    event_name = event["event"]
                    event_data = event["data"]
                if event.get("event") and event.get("source"):
                    event_name = event["event"]
                    event_data = json.dumps(self.context.get(event["source"]) or "")
            else:
                event_name = event
                event_data = ""

            if event_name and event_data is not None:
                await self.emit(event_name, event_data)

        # clear context events
        self.context.set("events", [])

        return self.continue_flow()
