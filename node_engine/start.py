# Copyright (c) Microsoft. All rights reserved.

import argparse
import os

import uvicorn
from fastapi import FastAPI

from . import service


def main():
    parser = argparse.ArgumentParser(
        prog="node_engine_service",
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
        "--registry_root",
        dest="registry_root",
        type=str,
        default=".",
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

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
