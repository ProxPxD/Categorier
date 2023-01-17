from parameterized import parameterized

from abstractCategorierTest import AbstractCategorierTest
from categorierCli import Keywords as K
from nodes import NodesManager


class FlatConnectingTest(AbstractCategorierTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Flat Connecting'

	@parameterized.expand([
		('simple_single_case_add', ['g1', 'g2'], ['p'], [['g1', 'g2']], K.ADD),
		('common_ancestor_add', ['g1', 'g2', 'g3'], ['p1', 'p2'], [['g1', 'g2'], ['g2', 'g3']], K.ADD),
		('parent_in_grandparents_add', ['g1', 'g2', 'g3'], ['p1', 'p2'], [['g1', 'p2'], ['g2', 'g3']], K.ADD),
		('simple_single_case_cat', ['g1', 'g2'], ['p'], [['g1', 'g2']], K.CAT),
		('common_ancestor_cat', ['g1', 'g2', 'g3'], ['p1', 'p2'], [['g1', 'g2'], ['g2', 'g3']], K.CAT),
		('parent_in_grandparents_cat', ['g1', 'g2', 'g3'], ['p1', 'p2'], [['g1', 'p2'], ['g2', 'g3']], K.CAT),
	])
	def test_flat_option(self, node_name: str, e_ancestors: list[str], all_parents: list[str], all_grandparents: list[list[str]], flag: str):
		for node in self.flatten_string_lists(all_parents, all_grandparents, unique=True):
			self.cli.parse(f'm {K.ADD} {node}')
		if flag != K.ADD:
			self.cli.parse(f'm {K.ADD} {node_name}')

		for parent, grandparents in zip(all_parents, all_grandparents):
			self.cli.parse(f'm {K.CAT} {parent} {" ".join(grandparents)}')

		self.cli.parse(f'm {flag} {node_name} {" ".join(all_parents)} {K.FLAT_LONG}')

		node = NodesManager.get_node(node_name)
		self.assertCountEqual(e_ancestors, node.parents.get_names())

	@parameterized.expand([
		('not_interconnected_ancestors_add',
										['p1', 'p2', 'g1', 'g2', 'g3', 'g4'],
										['p1', 'p2'],
										[['g1', 'g2'], ['g3', 'g4']],
		 								K.ADD),
		('common_grandparent_add',
								['p1', 'p2', 'g1', 'g2', 'g3'],
								['p1', 'p2'],
								[['g1', 'g2'], ['g2', 'g3']],
		 						K.ADD),
		('parent_as_grandparent_add',
								['p1', 'p2', 'p3'],
								['p1', 'p2', 'p3'],
								[[], [], ['p1', 'p2']],
		 						K.ADD),
		('duplicated_ancestors_add',
								['p', 'g'],
								['p', 'p', 'p'],
								[['g', 'g'], ['g', 'g'], ['g', 'g']],
		 						K.CAT),
		('not_interconnected_ancestors_cat',
										['p1', 'p2', 'g1', 'g2', 'g3', 'g4'],
										['p1', 'p2'],
										[['g1', 'g2'], ['g3', 'g4']],
		 								K.CAT),
		('common_grandparent_cat',
								['p1', 'p2', 'g1', 'g2', 'g3'],
								['p1', 'p2'],
								[['g1', 'g2'], ['g2', 'g3']],
		 						K.CAT),
		('parent_as_grandparent_cat',
								['p1', 'p2', 'p3'],
								['p1', 'p2', 'p3'],
								[[], [], ['p1', 'p2']],
		 						K.CAT),
		('duplicated_ancestors_cat',
								['p', 'g'],
								['p', 'p', 'p'],
								[['g', 'g'], ['g', 'g'], ['g', 'g']],
		 						K.CAT),
	])
	def test_add_with_all_flat_option(self, node_name: str, e_all_parents: list[str], all_parents: list[str], all_grandparents: list[list[str]], flag: str):
		for node in self.flatten_string_lists(all_parents, all_grandparents, unique=True):
			self.cli.parse(f'm {K.ADD} {node}')
		if flag != K.ADD:
			self.cli.parse(f'm {K.ADD} {node_name}')

		for parent, grandparents in zip(all_parents, all_grandparents):
			self.cli.parse(f'm {K.CATEGORIZE} {parent} {" ".join(grandparents)}')

		self.cli.parse(f'm {flag} {node_name} {K.ALL_FLAT_LONG} {" ".join(all_parents)}')

		node = NodesManager.get_node(node_name)
		for parent in e_all_parents:
			parent_node = node.parents.get_node(parent)
			self.assertIn(parent, node.parents, 'expected parent does not exist')
			self.assertIn(node_name, parent_node.children, 'node not in parent\'s children')

		self.assertCountEqual(e_all_parents, list(node.get_all_ancestors_names()), 'Amount of ancestors does not match')

