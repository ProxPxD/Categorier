import configurations
from abstractTest import AbstractTest
from category import Category
from commandManager import Flags as F, to_short_flag


class CategoriesTest(AbstractTest):

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        configurations.remove_file(configurations.Paths.CATEGORIES_TESTS_PATH)

    def test_add_category(self):
        name = 'default'

        self.execute(f'{F.CATEGORY} {name}')

        self.assertEqual(len(Category.get_all_categories()), 1)
        category: Category = Category.get_category(name)

        self.assertEqual(name, category.name)

    def test_add_category_short(self):
        name = 'default_short'
        self.execute(f'{to_short_flag(F.CATEGORY)} {name}')

        by_name: Category = Category.get_category(name)
        by_index: Category = Category.get_category(0)

        self.assertEqual(name, by_index.name)
        self.assertEqual(name, by_name.name)

    def test_add_category_with_description(self):
        name = 'with_description'
        description = 'custom and detailed description'
        self.execute(f'{F.CATEGORY} {name} {F.DESCRIPTIONS} {description}')

        category: Category = Category.get_category(name)

        self.assertEqual(name, category.name)
        self.assertEqual(description, category.get_description())

    def test_add_category_with_description_short(self):
        name = 'with_description_short'
        description = 'custom and detailed description'
        self.execute(f'{to_short_flag(F.CATEGORY)} {name} {to_short_flag(F.DESCRIPTIONS)} {description}')

        category: Category = Category.get_category(name)

        self.assertEqual(name, category.name)
        self.assertEqual(description, category.get_description())

    def test_add_category_with_subcategories(self):
        main_name = 'with_subcategories'
        sub_names = ('sub1', 'sub2', 'sub3')

        for sub_name in sub_names:
            self.execute(f'{to_short_flag(F.CATEGORY)} {sub_name}')
        self.execute(f'{to_short_flag(F.CATEGORY)} {main_name} {" ".join(sub_names)}')

        main_category: Category = Category.get_category(main_name)

        self.assertEqual(main_name, main_category.name)
        sub_categories: list[Category] = main_category.get_subcategories()
        for sub_category, sub_name in zip(sub_categories, sub_names):
            self.assertEqual(sub_category.name, sub_name)

    def test_add_category_with_subcategories_flag(self):
        main_name = 'with_subcategories_flag'
        sub_names = ('sub1_f', 'sub2_f', 'sub3_f')

        for sub_name in sub_names:
            self.execute(f'{to_short_flag(F.CATEGORY)} {sub_name}')
        self.execute(f'{to_short_flag(F.CATEGORY)} {main_name} {F.SUBS} {" ".join(sub_names)}')

        main_category: Category = Category.get_category(main_name)

        self.assertEqual(main_name, main_category.name)
        sub_categories: list[Category] = main_category.get_subcategories()
        for sub_category, sub_name in zip(sub_categories, sub_names):
            self.assertEqual(sub_category.name, sub_name)

    def test_add_category_with_subcategories_and_description(self):
        main_name = 'with_subcategories_and_descriptions'
        description = 'custom and detailed description'
        sub_names = ('sub1_d', 'sub2_d', 'sub3_d')
        sub_descriptions = ('sd1', 'sd2', 'sd3')

        for sub_name, sub_description in zip(sub_names, sub_descriptions):
            self.execute(f'{to_short_flag(F.CATEGORY)} {sub_name} {F.DESCRIPTIONS} {sub_description}')
        self.execute(f'{to_short_flag(F.CATEGORY)} {main_name} {F.SUBS} {" ".join(sub_names)} {F.DESCRIPTIONS} {description}')

        main_category: Category = Category.get_category(main_name)

        self.assertEqual(main_name, main_category.name)
        sub_categories: list[Category] = main_category.get_subcategories()
        for sub_category, sub_name in zip(sub_categories, sub_names):
            self.assertEqual(sub_category.name, sub_name)

    def test_remove_category_by_number(self):
        self.remove_all_categories()
        name = 'to_remove'

        self.execute(f'{F.CATEGORY} {name}')
        self.assertEqual(len(Category.get_all_categories()), 1)

        by_name: Category = Category.get_category(name)
        by_index: Category = Category.get_category(0)
        self.assertEqual(name, by_index.name)
        self.assertEqual(name, by_name.name)

        self.execute(f'{F.CATEGORY} {F.REMOVE} 0')
        self.assertEqual(len(Category.get_all_categories()), 0, msg='The category has not been removed (by index)')

    def test_remove_category_by_name(self):
        self.remove_all_categories()
        name = 'to_remove'

        self.execute(f'{F.CATEGORY} {name}')
        self.assertEqual(len(Category.get_all_categories()), 1)

        by_name: Category = Category.get_category(name)
        by_index: Category = Category.get_category(0)
        self.assertEqual(name, by_index.name, msg='Wrong by name search')
        self.assertEqual(name, by_name.name, msg='Wrong by index search')

        self.execute(f'{F.CATEGORY} {F.REMOVE} {name}')
        self.assertEqual(len(Category.get_all_categories()), 0, msg='The category has not been removed (by name)')

    def test_remove_subcategory(self):
        self.remove_all_categories()
        main_name = 'with_subcategories'
        sub_names = ('sub1', 'sub2', 'sub3')

        for sub_name in sub_names:
            self.execute(f'{to_short_flag(F.CATEGORY)} {sub_name}')
        self.execute(f'{to_short_flag(F.CATEGORY)} {main_name} {" ".join(sub_names)}')

        main_category: Category = Category.get_category(main_name)

        self.execute(f'{F.CATEGORY} {F.REMOVE} {sub_names[0]}')

        self.assertIsNone(Category.get_category(sub_names[0]), msg='Category not removed')
        self.assertEqual(len(main_category.get_subcategories()), 2, msg='Wrong number of categories')
        self.assertIsNone(next((category for category in main_category.get_subcategories() if category.name == sub_names[0]), None), msg='The category is still in subcategories or a wrong category has been returned')


