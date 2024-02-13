# Copyright (c) Microsoft. All rights reserved.

import traceback

from print_color import print

from node_engine.libs.log import Log
from node_engine.libs.registry import Registry
from node_engine.libs.sse_state import SSEState
from node_engine.libs.utility import continue_flow, exit_flow_with_error
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_step import FlowStep


class Runtime:
    sse_state = SSEState()

    def __init__(self, local_files_root: str) -> None:
        self.registry = Registry(local_files_root)

    # Invoke a flow.
    async def invoke(
        self, flow_definition: FlowDefinition, tunnel_authorization: str | None = None
    ) -> FlowDefinition:
        # Ensure there is at least one component in the flow.
        if not flow_definition.flow or len(flow_definition.flow) == 0:
            raise Exception("No components found in flow")

        # Start the flow
        next = flow_definition.flow[0].key
        # Execute the flow until the next component is "exit".
        while next != "exit":
            result = await self.__execute_next(
                flow_definition, next, tunnel_authorization
            )
            flow_definition = result.flow_definition
            next = "exit" if result.next is None else result.next

        # Add the session_id to the flow context in case
        # it was generated during the flow, since we don't
        # return the full flow and just the context.
        # TODO: Is this the best pattern?
        flow_definition.context["session_id"] = flow_definition.session_id

        # Return the flow.
        return flow_definition

    # Add new SSE connection registration to the state
    def add_sse_connection(self, connection_id, session_id):
        self.sse_state.add_connection(connection_id, session_id)

    # Emit an SSE message to a session or connection
    # Each message will be added to the state to be dequeued and sent to the client
    def emit_sse_message(self, session_id, message, connection_id=None):
        if connection_id:
            self.sse_state.connections[connection_id]["messages"].append(message)
        else:
            for connection_id in self.sse_state.connections:
                if (
                    self.sse_state.connections[connection_id]["session_id"]
                    == session_id
                ):
                    self.sse_state.connections[connection_id]["messages"].append(
                        message
                    )

    # Invoke a component
    async def invoke_component(
        self,
        flow_definition: FlowDefinition,
        component_key: str,
        tunnel_authorization: str | None = None,
    ) -> FlowStep:
        # Ensure there is at least one component in the flow
        if not flow_definition.flow or len(flow_definition.flow) == 0:
            raise Exception("No components found in flow")

        # Find the component to invoke by key
        return await self.__execute_next(
            flow_definition, component_key, tunnel_authorization
        )

    # Execute the next component in the flow
    async def __execute_next(
        self,
        flow_definition: FlowDefinition,
        key: str,
        tunnel_authorization=None,
    ) -> FlowStep:
        log = Log("runtime", flow_definition)

        # Find the next component to execute by key
        flow_component = None
        for item in flow_definition.flow:
            if item.key == key:
                flow_component = item
                break

        flow_definition.status.current_component = flow_component

        # If no component is found, exit the flow
        if not flow_component:
            return exit_flow_with_error(
                f"No component found with key: {key}",
                flow_definition,
                log,
            )

        log_message = (
            f"Executing component: {flow_component.key} ({flow_component.name})."
        )
        log(log_message)
        print(log_message, tag="runtime", tag_color="green")

        # Execute the component and get the next component to execute
        try:
            component = await self.registry.load_component(
                flow_component.name,
                flow_definition,
                flow_component.key,
                tunnel_authorization,
            )
        except Exception as exception:
            return exit_flow_with_error(
                f"Error loading component: [{flow_component.name}] {exception}",
                flow_definition,
                log,
            )
        if component is None:
            return exit_flow_with_error(
                f"Component not found: {flow_component.name}",
                flow_definition,
                log,
            )

        try:
            result = await component.invoke_execute()
        except Exception as exception:
            stacktrace = traceback.format_exc()
            return exit_flow_with_error(
                f"error executing component. name={flow_component.name}], error: {exception}, stack={stacktrace}",
                flow_definition,
                log,
            )

        flow_definition = result.flow_definition

        if result.next is None:
            # No next component defined by component, so get next from flow.
            next_index = flow_definition.flow.index(flow_component) + 1
            if next_index >= len(flow_definition.flow):
                # No more components in flow, exit.
                return continue_flow("exit", flow_definition)
            else:
                # Get key of next component in flow.
                return continue_flow(
                    flow_definition.flow[next_index].key, flow_definition
                )
        else:
            return continue_flow(result.next, flow_definition)
