# Copyright (c) Microsoft. All rights reserved.

from nicegui import ui
from print_color import print


class new_chat(ui.button):
    def __init__(self) -> None:
        super().__init__("new chat")

        self.on("click", lambda: create_new_chat())


async def create_new_chat() -> None:
    print(f"new chat", color="blue")

    await ui.run_javascript(
        f"""
        var searchParams = new URLSearchParams(window.location.search);
        searchParams.delete('session_id');
        window.location.href = window.location.origin + '?' + searchParams.toString();
        """
    )
