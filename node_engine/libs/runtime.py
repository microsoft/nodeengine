# Copyright (c) Microsoft. All rights reserved.

import asyncio
import traceback

from node_engine.libs import debug_collector
from node_engine.libs.log import Log
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.libs.registry import Registry
from node_engine.libs.utility import continue_flow, exit_flow_with_error
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_event import FlowEvent
from node_engine.models.flow_step import FlowStep


class EventConsumer:
    def __init__(
        self,
        session_id: str,
        queue: asyncio.Queue[FlowEvent],
        connection_id: str | None,
    ) -> None:
        self.connection_id = connection_id
        self.session_id = session_id
        self.queue = queue


class ConnectionEvent:
    def __init__(self, event: FlowEvent, for_connection_id: str | None) -> None:
        self.for_connection_id = for_connection_id
        self.message = event


class Runtime:
    def __init__(self, registry_root: str) -> None:
        self.registry = Registry(registry_root)
        self.consumers: list[EventConsumer] = []

    # Invoke a flow.
    async def invoke(
        self, flow_definition: FlowDefinition, tunnel_authorization: str | None = None
    ) -> FlowDefinition:

        log = Log("runtime", flow_definition, executor=self)
        log("Invoking flow")

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

        log("Flow invocation complete")

        # Return the flow.
        return flow_definition

    def add_event_consumer(
        self,
        session_id: str,
        queue: asyncio.Queue[FlowEvent],
        connection_id: str | None = None,
    ):
        self.consumers.append(
            EventConsumer(session_id, queue, connection_id=connection_id)
        )

    async def emit(self, event: FlowEvent, connection_id=None) -> None:
        """
        Emits a flow event to a session or connection
        """
        self.__forward_event(ConnectionEvent(event, connection_id))

    def __forward_event(self, event: ConnectionEvent) -> None:
        """
        Forward an event to the appropriate consumer(s).
        """
        for consumer in self.consumers:
            if (
                event.for_connection_id is not None
                and consumer.connection_id is not None
                and consumer.connection_id != event.for_connection_id
            ):
                # Event is for a specific connection, and this consumer is not it.
                continue

            if (
                event.for_connection_id is None
                and consumer.session_id != event.message.session_id
            ):
                # Event is for a specific session, and this consumer is not it.
                continue

            consumer.queue.put_nowait(event.message)

    async def invoke_component(
        self,
        flow_definition: FlowDefinition,
        component_key: str,
        tunnel_authorization: str | None = None,
    ) -> FlowStep:
        """
        Invokes a component in the provided flow.
        """
        # Ensure there is at least one component in the flow
        if not flow_definition.flow or len(flow_definition.flow) == 0:
            raise Exception("No components found in flow")

        # Find the component to invoke by key
        return await self.__execute_next(
            flow_definition, component_key, tunnel_authorization
        )

    async def __execute_next(
        self,
        flow_definition: FlowDefinition,
        key: str,
        tunnel_authorization=None,
    ) -> FlowStep:
        """
        Executes the next component in the flow.
        """
        log = Log("runtime", flow_definition, executor=self)

        # Find the next component to execute by key
        flow_component = None
        for item in flow_definition.flow:
            if item.key == key:
                flow_component = item
                break

        flow_definition.status.current_component = flow_component

        # If no component is found, exit the flow
        if not flow_component:
            return self.exit_flow_with_error(
                f"No component found with key: {key}",
                flow_definition,
                log=log,
            )

        log(
            "Executing component; component_key: %s, component_name: %s",
            flow_component.key,
            flow_component.name,
        )

        # Execute the component and get the next component to execute
        try:
            component = self.registry.load_component(
                flow_component.name,
                flow_definition,
                flow_component.key,
                self,
                tunnel_authorization=tunnel_authorization,
            )
        except Exception as exception:
            return self.exit_flow_with_error(
                f"Error loading component: [{flow_component.name}] {exception}",
                flow_definition,
                log=log,
            )
        if component is None:
            return self.exit_flow_with_error(
                f"Component not found: {flow_component.name}",
                flow_definition,
                log=log,
            )

        try:
            result = await component.invoke_execute()
        except Exception as exception:
            stacktrace = traceback.format_exc()
            return self.exit_flow_with_error(
                f"error executing component. name={flow_component.name}], error: {exception}, stack={stacktrace}",
                flow_definition,
                log=log,
                component=component,
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

    def exit_flow_with_error(
        self,
        message: str,
        flow_definition: FlowDefinition,
        log: Log,
        component: NodeEngineComponent | None = None,
    ):
        debug_information = debug_collector.collect(
            message=message,
            flow_definition=flow_definition,
            component_info=component.__class__.get_info() if component else {},
            component_source=component._source_code() if component else None,
        )
        return exit_flow_with_error(
            message,
            flow_definition,
            log=log,
            debug_information=debug_information,
        )
