from parameterized import parameterized

from abstractTest import AbstractTest
from nodes import NodesManager
from categorierCli import Keywords as K


class DeleteAncestorTest(AbstractTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Delete Just Ancestor'

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
	def test_delete_one_ancestor_from_node(self, name: str, e_parents: list[str], parents_to_remove: list[str], all_parents: list[str], all_grandparents: list[list[str]]):
		for parent, grandparents in zip(all_parents, all_grandparents):
			for grandparent in filter(NodesManager.is_not_in_data, grandparents):
				self.cli.parse(f'm {K.ADD} {grandparent}')
			self.cli.parse(f'm {K.ADD} {parent} {" ".join(grandparents)}')

		self.cli.parse(f'm {K.ADD} {name} {" ".join(all_parents)}')

		self.cli.parse(f'm {K.DELETE} {K.JUST} {" ".join(parents_to_remove)} {K.FROM} {name}')

		node = NodesManager.get_node(name)
		self.assertCountEqual(e_parents, node.parents.names)