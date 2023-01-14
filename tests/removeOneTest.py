from parameterized import parameterized

from abstractTest import AbstractTest
from nodes import NodesManager
from categorierCli import Keywords as K


class RemoveOneTest(AbstractTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Remove One'

	@parameterized.expand([
		('not_interconnected_ancestors',
										['g1', 'g2', 'g3', 'g4'],
										['p1', 'p2'],
										['p1', 'p2'],
										[['g1', 'g2'], ['g3', 'g4']]),
		('common_grandparent',
								['g1', 'g2', 'g3'],
								['p1', 'p2'],
								['p1', 'p2'],
								[['g1', 'g2'], ['g2', 'g3']]),
		('remove_unwanted_node',
								['p1', 'g'],
								['p2'],
								['p1', 'p2', 'p3'],
								[[], [], ['p1', 'p2', 'g']]),
	])
	def test_delete_one_ancestor_from_node(self, node_name: str, e_parents: list[str], parents_to_remove: list[str], all_parents: list[str], all_grandparents: list[list[str]]):
		for parent, grandparents in zip(all_parents, all_grandparents):
			for grandparent in filter(NodesManager.is_not_in_data, grandparents):
				self.cli.parse(f'm {K.ADD_FULL} {grandparent}')
			self.cli.parse(f'm {K.ADD_FULL} {parent} {" ".join(grandparents)}')

		self.cli.parse(f'm {K.ADD_FULL} {node_name} {" ".join(all_parents)}')

		self.cli.parse(f'm {K.DELETE_FULL} {" ".join(parents_to_remove)} {K.FROM} {node_name}')

		node = NodesManager.get_node(node_name)
		self.assertCountEqual(e_parents, node.parents)