from parameterized import parameterized

from abstractTest import AbstractTest
from categorierCli import Keywords as K
from nodes import NodesManager


class AllFlatConnectingTest(AbstractTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'All Flat Connecting'

	@parameterized.expand([
		('not_interconnected_ancestors',
										['p1', 'p2', 'g1', 'g2', 'g3', 'g4'],
										['p1', 'p2'],
										[['g1', 'g2'], ['g3', 'g4']]),
		('common_grandparent',
								['p1', 'p2', 'g1', 'g2', 'g3'],
								['p1', 'p2'],
								[['g1', 'g2'], ['g2', 'g3']]),
		('parent_as_grandparent',
								['p1', 'p2', 'p3'],
								['p1', 'p2', 'p3'],
								[[], [], ['p1', 'p2']]),
		('duplicated_ancestors',
								['p', 'g'],
								['p', 'p', 'p'],
								[['g', 'g'], ['g', 'g'], ['g', 'g']]),
	])
	def test_deep_add_ancestors_to_node(self, node_name: str, e_all_parents: list[str], all_parents: list[str], all_grandparents: list[list[str]]):
		for parent, grandparents in zip(all_parents, all_grandparents):
			for grandparent in grandparents:
				self.cli.parse(f'm {K.ADD_FULL} {grandparent}')
			self.cli.parse(f'm {K.ADD_FULL} {parent} {" ".join(grandparents)}')

		self.cli.parse(f'm {K.ADD_FULL} {node_name} {K.ALL_FLAT_LONG} {" ".join(all_parents)}')

		node = NodesManager.get_node(node_name)
		for parent in e_all_parents:
			parent_node = node.parents.get_node(parent)
			self.assertIn(parent, node.parents, 'expected parent does not exist')
			self.assertIn(node_name, parent_node.children, 'node not in parent\'s children')

		self.assertCountEqual(e_all_parents, list(node.get_all_ancestors_names()), 'Amount of ancestors does not match')
