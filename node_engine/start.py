# Copyright (c) Microsoft. All rights reserved.

import argparse
import os

import uvicorn
from fastapi import FastAPI

from . import service

local_files_root = None

parser = argparse.ArgumentParser(description="Node Engine")
parser.add_argument("--reload", dest="reload", default=False)
parser.add_argument("--local_files_root", dest="local_files_root")
args = parser.parse_args()

local_files_root = os.path.abspath(".")
if args.local_files_root:
    local_files_root = f"{args.local_files_root}"
    # check to see if directory exists
    if os.path.isdir(local_files_root):
        local_files_root = os.path.abspath(local_files_root)
    else:
        print(f"Directory '{local_files_root}' does not exist.")
        exit()

reload = False
if args.reload:
    reload = True


app = FastAPI()
service.init(app, local_files_root)

if __name__ == "__main__":
    uvicorn.run("node_engine.start:app", reload=reload)
