# Copyright (c) Microsoft. All rights reserved.

import json
import os
from pathlib import Path
from typing import Any

file_path = "storage"


class Storage:
    @staticmethod
    async def get_file_name(session_id, key) -> str:
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        return f"{file_path}/{session_id}_{key}"

    @staticmethod
    async def get(session_id, key, raw=False) -> Any | None:
        if not os.path.exists(await Storage.get_file_name(session_id, key)):
            return None

        filename = await Storage.get_file_name(session_id, key)
        with open(filename, mode="r") as file:
            if raw:
                contents = file.read()
            else:
                try:
                    contents = json.load(file)
                except Exception as exception:
                    raise Exception(
                        f"unable to parse storage file ({filename}) contents: {exception}"
                    )
            return contents

    @staticmethod
    async def set(session_id, key, value, raw=False) -> None:
        with open(await Storage.get_file_name(session_id, key), mode="w") as file:
            if raw and isinstance(value, str):
                file.write(value)
            else:
                json.dump(value, file, indent=2)

    @staticmethod
    async def delete(session_id, key) -> None:
        filename = await Storage.get_file_name(session_id, key)
        if os.path.exists(filename):
            os.remove(filename)

    @staticmethod
    async def list(session_id) -> list[str]:
        files = list(Path(file_path).glob(f"{session_id}_*"))
        prepend = Path(file_path)
        filenames = []
        for file in files:
            filename = str(file).replace(f"{prepend}", "")[1:]
            filenames.append(filename)
        return filenames
