from __future__ import annotations

import shlex
from dataclasses import dataclass


@dataclass
class Flags:
    CATEGORY = '--cat'
    DESCRIPTIONS = '--descr'
    SUBS = '--sub'
    SHOW = '--show'
    IDEAS = '--ideas'
    REMOVE = '--remove'


def to_short_flag(flag: str):
    return to_short_flag_dict[flag]


to_short_flag_dict = {
    Flags.CATEGORY: '-c',
    Flags.DESCRIPTIONS: '-d',
    Flags.SUBS: '-sub',
    Flags.SHOW: '-s',
    Flags.IDEAS: '-i',
    Flags.REMOVE: '-r',
}


class CommandManager:

    def __init__(self):
        pass

    def execute(self, command: str | list[str]):
        if isinstance(command, str):
            command = shlex.split(command)
