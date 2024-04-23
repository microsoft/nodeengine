# Copyright (c) Microsoft. All rights reserved.

import logging

import rich.logging


def new() -> rich.logging.RichHandler:
    return rich.logging.RichHandler(
        level=logging.INFO,
        log_time_format="[%X]",
        keywords=(rich.logging.RichHandler.KEYWORDS or []) + ["node_engine"],
    )
