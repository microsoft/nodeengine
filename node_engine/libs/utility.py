# Copyright (c) Microsoft. All rights reserved.

import json
import os
import re

from dotenv import load_dotenv

from node_engine.libs.context import Context
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_step import FlowStep


def load_azureopenai_config(environment_variable: str) -> dict:
    """
    Load Azure OpenAI config from environment variable.
    """
    load_dotenv()
    # load env var, split key value pairs on comma, and then split each pair on pipe
    config = os.getenv(environment_variable)
    if not config:
        raise Exception(f"missing environment variable {environment_variable}")

    try:
        config = config.split(",")
        config = [item.split("|") for item in config]
        config = {item[0]: item[1] for item in config}
        return config
    except Exception as exception:
        raise Exception(
            f"error parsing environment variable {environment_variable}: {exception}"
        )


def exit_flow_with_error(
    message: str, flow_definition: FlowDefinition, log=None
) -> FlowStep:
    context = Context(flow_definition)
    context.set("error", message)
    flow_definition.status.error = message

    if log:
        log.error(message)

    return FlowStep(
        next="exit",
        flow_definition=flow_definition,
    )


def continue_flow(next: str | None, flow_definition: FlowDefinition) -> FlowStep:
    return FlowStep(
        next=next,
        flow_definition=flow_definition,
    )


def eval_template(template_string: str, values: dict) -> str | dict | list:
    """
    Use template string to walk through the values dict to find the
    replacement value. If no replacement value is found, or the template
    string is invalid, the template will be untouched.
    Examples (see tests/test_utility.py for more examples)
      {{foo}} = values["foo"]
      {{foo.bar}} = values["foo"]["bar"]
      {{foo.bar.baz}} = values["foo"]["bar"]["baz"]
      {{foo.bar[0]}} = values["foo"]["bar"][0]
      {{foo.bar[0].baz}} = values["foo"]["bar"][0]["baz"]
    """

    def replace_string(match: str) -> str:
        replacement = replace_value(match)
        if isinstance(replacement, dict) or isinstance(replacement, list):
            return json.dumps(replacement)
        return str(replacement)

    def replace_value(template: str) -> str | dict | list:
        original_template = "{{" + template + "}}"
        template_parts = template.split(".")

        # Walk through each template part, navigating the `values`` dict to end up
        # with the final value we want to replace the template with. At any part, if
        # the value is not found, set `replace_with` to be an empty string.
        replacement = values
        for template_part in template_parts:
            # If the key has square brackets, expect the value to be an array
            # and get the index from the key.
            if "[" in template_part:
                # Expect the value to be a dict.
                if not isinstance(replacement, dict):
                    replacement = original_template
                    break

                # Pull the index from the template_key_part.
                template_part, index = template_part.split("[")
                if template_part not in replacement:
                    replacement = original_template
                    break
                index = int(index.replace("]", ""))

                # Expect the value's value to be a list.
                if not isinstance(replacement[template_part], list):
                    replacement = original_template
                    break

                # Expect the index to be in range.
                if len(replacement[template_part]) <= index:
                    replacement = original_template
                    break

                # Replace with the index value from the list.
                replacement = replacement[template_part][index]
            else:
                if isinstance(replacement, dict):
                    replacement = replacement.get(template_part, original_template)
                else:
                    replacement = original_template
                    break

        # Replace the template string with the context value.
        if isinstance(replacement, dict) or isinstance(replacement, list):
            # If the value is a dict or list, don't do string
            # substitution, just use the value.
            return replacement

        # If a string or number, do string substitution.
        replacement = str(replacement)
        return replacement

    # Search for template replacement patterns.
    pattern = r"\{\{([^{}]+)\}\}"
    matches = re.findall(pattern, template_string)
    if len(matches) == 0:
        return template_string
    if len(matches) == 1 and "{{" + matches[0] + "}}" == template_string:
        return replace_value(matches[0])

    def replace_string_matches(match: re.Match[str]) -> str:
        return replace_string(match.group(1))

    return re.sub(pattern, replace_string_matches, template_string)


def eval_templates_in_dict(template: dict, values: dict) -> dict:
    """
    Walk through (possibly nested) template dict values and replace any {{key}}
    strings with a value from the values dict.
    """
    for key, value in template.items():
        if isinstance(value, dict):
            eval_templates_in_dict(value, values)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    eval_templates_in_dict(item, values)
        elif isinstance(value, str):
            template[key] = eval_template(value, values)
    return template
