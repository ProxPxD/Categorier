from __future__ import annotations

import configurations
from category import Category
from idea import Idea


class IdeasList:

    _ideas_list = None

    @classmethod
    def get(cls, test_mode=False):
        if cls._ideas_list is None:
            path = configurations.Paths.IDEAS_PATH if not test_mode else configurations.Paths.IDEAS_TESTS_PATH
            cls._ideas_list = configurations.load_list(path)
        if cls._ideas_list is None:
            cls._ideas_list = cls()
        return

    def __init__(self):
        self._ideas: list[Idea] = []

    def get(self, idea: str | int) -> Idea:
        if isinstance(idea, int):
            return self._ideas[idea] if idea < len(self._ideas) else None
        else:
            return self._get_by_name(idea)

    def _get_by_name(self, name: str) -> Idea:
        return next((idea for idea in self._ideas if idea.get_content() == name), None)

    def add(self, idea: Idea | str, categories: list[str | Category] = None):
        if not idea:
            return
        if isinstance(idea, str):
            idea = Idea(idea, categories if categories else [])
        self._ideas.append(idea)

    def remove(self, index: int) -> None:
        if index < len(self._ideas):
            del self._ideas[index]

    def remove_by_name(self, name: str):
        to_remove = self._get_by_name(name)
        if to_remove:
            self._ideas.remove(to_remove)

    def __len__(self):
        return len(self._ideas)

    def __str__(self):
        return str([str(idea) for idea in self._ideas])[1:-1] if self._ideas else '[]'

    def __iter__(self):
        return iter(self._ideas)