# Copyright (c) Microsoft. All rights reserved.

from typing import Awaitable, Callable

from nicegui import ui


class chat_input(ui.textarea):
    def __init__(self, on_send_message: Callable[[str], Awaitable[None]]) -> None:
        super().__init__(placeholder="message")
        self.props("autogrow")
        self.on_send_message = on_send_message

        self.props("rounded outlined input-class=mx-3")
        self.classes("w-full text-secondary")
        self.on(
            "keydown.enter",
            lambda event: self.send_handler(event),
        )

    async def send_handler(self, event) -> None:
        if event.args["shiftKey"]:
            return

        message = self.value
        self.value = ""

        await self.on_send_message(message)
