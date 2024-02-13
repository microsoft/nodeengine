# Copyright (c) Microsoft. All rights reserved.

from typing import Any

from nicegui import ui

from .ui_utility import scroll_to_bottom


class chat_messages(ui.column):
    messages: dict[str, dict[str, Any]] = {}

    def __init__(self, current_user: str) -> None:
        super().__init__()
        self.current_user = current_user

        self.classes("w-full items-stretch")

    async def set(self, messages: dict[str, dict[str, str]]) -> None:
        for message_id, message in messages.items():
            if message_id in self.messages:
                # determine if message has changed
                if message == self.messages[message_id]["data"]:
                    # message has not changed, continue to next message
                    continue
                # update ui
                self.update_message(message_id, message)
            else:
                # add ui
                self.add_message(message_id, message)

        with self:
            await scroll_to_bottom()

    def add_message(self, message_id: str, message: dict[str, str]) -> None:
        sender = message["sender"]
        content = message["content"]
        with self:
            message_ui = ui.chat_message(
                text=content, name=sender, sent=sender == self.current_user
            )
        self.messages[message_id] = {"data": message, "ui": message_ui}

    def update_message(self, message_id: str, message: dict[str, str]) -> None:
        message_ui = self.messages[message_id]["ui"]
        message_ui.text = message["content"]
        self.messages[message_id]["data"] = message
