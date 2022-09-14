from abc import ABC

from descriptable import Descriptable


class MultiDescriptable(Descriptable, ABC):

    def get_all_descriptions(self) -> list[str]:
        return self._get_all_descriptions()

    def add_description(self, description: str, index: int = -1):
        self._add_description(description, index)

    def add_all_descriptions(self, descriptions: list[str]):
        for description in descriptions:
            self._add_description(description)

    def change_description(self, description: str, index: int):
        self._get_all_descriptions()[index] = description

    def remove_description(self, index: int = 0) -> None:
        self._remove_description(index)

    def remove_last_description(self):
        self._remove_description(len(self._get_all_descriptions()) - 1)

    def remove_first_description(self):
        self._remove_description(0)
