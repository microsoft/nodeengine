# Copyright (c) Microsoft. All rights reserved.

import time
from functools import wraps
from typing import Any, Callable

from node_engine.libs.storage import Storage


class Timer:
    def __init__(self) -> None:
        self.start_time = None
        self.end_time = None
        self.start()

    def start(self) -> None:
        self.start_time = time.time_ns() / 1_000_000

    def stop(self) -> None:
        self.end_time = time.time_ns() / 1_000_000

    def elapsed_time(self) -> float | None:
        if self.start_time is None or self.end_time is None:
            return None
        return self.end_time - self.start_time


class Telemetry:
    def __init__(self, session_id, flow_key, component_key) -> None:
        self.session_id = session_id
        self.flow_key = flow_key
        self.component_key = component_key

    def telemetry_storage_key(self) -> str:
        return f"telemetry_{self.flow_key}-{self.component_key}"

    async def capture(self, data) -> None:
        existing_data = (
            await Storage.get(self.session_id, self.telemetry_storage_key()) or {}
        )
        existing_data.update(data)
        await Storage.set(self.session_id, self.telemetry_storage_key(), data)

    async def capture_value(self, key, value) -> None:
        await self.capture({key: value})

    async def capture_average(self, key, value) -> None:
        existing_data = (
            await Storage.get(self.session_id, self.telemetry_storage_key()) or {}
        )
        if key not in existing_data:
            existing_data[key] = {"count": 0, "average": 0.0}
        prev_count = existing_data[key]["count"]
        existing_data[key]["count"] += 1
        existing_data[key]["average"] = (
            (existing_data[key]["average"] * prev_count) + value
        ) / existing_data[key]["count"]
        await Storage.set(self.session_id, self.telemetry_storage_key(), existing_data)

    async def recall(self) -> None:
        await Storage.get(self.session_id, self.telemetry_storage_key())

    async def increment_key(self, key) -> None:
        existing_data = (
            await Storage.get(self.session_id, self.telemetry_storage_key()) or {}
        )
        if key not in existing_data:
            existing_data[key] = 0
        existing_data[key] += 1
        await Storage.set(self.session_id, self.telemetry_storage_key(), existing_data)

    async def recall_key(self, key) -> Any | None:
        existing_data = (
            await Storage.get(self.session_id, self.telemetry_storage_key()) or {}
        )
        return existing_data[key] if key in existing_data else None


def lifecycle_logger(
    func,
) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        self.log.debug(f"{func.__name__} started")
        result = func(self, *args, **kwargs)
        self.log.debug(f"{func.__name__} finished")
        return result

    return wrapper
