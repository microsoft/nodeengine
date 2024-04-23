# Copyright (c) Microsoft. All rights reserved.

import argparse
import logging
import os

import uvicorn
from fastapi import FastAPI

from node_engine.libs.logging import console_log_handler

from . import service

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)35s | %(message)s",
    handlers=[console_log_handler.new()],
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        prog="node-engine-service",
        description="Node Engine Service",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--host",
        dest="host",
        type=str,
        default="127.0.0.1",
        help="host IP to run service on",
    )
    parser.add_argument(
        "--port", dest="port", type=int, default=8000, help="port to run service on"
    )
    parser.add_argument(
        "--registry-root",
        dest="registry_root",
        type=str,
        default="./examples",
        help="root directory for registry and component discovery",
    )
    args = parser.parse_args()

    host = args.host
    port = args.port
    registry_root = args.registry_root

    # check to see if directory exists
    if not os.path.isdir(registry_root):
        print(f"Directory '{registry_root}' does not exist.")
        exit(1)

    registry_root = os.path.abspath(registry_root)

    app = FastAPI()
    service.init(app, registry_root)

    logger.info("Starting node_engine service on %s:%s...", host, port)
    logger.info("Registry root: %s", registry_root)

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_config={"version": 1, "disable_existing_loggers": False},
    )


if __name__ == "__main__":
    main()
