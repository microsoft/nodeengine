# Copyright (c) Microsoft. All rights reserved.

import asyncio
import threading
import uuid

from nicegui import Client, app, ui
from print_color import print

from examples.libs.sse_listener import SSEListener

from .. import theme
from ..functions.generate_response import generate_response
from ..functions.get_messages import get_messages
from ..functions.send_message import send_message
from ..widgets.chat_interface import chat_interface

# set up variables
log_level = "info"
stream_log = True
sse_endpoint = "http://localhost:8000/sse"


def chat_init() -> None:
    @ui.page("/")
    async def chat(
        client: Client,
        session_id: str | None = None,
    ) -> None:
        # add custom CSS
        # must be run before client.connected()
        ui.add_head_html(
            f"""
            <style>
                .q-message-text--sent {{
                    background-color: {theme.colors["secondary"]};
                    color: {theme.colors["secondary"]};
                }}
                .q-message-text--received {{
                    background-color: {theme.colors["tertiary"]};
                    color: {theme.colors["tertiary"]};
                }}
            </style>
            """
        )

        ui.colors(
            primary=theme.colors["primary"],
            secondary=theme.colors["secondary"],
            accent=theme.colors["accent"],
            dark=theme.colors["dark"],
            positive=theme.colors["positive"],
            negative=theme.colors["negative"],
            info=theme.colors["info"],
            warning=theme.colors["warning"],
        )

        # wait for connection to service
        await client.connected()

        user_name = (
            app.storage.user["user_name"] if "user_name" in app.storage.user else None
        )
        if not user_name:
            ui.open("/login")
            return

        if not session_id:
            session_id = str(uuid.uuid4())
            await ui.run_javascript(
                f"""
                var searchParams = new URLSearchParams(window.location.search);
                searchParams.set('session_id', '{session_id}');
                window.location.href = window.location.origin + '?' + searchParams.toString();
                """
            )

        print(f"Starting chat client for session: {session_id}", color="blue")

        # set up event handlers
        async def messages_changed_handler(message, sender_id) -> None:
            if sender_id != client.id:
                return

            await interface.messages.set(await get_messages(session_id))

            if message.data != "user":
                # If the message is not from the user,
                # then the agent has sent a message.
                # Exit early - we handle additional
                # agent responses in the get_response
                # handler and it's flow.
                return
            else:
                # get a response from the agent
                print("Generating agent response...", color="blue")
                invoke_thread = threading.Thread(
                    target=asyncio.run,
                    args=(generate_response(session_id),),
                )
                invoke_thread.start()

        async def status_handler(message, sender_id) -> None:
            if sender_id != client.id:
                return
            await interface.status.set(message.data)

        async def on_send_message(message) -> None:
            await send_message(message, session_id, user_name)

        async def on_logout() -> None:
            app.storage.user["user_name"] = None
            ui.open("/login")

        # set up main UI
        interface = chat_interface(
            user_name,
            on_send_message,
            on_logout,
        )

        # get initial data
        await interface.messages.set(await get_messages(session_id))

        sse_listener = SSEListener(
            endpoint=sse_endpoint,
            session_id=session_id,
            log_level=log_level,
            stream_log=stream_log,
            connection_id=client.id,
        )

        # register event handler
        sse_listener.on("messages:changed", messages_changed_handler)
        sse_listener.on("status", status_handler)

        # connect to service
        sse_listener.connect()

        # register disconnect handler
        def on_disconnect_handler(disconnecting_client: Client) -> None:
            if disconnecting_client.id == client.id:
                sse_listener.disconnect()

        app.on_disconnect(on_disconnect_handler)
