from abc import ABC, abstractmethod


class Descriptable(ABC):

    @classmethod
    def __subclasshook__(cls, subclass):
        necessary_methods = [cls._get_all_descriptions, cls._add_description, cls._remove_description]
        method_names = (method.__name__ for method in necessary_methods)
        has_method = lambda method: any(method in parent_class.__dict__ for parent_class in subclass.__mro__)
        return all(has_method(method) for method in method_names)

    @abstractmethod
    def _get_all_descriptions(self) -> list[str]:
        raise NotImplementedError

    def _add_description(self, description: str, index: int = -1):
        descriptions = self._get_all_descriptions()
        descriptions.insert(index, description)
        # self.save_all_descriptions(descriptions)

    def _remove_description(self, index: int = 0) -> None:
        descriptions = self._get_all_descriptions()
        if len(descriptions) > index:
            del descriptions[index]
        # self.save_all_descriptions(descriptions)

    def __eq__(self, other):
        return self._get_all_descriptions() == other._get_all_descriptions()
