from abstractTest import AbstractTest

from parameterized import parameterized

from nodes import NodesManager
from categorierCli import Keywords as K


class NodeConnectingTest(AbstractTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Node connecting'

	@parameterized.expand([
		('only_node', [], []),
		('with_children', [], ['child1', 'child2']),
		('with_parents', ['parent1', 'parent2'], []),
		('with_children_and_parents', ['parent1', 'parent2'], ['child1', 'child2']),
	])
	def test_add_node(self, node_name: str, parents: list[str], children: list[str]):
		self.cli.parse(f'm {K.ADD_FULL} {node_name}')

		self.assertTrue(NodesManager.is_in_data(node_name), 'Node creation error')
		node = NodesManager.get_node(node_name)
		self.assertCountEqual(parents, node.parents.get_names(), 'Parent nodes creation error')
		self.assertCountEqual(children, node.children.get_names(), 'Children nodes creation error')

	@parameterized.expand([
		('not_interconnected_ancestors',
										['p1', 'p2'],
										[['g1', 'g2'], ['g3', 'g4']],
										['p1', 'p2'],
										[['g1', 'g2'], ['g3', 'g4']]),
		('common_grandparent',
								['p1', 'p2'],
								[['g1', 'g2'], ['g2', 'g3']],
								['p1', 'p2'],
								[['g1', 'g2'], ['g2', 'g3']]),
		('parent_as_grandparent',
								['p1', 'p2', 'p3'],
								[[], [], ['p1', 'p2']],
								['p1', 'p2', 'p3'],
								[[], [], ['p1', 'p2']]),
		('duplicated_ancestors',
								['p'],
								[['g']],
								['p', 'p', 'p'],
								[['g', 'g'], ['g', 'g'], ['g', 'g']]),
	])
	def test_add_ancestors_to_node(self, node_name: str, e_all_parents: list[str], e_all_grandparents: list[list[str]], all_parents: list[str], all_grandparents: list[list[str]]):
		for parent, grandparents in zip(all_parents, all_grandparents):
			for grandparent in grandparents:
				self.cli.parse(f'm {K.ADD_FULL} {grandparent}')
			self.cli.parse(f'm {K.ADD_FULL} {parent} {" ".join(grandparents)}')

		self.cli.parse(f'm {K.ADD_FULL} {node_name} {" ".join(all_parents)}')

		node = NodesManager.get_node(node_name)
		for parent, grandparents in zip(e_all_parents, e_all_grandparents):
			parent_node = node.parents.get(parent)
			self.assertIn(parent, node.parents, 'expected parent does not exist')
			self.assertIn(node_name, parent_node.children, 'node not in parent\'s children')
			for grandparent in grandparents:
				grandparent_node = parent_node.parents.get(grandparent)
				self.assertIn(grandparent, node.parents.get(parent).parents, 'expected grandparent does not exist')
				self.assertIn(parent, grandparent_node.children, 'node not in parent\'s children (grandparent level)')

		e_ancestors = set(e_all_parents) | set(*e_all_grandparents)
		self.assertCountEqual(e_ancestors, list(node.get_all_ancestors_names()))

	@parameterized.expand([
		('not_interconnected_descendants',
										['c1', 'c2'],
										[['g1', 'g2'], ['g3', 'g4']],
										['c1', 'c2'],
										[['g1', 'g2'], ['g3', 'g4']]),
		('common_grandchildren',
								['c1', 'c2'],
								[['g1', 'g2'], ['g2', 'g3']],
								['c1', 'c2'],
								[['g1', 'g2'], ['g2', 'g3']]),
		('children_as_grandchildren',
								['c1', 'c2', 'c3'],
								[[], [], ['c1', 'c2']],
								['c1', 'c2', 'c3'],
								[[], [], ['c1', 'c2']]),
		('duplicated_descendants',
								['c'],
								[['g']],
								['c', 'c', 'c'],
								[['g', 'g'], ['g', 'g'], ['g', 'g']]),
	])
	def test_add_descendatns_to_node(self, node_name: str, e_all_children: list[str], e_all_grandchildren: list[list[str]], all_children: list[str], all_grandchildren: list[list[str]]):
		self.cli.parse(f'm {K.ADD_FULL} {node_name}')
		for child, grandchildren in zip(all_children, all_grandchildren):
			self.cli.parse(f'm {K.ADD_FULL} {child} {node_name}')
			for grandchild in grandchildren:
				self.cli.parse(f'm {K.ADD_FULL} {grandchild} {child}')

		node = NodesManager.get_node(node_name)
		for child, grandchildren in zip(e_all_children, e_all_grandchildren):
			child_node = node.children.get(child)
			self.assertIn(child, node.children, 'expected child does not exist')
			self.assertIn(node_name, child_node.parents, 'node not in child\'s parents')
			for grandchild in grandchildren:
				grandchild_node = child_node.children.get(grandchild)
				self.assertIn(grandchild, node.children.get(child).parents, 'expected grandparent does not exist')
				self.assertIn(child, grandchild_node.parents, 'node not in child\'s parents (grandchild level)')

		e_descendants = set(e_all_children) | set(*e_all_grandchildren)
		self.assertCountEqual(e_descendants, list(node.get_all_ancestors_names()))
