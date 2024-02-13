# Copyright (c) Microsoft. All rights reserved.

from nicegui import ui


async def scroll_to_bottom(threshold: int = 200) -> None:
    await ui.run_javascript(
        f"""
        if (window.scrollY + window.innerHeight >= document.body.scrollHeight - {threshold}) {{
            window.scrollTo(0, document.body.scrollHeight);
        }}
        """,
        respond=False,
    )
