from descriptable import Descriptable


class Description(Descriptable):

    def __init__(self, *descriptions: str):
        self._descriptions = [description for description in descriptions if description]

    def _get_all_descriptions(self) -> list[str]:
        return self._descriptions

    def get_all_descriptions(self):
        return self._descriptions

    def __str__(self):
        if not self._descriptions:
            return '[]'
        if len(self._descriptions) == 1:
            return str(self._descriptions[0])
        return '\n'.join(self._descriptions)

    def __bool__(self):
        return self._descriptions is not None and len(self._descriptions) > 0