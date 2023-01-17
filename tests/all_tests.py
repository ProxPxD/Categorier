import unittest

from abstractTest import AbstractTest
from changeTest import ChangeTest
from descriptionTest import DescriptionTest
from flatConnectingTest import FlatConnectingTest
from multipleNodesTest import MultipleNodesTest
from nodeConnectingTest import NodeConnectingTest
from nodeSettingValuesTest import NodeSettingValuesTest
from deleteParentTest import DeleteParentTest
from searchTest import SearchTest

tests = [
    NodeConnectingTest,
    MultipleNodesTest,
    DescriptionTest,
    FlatConnectingTest,
    NodeSettingValuesTest,
    DeleteParentTest,
    ChangeTest,
    SearchTest,
]


def main():
    failure, errors, total, skipped = 0, 0, 0, 0
    for test_class in tests:
        test = test_class()
        unittest.main(module=test, exit=False)

        failure += test.failure
        errors += test.errors
        total += test.total
        skipped += test.skipped

    print()
    print('#' * (2 * AbstractTest.half_sep_length))
    print('Total test statistics:')
    AbstractTest.print_statistics(failure, errors, skipped, total)
# python -m unittest discover -s tests -p *Test.py


if __name__ == '__main__':
    main()
