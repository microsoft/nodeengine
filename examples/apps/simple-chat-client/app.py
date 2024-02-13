# Copyright (c) Microsoft. All rights reserved.

import os

from fastapi import FastAPI
from print_color import print

from node_engine import service

from .scripts import frontend

# local files
local_files_root = os.path.dirname(os.path.realpath(__file__))

# set up FastAPI
app = FastAPI()

# launch service
print("Starting service...")
service.init(app, local_files_root)

# launch frontend
print("Starting frontend...")
frontend.init(fastapi_app=app)
