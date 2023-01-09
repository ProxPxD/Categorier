from abstractTest import AbstractTest


class IdeasTest(AbstractTest):

    def test_default_add_idea_mode(self):
        name = 'default'

        self.execute(name)
        by_index = self.ideas_list.get_node(0)
        by_name = self.ideas_list.get_node(name)

        self.assertEqual(name, by_index.get_content())
        self.assertEqual(name, by_name.get_content())

    def test_add_idea_with_descriptions(self):
        name = 'with_description'
        description = 'custom and detailed description'
        self.execute(f'{name} {F.DESCRIPTIONS} {description}')


        self.assertEqual(name, category.name)
        self.assertEqual(description, category.get_description())

    def test_add_idea_with_categories(self):
        self.fail()

    def test_add_idea_with_categories_and_descriptions(self):
        self.fail()
