from singleDescriptable import SingleDescriptable
from description import Description
import configurations


class Category(SingleDescriptable):
    _categories = {}

    @classmethod
    def load_categories(cls):
        cls._categories = {category.name: category for category in configurations.load_list(configurations.Saved.CATEGORIES_LIST_PATH)}

    @classmethod
    def get_category(cls, name):
        return cls._categories[name] if name in cls._categories else None

    @classmethod
    def get_categories(cls, names):
        categories = (cls.get_category(name) for name in names)
        categories = [category for category in categories if category]
        return categories

    @classmethod
    def get_all_categories(cls):
        return list(cls._categories.values())

    @classmethod
    def remove_category(cls, name: str) -> None:
        del cls._categories[name]

    def __init__(self, name: str, description: str = '', sub_categories: list = None):
        if name in Category._categories:
            raise ValueError
        Category._categories[name] = self
        self.name = name
        self._description = Description(description)
        self._sub_categories = sub_categories or []

    def _get_all_descriptions(self) -> list[str]:
        return self._description.get_all_descriptions()

    def __str__(self):
        string = str(self.name)
        if self._sub_categories:
            sub_categories_str = str([str(category) for category in self._sub_categories])[1:-1]
            string += f'({sub_categories_str})'
        if self._description:
            string += f': {self._description}'
        return string
