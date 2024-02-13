# Copyright (c) Microsoft. All rights reserved.

from fastapi import FastAPI
from nicegui import ui

from .pages.chat import chat_init
from .pages.login import login_init

####################
# load files and command line arguments
####################

# set up variables
darkMode = True


def init(fastapi_app: FastAPI) -> None:
    # pages
    login_init()
    chat_init()

    # start UI
    ui.run_with(
        fastapi_app,
        title="Chat",
        storage_secret="chat-client",
        dark=darkMode,
    )
