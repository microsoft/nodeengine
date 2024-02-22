import contextlib
import json
import os
import uuid
from pathlib import Path
from typing import IO, Any


class Storage:
    root_path: str = "storage"

    @staticmethod
    async def get_file_name(session_id, key) -> str:
        session_path = Path(Storage.root_path, session_id)
        if not os.path.exists(session_path):
            os.makedirs(session_path, exist_ok=True)

        return str(Path(session_path, key).absolute())

    @staticmethod
    async def _get_temp_file_name(session_id) -> str:
        return await Storage.get_file_name(session_id, f"_temp-{uuid.uuid4().hex}")

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
    async def stream(session_id, key) -> contextlib.closing[IO[str]]:
        filename = await Storage.get_file_name(session_id, key)
        if os.path.exists(filename):
            return contextlib.closing(open(filename, mode="r"))
        else:
            raise FileNotFoundError(f"file not found: {filename}")

    @staticmethod
    async def set(session_id, key, value, raw=False) -> None:
        # write to temp file first to avoid corrupting the file if the process is interrupted
        # or json encoding fails
        file_path = await Storage.get_file_name(session_id, key)
        temp_file_path = await Storage._get_temp_file_name(session_id)

        try:
            with open(temp_file_path, mode="w") as temp_file:
                if raw and isinstance(value, str):
                    temp_file.write(value)
                else:
                    json.dump(value, temp_file, indent=2)

            # this is a move/rename operation
            os.replace(temp_file_path, file_path)

        finally:
            Path(temp_file_path).unlink(missing_ok=True)

    @staticmethod
    async def append(session_id, key, value, raw=False) -> None:
        file_path = await Storage.get_file_name(session_id, key)
        with open(file_path, mode="a") as file:
            if raw and isinstance(value, str):
                file.write(value)
            else:
                json.dump(value, file)

    @staticmethod
    async def delete(session_id, key) -> None:
        filename = await Storage.get_file_name(session_id, key)
        if os.path.exists(filename):
            os.remove(filename)

    @staticmethod
    async def list(session_id) -> list[str]:
        files = list(Path(Storage.root_path).glob(f"{session_id}_*"))
        prepend = Path(Storage.root_path)
        filenames = []
        for file in files:
            filename = str(file).replace(f"{prepend}", "")[1:]
            filenames.append(filename)
        return filenames
