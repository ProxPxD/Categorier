from parameterized import parameterized

from abstractTest import AbstractTest
from categorierCli import Keywords as K
from nodes import NodesManager


class FlatConnectingTest(AbstractTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Flat Option'

	@parameterized.expand([
		('simple_single_case', ['g1', 'g2'], ['p'], [['g1', 'g2']]),
		('common_ancestor', ['g1', 'g2', 'g3'], ['p1', 'p2'], [['g1', 'g2'], ['g2', 'g3']]),
		('parent_in_grandparents', ['g1', 'g2', 'g3'], ['p1', 'p2'], [['g1', 'p2'], ['g2', 'g3']]),
	])
	def test_add_with_flat_option(self, node_name: str, e_ancestors: list[str], all_parents: list[str], all_grandparents: list[list[str]]):
		for parent, grandparents in zip(all_parents, all_grandparents):
			for grandparent in filter(NodesManager.is_not_in_data, grandparents):
				self.cli.parse(f'm {K.ADD_FULL} {grandparent}')
			self.cli.parse(f'm {K.ADD_FULL} {parent} {" ".join(grandparents)}')

		self.cli.parse(f'm {K.ADD_FULL} {node_name} {" ".join(all_parents)} {K.FLAT_LONG}')

		node = NodesManager.get_node(node_name)
		self.assertCountEqual(e_ancestors, node.parents.get_names())

