# Copyright (c) Microsoft. All rights reserved.

from typing import Awaitable, Callable

from nicegui import ui

from .chat_input import chat_input
from .chat_messages import chat_messages
from .chat_thinking import chat_thinking
from .new_chat import new_chat


class chat_interface(ui.column):
    def __init__(
        self,
        current_user: str,
        on_send_message: Callable[[str], Awaitable[None]],
        on_logout: Callable[[], Awaitable[None]],
    ) -> None:
        super().__init__()
        self.current_user = current_user

        with ui.header(), ui.row().classes(
            "w-full max-w-3xl mx-auto justify-between items-center"
        ):
            new_chat()

            ui.markdown(
                "built on [Node Engine](https://github.com/microsoft/nodeengine)"
            ).classes("text-xs mr-8 m-[-1em] text-secondary")

            with ui.button(icon="menu"):
                with ui.menu():
                    ui.menu_item("logout", lambda: on_logout())

        with ui.column().classes("w-full max-w-2xl mx-auto"):
            self.messages = chat_messages(current_user)
            self.status = chat_thinking()

        with ui.footer(), ui.column().classes("w-full max-w-3xl mx-auto"):
            chat_input(on_send_message)
