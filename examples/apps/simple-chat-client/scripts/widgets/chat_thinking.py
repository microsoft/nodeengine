# Copyright (c) Microsoft. All rights reserved.

from nicegui import ui

from .ui_utility import scroll_to_bottom


class chat_thinking(ui.row):
    status: str | None = None

    def __init__(self) -> None:
        super().__init__()
        self.visible = False

        self.classes("items-center")
        with self:
            ui.spinner("dots", size="2em", color="accent")
            self.status_label = ui.label().classes("text-accent")

    async def set(self, status: str | None) -> None:
        self.status = status

        if status:
            self.visible = True
            self.status_label.set_text(status)
        else:
            self.visible = False

        with self:
            await scroll_to_bottom()
