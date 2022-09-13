from __future__ import annotations

from category import Category
from description import Description
from multiDescriptable import MultiDescriptable


class Idea(MultiDescriptable):
    def __init__(self, content: str, categories: list[Category | str] = None):
        self._content = content
        self._description = Description()
        if categories and isinstance(categories[0], str):
            categories = Category.get_categories(categories)
        self._categories = categories if categories else []

    def _get_all_descriptions(self) -> list[str]:
        return self._description.get_all_descriptions()

    def __str__(self):
        categories_str = str(self._categories)[1: -1]
        string = f'{self._content} ({categories_str})'
        if self._description:
            string += f': {self._description}'
        return string