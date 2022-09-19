import unittest

from tests.categoriesTest import CategoriesTest


tests = [
    CategoriesTest,
]


def main():
    unittest.main(exit=False, verbosity=0)

# python -m unittest discover -s tests -p *Test.py

if __name__ == '__main__':
    main()
