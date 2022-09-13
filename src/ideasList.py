from __future__ import annotations

from category import Category
from idea import Idea


class IdeasList:
    def __init__(self):
        self._ideas: list[Idea] = []

    def add(self, idea: Idea):
        self._ideas.append(idea)

    def add(self, content: str, categories: list[str | Category]):
        self.add(Idea(content, categories))

    def __len__(self):
        return len(self._ideas)

    def __str__(self):
        return str(self._ideas)
