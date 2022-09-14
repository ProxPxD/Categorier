from __future__ import annotations

from category import Category
from idea import Idea


class IdeasList:
    def __init__(self):
        self._ideas: list[Idea] = []

    def add(self, idea: Idea | str, categories: list[str | Category] = None):
        if not idea:
            return
        if isinstance(idea, str):
            idea = Idea(idea, categories if categories else [])
        self._ideas.append(idea)

    def __len__(self):
        return len(self._ideas)

    def __str__(self):
        return str([str(idea) for idea in self._ideas])[1:-1] if self._ideas else '[]'
