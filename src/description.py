from descriptable import Descriptable


class Description(Descriptable):

    def __init__(self, *descriptions: str):
        self._descriptions = list(descriptions)

    def _get_all_descriptions(self) -> list[str]:
        return self._descriptions

    def get_all_descriptions(self):
        return self._descriptions

    def __str__(self):
        if not self._descriptions:
            return '[]'
        if len(self._descriptions) == 1:
            return self._descriptions[0]
        return '\n'.join(self._descriptions)
