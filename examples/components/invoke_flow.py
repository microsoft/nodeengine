# Copyright (c) Microsoft. All rights reserved.

from node_engine.client import NodeEngineClient
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.libs.utility import eval_template, eval_templates_in_dict
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_step import FlowStep


class InvokeFlow(NodeEngineComponent):
    description = "This component will load a flow definition and invoke it. All context will be passed to the flow."

    default_config = {
        "include_debug": False,
    }

    reads_from = {
        "context": {},
        "config": {
            "flow_definition": {
                "type": "dict",
                "description": "The flow definition to invoke.",
                "required": True,
            },
            "context": {
                "type": "dict",
                "description": "Additional context to pass to be merged into the flow.",
                "required": False,
            },
            "next": {
                "type": "string",
                "description": "The next step in the flow after repeats have been completed. Defaults to 'None'.",
                "required": False,
            },
        },
    }

    writes_to = {}

    sample_input = {
        "key": "",
        "session_id": "test",
        "context": {
            "stream_log": "true",
        },
        "flow": [
            {
                "key": "a_flow",
                "name": "InvokeFlow",
                "config": {
                    "flow_definition": {},
                },
            },
        ],
    }

    sample_output = {
        **sample_input,
        "context": {**sample_input["context"], "output": {}},
    }

    async def execute(self) -> FlowStep:
        # Set up a flow definition.
        flow_definition = self.config.get("flow_definition") or None
        if flow_definition is None:
            return self.exit_flow_with_error("no flow definition provided")

        # The flow definition that is to be invoked needs to be specified
        # either as a dict or as a template that resolves to a dict.
        if isinstance(flow_definition, str):
            # If the flow definition is a template, replace it with values from the context.
            if "{{" in flow_definition:
                flow_definition = eval_template(
                    flow_definition, self.flow_definition.context
                )
                if not isinstance(flow_definition, dict):
                    return self.exit_flow_with_error(
                        "invalid config, 'definition' template variable does not resolve to a dict."
                        f"input={self.config.get('definition')}"
                    )
            else:
                return self.exit_flow_with_error(
                    f"invalid config, 'definition' must be a dict or a template. input={self.config.get('definition')}"
                )
            flow_definition = FlowDefinition(**flow_definition)
        elif isinstance(flow_definition, dict):
            flow_definition = FlowDefinition(**flow_definition)
        else:
            return self.exit_flow_with_error(
                f"invalid config, 'definition' must be a dict or a template. input={self.config.get('definition')}"
            )

        # Pass on session_id from parent.
        flow_definition.session_id = self.flow_definition.session_id

        # Pass on registry from parent.
        flow_definition.registry = self.flow_definition.registry

        # When a flow is invoked using this component, it can get context from
        # three places:
        # 1. From the invoking flow's context (parent context).
        # 2. From the default context in the flow being invoked (default child
        #    context).
        # 3. From the context being passed into this component via config
        # (config context).
        #
        # The context from these three places is merged together, with the
        # config context taking precedence over the default child context, and
        # the child context taking precedence over the parent context. In the
        # end, this allows you to use whatever context was in flow already when
        # invoked, but use defaults from the invoked flow if they're not set,
        # and let you overwrite any of the context you'd like with values from
        # the config.
        default_child_context = flow_definition.context or {}
        parent_context = self.flow_definition.context or {}
        config_context = self.config.get("context") or {}
        # Replace any template variables in the overwrite context with values
        # from the parent context.
        config_context = eval_templates_in_dict(
            config_context, self.flow_definition.context
        )
        flow_definition.context = {
            **default_child_context,
            **parent_context,
            **config_context,
        }

        # Pass status from parent flow to child.
        flow_definition.status = self.flow_definition.status

        # Execute the new flow.
        self.log.info(f"Invoking flow. key: {flow_definition.key}.")
        flow_result = await NodeEngineClient().invoke(flow_definition)

        # Pass child flow's status and context back to parent.
        self.flow_definition.status = flow_result.status
        self.flow_definition.context = flow_result.context

        return self.continue_flow(self.config.get("next"))
