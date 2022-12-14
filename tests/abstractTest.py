from __future__ import annotations

import abc
import unittest

from categorierCli import CategorierCli
from nodes import NodesManager, Paths


class AbstractTest(unittest.TestCase, abc.ABC):

    half_sep_length = 40
    currentResult = None

    total = 0
    failure = 0
    errors = 0
    skipped = 0

    cli = CategorierCli()

    test_path = Paths.RESOURCES / 'test_data.yml'

    @classmethod
    def print_sep_with_text(cls, text: str, sep: str = '*') -> None:
        with_sep_lines = sep * cls.half_sep_length + f' {text} ' + sep * cls.half_sep_length
        over_length = len(with_sep_lines) - cls.half_sep_length*2
        to_print = with_sep_lines[over_length//2 : -over_length//2]
        print(to_print)

    @classmethod
    def setUpClass(cls) -> None:
        cls.print_sep_with_text(f'Starting {cls._get_test_name()} tests!')

    @classmethod
    @abc.abstractmethod
    def _get_test_name(cls) -> str:
        return 'unnamed'

    def setUp(self) -> None:
        if not self.get_method_name().startswith('test_'):
            return
        super().setUp()
        print('- ', self.get_method_name(), end=' ... ')
        NodesManager.load_data(self.test_path)

    def tearDown(self) -> None:
        if not self.get_method_name().startswith('test_'):
            return
        super().tearDown()
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)

        is_error = any(test == self for test, text in result.errors)
        is_failure = any(test == self for test, text in result.failures)
        is_skipped = any(test == self for test, text in result.skipped)
        passed = not (is_error or is_failure or is_skipped)

        self.__class__.total += 1
        if is_error:
            self.__class__.errors += 1
        if is_failure:
            self.__class__.failure += 1
        if is_skipped:
            self.__class__.skipped += 1

        print('PASS' if passed else 'ERROR' if is_error else 'FAIL' if is_failure else 'SKIP' if is_skipped else
        'WRONG UNIT TEST OUTCOME CHECKING! Investigate (possible incompatible with a python newer than 3.10)')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.print_statistics(percentage=False)

    @classmethod
    def print_statistics(cls, failure=None, errors=None, skipped=None, total=None, *, short=False, percentage=True):
        if failure is None:
            failure = cls.failure
        if errors is None:
            errors = cls.errors
        if skipped is None:
            skipped = cls.skipped
        if total is None:
            total = cls.total
        failed = failure + errors
        passed = total - failed - skipped
        if short:
            print(f'({failure}F, {errors}E, {passed}P)/{total}')
        else:
            print(f'Failed: {failed} (Failures: {failure}, Errors: {errors}), Passed: {passed}, Total: {total}')
        if percentage:
            print(
                f'Failed: {100 * failed / total:.1f}% (Failures: {100 * failure / total:.1f}%, Errors: {100 * errors / total:.1f})%, Passed: {100 * passed / total:.1f}%')

    def get_method_name(self) -> str:
        return self.id().split('.')[-1]

    def run(self, result: unittest.result.TestResult | None = ...) -> unittest.result.TestResult | None:
        self.currentResult = result
        unittest.TestCase.run(self, result)