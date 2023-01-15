from parameterized import parameterized

from abstractTest import AbstractTest
from categorierCli import Keywords as K
from nodes import NodesManager


class DescriptionTest(AbstractTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Description'

	@parameterized.expand([
		('one_to_one', [['d']], ['d'], ['n']),
		('many_to_one', [['d1', 'd2', 'd3']], ['d1', 'd2', 'd3'], ['n']),
		('one_to_many', [['d'], ['d'], ['d'], ['d']], ['n1', 'n2', 'n3', 'n4']),
		('many_to_many_same_amount', [['d1', 'd2', 'd3'], ['d1', 'd2', 'd3'], ['d1', 'd2', 'd3']], ['d1', 'd2', 'd3'], ['n1', 'n2', 'n3']),
		('many_to_many_less_descriptions', [['d1', 'd2'], ['d1', 'd2'], ['d1', 'd2']], ['d1', 'd2'], ['n1', 'n2', 'n3']),
		('many_to_many_less_nodes', [['d1', 'd2', 'd3'], ['d1', 'd2', 'd3'], ['d1', 'd2', 'd3']], ['d1', 'd2', 'd3'], ['n1', 'n2']),
	])
	def test_add_description(self, name: str, e_descriptions_per_node: list[list[str]], descriptions: list[str], nodes: list[str]):
		self.cli.parse(f'm {K.ADD} {K.MANY} {" ".join(nodes)}')

		input_line = f'm {K.ADD} {K.DESCR} {" ".join(descriptions)} {K.TO} {" ".join(nodes)}'
		self.cli.parse(input_line)

		for node, e_descriptions in zip(nodes, e_descriptions_per_node):
			try:
				a_node = NodesManager.get_node(node)
			except KeyError:
				self.fail('Some node has not been created')

			self.assertCountEqual(e_descriptions, a_node.descriptions)

	@parameterized.expand([
		('one_to_one', [['d']], ['d'], ['n']),
		('many_to_one', [['d1', 'd2', 'd3']], ['d1', 'd2', 'd3'], ['n']),
		('one_to_many', [['d'], ['d'], ['d'], ['d']], ['n1', 'n2', 'n3', 'n4']),
		('many_to_many_same_amount', [['d1', 'd2', 'd3'], ['d1', 'd2', 'd3'], ['d1', 'd2', 'd3']], ['d1', 'd2', 'd3'], ['n1', 'n2', 'n3']),
		('many_to_many_less_descriptions', [['d1', 'd2'], ['d1', 'd2'], ['d1', 'd2']], ['d1', 'd2'], ['n1', 'n2', 'n3']),
		('many_to_many_less_nodes', [['d1', 'd2', 'd3'], ['d1', 'd2', 'd3'], ['d1', 'd2', 'd3']], ['d1', 'd2', 'd3'], ['n1', 'n2']),
	])
	def test_add_node_with_description(self, name: str, e_descriptions_per_node: list[list[str]], descriptions: list[str], nodes: list[str]):
		node_part_of_input = f'm {K.ADD} {K.MANY} {" ".join(nodes)}' if len(nodes) > 1 else f'm {K.ADD} {nodes[0]}'
		description_part_of_input = f'{K.DESCRIPTION_FLAG} {" ".join(descriptions)}'

		self.cli.parse(f'{node_part_of_input} {description_part_of_input}')

		for node, e_descriptions in zip(nodes, e_descriptions_per_node):
			try:
				a_node = NodesManager.get_node(node)
			except KeyError:
				self.fail('Some node has not been created')

			self.assertCountEqual(e_descriptions, a_node.descriptions)
