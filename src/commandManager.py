from __future__ import annotations

import shlex


class CommandManager:

    def __init__(self):
        pass

    def execute(self, command: str | list[str]):
        if isinstance(command, str):
            command = shlex.split(command)
        