from abstractTest import AbstractTest

from categorierCli import Keywords as K
from nodes import NodesManager, Node


class MultipleNodesTest(AbstractTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Multiple Nodes'

	def test_add_many_nodes(self):
		nodes = 'n1 n2 n3'.split(' ')
		self.cli.parse(f'm {K.ADD} {K.MANY} {" ".join(nodes)}')

		try:
			actual_nodes = list(map(Node.get_name, NodesManager.get_nodes(*nodes)))
		except KeyError:
			self.fail('Some node has not been created')

		self.assertCountEqual(nodes, actual_nodes, 'Some node has not been created properly')

	def test_add_many_nodes_with_common_ancestors(self):
		nodes = 'n1 n2 n3'.split(' ')
		ancestors = 'a1 a2 a3 a4'.split(' ')

		self.cli.parse(f'm {K.ADD} {K.MANY} {" ".join(ancestors)}')
		self.cli.parse(f'm {K.ADD} {K.MANY} {" ".join(nodes)} {K.TO} {" ".join(ancestors)}')

		try:
			actual_nodes = list(NodesManager.get_nodes(*nodes))
		except KeyError:
			self.fail('Some node has not been created')

		for actual in actual_nodes:
			self.assertIn(actual.name, nodes, 'Some node has not been created properly')
			self.assertCountEqual(ancestors, actual.get_all_ancestors_names(), 'Some ancestor has not been assigned properly')

	def test_add_many_with_separate_ancestors(self):
		nodes = 'n1 n2 n3'.split(' ')
		all_ancestors = [['a11', 'a12'], ['a21'], ['a31', 'a32', 'a33']]
		ancestor_strings = (' '.join(ancestors) for ancestors in all_ancestors)
		ancestors_and_string = f' {K.AND} '.join(ancestor_strings)

		flat_ancestors = set(ancestor for ancestors in all_ancestors for ancestor in ancestors)
		self.cli.parse(f'm {K.ADD} {K.MANY} {" ".join(flat_ancestors)}')
		self.cli.parse(f'm {K.ADD} {K.MANY} {" ".join(nodes)} {K.TO} {ancestors_and_string}')

		for e_node, ancestors in zip(nodes, all_ancestors):
			try:
				a_node = NodesManager.get_node(e_node)
			except KeyError:
				self.fail('Some node has not been created')

			self.assertCountEqual(ancestors, a_node.parents.get_all_names(), 'Some ancestor has not been assigned properly')
