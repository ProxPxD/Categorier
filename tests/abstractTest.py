from __future__ import annotations

import abc
import unittest


class AbstractTest(unittest.TestCase, abc.ABC):

    half_sep_length = 40
    currentResult = None

    _manager = commandManager.CommandManager()
    ideas_list: IdeasList = configurations.load_list(Paths.IDEAS_TESTS_PATH, test_mode=True)

    @classmethod
    def print_sep_with_text(cls, text: str, sep: str = '*') -> None:
        with_sep_lines = sep * cls.half_sep_length + f' {text} ' + sep * cls.half_sep_length
        over_length = len(with_sep_lines) - cls.half_sep_length * 2
        to_print = with_sep_lines[over_length // 2: -over_length // 2]
        print(to_print)

    @classmethod
    def setUpClass(cls) -> None:
        cls.print_sep_with_text(f'Starting {type(cls).__name__.replace("Test", "")} test!')

    def setUp(self) -> None:
        super().setUp()
        print('- ', self.get_method_name(), end=' ... ')

    def get_method_name(self) -> str:
        return self.id().split('.')[-1]

    def tearDown(self) -> None:
        super().tearDown()
        ok = self.currentResult.wasSuccessful()
        errors = self.currentResult.errors
        failures = self.currentResult.failures
        print('ok' if ok else 'ERROR' if errors else 'FAIL')

    def run(self, result: unittest.result.TestResult | None = ...) -> unittest.result.TestResult | None:
        self.currentResult = result
        unittest.TestCase.run(self, result)

    def execute(self, command: str | list[str]):
        self._manager.execute(command)

    def save_all(self):
        self.save_ideas()
        self.save_categories()

    def save_ideas(self):
        configurations.save_list(self._ideas_list, Paths.IDEAS_TESTS_PATH)

    def save_categories(self):
        configurations.save_list(Category.get_all_categories(), Paths.CATEGORIES_TESTS_PATH)

    def remove_all_categories(self):
        for category in Category.get_all_categories():
            self.execute(f'{F.CATEGORY} {F.REMOVE} {category}')
