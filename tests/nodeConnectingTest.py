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
		self.cli.parse(f'm {K.ADD} {node_name}')

		self.assertTrue(NodesManager.is_in_data(node_name), 'Node creation error')
		node = NodesManager.get_node(node_name)
		self.assertCountEqual(parents, node.parents.get_all(), 'Parent nodes creation error')
		self.assertCountEqual(children, node.children.get_all(), 'Children nodes creation error')

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
			for grandparent in filter(NodesManager.is_not_in_data, grandparents):
				self.cli.parse(f'm {K.ADD} {grandparent}')
			self.cli.parse(f'm {K.ADD} {parent} {" ".join(grandparents)}')

		self.cli.parse(f'm {K.ADD} {node_name} {" ".join(all_parents)}')

		node = NodesManager.get_node(node_name)
		for parent, grandparents in zip(e_all_parents, e_all_grandparents):
			parent_node = node.parents.get_node(parent)
			self.assertIn(parent, node.parents, 'expected parent does not exist')
			self.assertIn(node_name, parent_node.children, 'node not in parent\'s children')
			for grandparent in grandparents:
				grandparent_node = parent_node.parents.get_node(grandparent)
				self.assertIn(grandparent, node.parents.get_node(parent).parents, 'expected grandparent does not exist')
				self.assertIn(parent, grandparent_node.children, 'node not in parent\'s children (grandparent level)')

		e_ancestors = set(e_all_parents) | set(*e_all_grandparents)
		self.assertCountEqual(e_ancestors, list(node.get_all_ancestors_names()), 'Amount of ancestors does not match')

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
		self.cli.parse(f'm {K.ADD} {node_name}')
		for child, grandchildren in zip(all_children, all_grandchildren):
			self.cli.parse(f'm {K.ADD} {child} {node_name}')
			for grandchild in filter(NodesManager.is_not_in_data, grandchildren):
				self.cli.parse(f'm {K.ADD} {grandchild} {child}')

		node = NodesManager.get_node(node_name)
		for child, grandchildren in zip(e_all_children, e_all_grandchildren):
			child_node = node.children.get_node(child)
			self.assertIn(child, node.children, 'expected child does not exist')
			self.assertIn(node_name, child_node.parents, 'node not in child\'s parents')
			for grandchild in grandchildren:
				grandchild_node = child_node.children.get_node(grandchild)
				self.assertIn(grandchild, node.children.get_node(child).parents, 'expected grandparent does not exist')
				self.assertIn(child, grandchild_node.parents, 'node not in child\'s parents (grandchild level)')

		e_descendants = set(e_all_children) | set(*e_all_grandchildren)
		self.assertCountEqual(e_descendants, list(node.get_all_ancestors_names()), 'Amount of descendants does not match')

	@parameterized.expand([
		('normal_removal', [['p2']], ['c'], [['p1', 'p2']], ['p1']),
		('common_parent', [['p1'], ['p3']], ['c1', 'c2'], [['p1', 'p2'], ['p2', 'p3']], ['p2']),
	])
	def test_remove_parent_nodes(self, name: str, e_all_parents: list[str], children: list[str], all_parents: list[str], to_removes: list[str]):
		for child, parents in zip(children, all_parents):
			for parent in parents:
				self.cli.parse(f'm {K.ADD} {parent}')
			self.cli.parse(f'm {K.ADD} {child} {" ".join(parents)}')

		for to_remove in to_removes:
			self.cli.parse(f'm {K.DELETE} {to_remove}')  # TODO: correct test after addint the confirmation of the removal

		for child, e_parents in zip(children, e_all_parents):
			node = NodesManager.get_node(child)
			self.assertCountEqual(e_parents, node.parents, 'parent node has not been deleted')

	@parameterized.expand([
		('normal_removal', [['c2']], ['p'], [['c1', 'c2']], ['c1']),
		('common_children', [['c1'], ['c3']], ['p1', 'p2'], [['c1', 'c2'], ['c2', 'c3']], ['c2']),
	])
	def test_remove_children_nodes(self, name: str, e_all_children: list[str], parents: list[str], all_children: list[str], to_removes: list[str]):
		for parent, children in zip(parents, all_children):
			self.cli.parse(f'm {K.ADD} {parent}')
			for child in children:
				self.cli.parse(f'm {K.ADD} {child} {" ".join(parents)}')

		for to_remove in to_removes:
			self.cli.parse(f'm {K.DEL} {to_remove}')  # TODO: correct test after addint the confirmation of the removal

		for parent, e_children in zip(parents, e_all_children):
			node = NodesManager.get_node(parent)
			self.assertCountEqual(e_children, node.children, 'parent node has not been deleted')