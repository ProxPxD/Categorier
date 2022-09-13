from singleDescriptable import SingleDescriptable
from description import Description


class Category(SingleDescriptable):
    _categories = {}

    @classmethod
    def get_category(cls, name):
        return cls._categories[name] if name in cls._categories else None

    @classmethod
    def get_categories(cls, *names):
        categories = (cls.get_category(name) for name in names)
        categories = [category for category in categories if category]
        return categories

    def __init__(self, name: str, description: str = ''):
        if name in Category._categories:
            raise ValueError
        Category._categories[name] = self
        self.name = name
        self._description = Description(description)

    def _get_all_descriptions(self) -> list[str]:
        return self._description.get_all_descriptions()
