import logging

import rich.logging

from node_engine.models.flow_definition import FlowDefinition


def new(flow_definition: FlowDefinition) -> rich.logging.RichHandler:
    console_handler = rich.logging.RichHandler(
        level=logging.INFO,
        log_time_format="[%X]",
        keywords=(rich.logging.RichHandler.KEYWORDS or []) + ["node_engine"],
    )
    console_handler.setFormatter(
        logging.Formatter(
            f"node_engine:%(name)s | s:{flow_definition.session_id} | f:{flow_definition.key}"
            f" | %(message)s"
        )
    )
    return console_handler
