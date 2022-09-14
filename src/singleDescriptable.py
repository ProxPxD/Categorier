from abc import ABC

from descriptable import Descriptable


class SingleDescriptable(Descriptable, ABC):

    def get_description(self) -> str:
        descriptions = self._get_all_descriptions()
        return descriptions[0] if descriptions else ''

    def set_description(self, description: str):
        if len(self._get_all_descriptions()):
            self.remove_description()
        self._add_description(description)

    def remove_description(self) -> None:
        self._remove_description(0)
