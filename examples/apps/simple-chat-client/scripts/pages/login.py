# Copyright (c) Microsoft. All rights reserved.

from nicegui import app, ui


def login_init() -> None:
    @ui.page("/login")
    async def login() -> None:
        with ui.column():
            ui.input(placeholder="username").bind_value(app.storage.user, "user_name")
            ui.button("login", on_click=lambda: ui.open("/"))
