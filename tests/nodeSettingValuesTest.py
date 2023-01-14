from abstractTest import AbstractTest
from categorierCli import Keywords as K
from nodes import NodesManager


class NodeSettingValuesTest(AbstractTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Node Setting Values'

	def test_set_single_value(self):
		node_name = 'n'
		NodesManager.add_node(node_name)
		e_key = 'Author'
		e_value = 'Orwell'
		self.cli.parse(f'm {K.SET} {e_key} {e_value} {K.IN} {node_name}')

		node = NodesManager.get_node(node_name)
		self.assertIn(e_key, node.keys())
		self.assertEqual(e_key, node.get(e_key))

	def test_set_single_list(self):
		node_name = 'n'
		NodesManager.add_node(node_name)
		e_key = 'names'
		e_value = ['Muhhamad', 'ibn', 'Hatimi']
		self.cli.parse(f'm {K.SET} {e_key} [] {K.IN} {node_name}')
		self.cli.parse(f'm {K.ADD_FULL} {K.VALUES} {" ".join(e_value)} {K.TO} {node_name}')

		node = NodesManager.get_node(node_name)
		self.assertIn(e_key, node.keys())
		self.assertIn(e_key, node.get(e_key))

	def test_set_many_values(self):
		node_name = 'n'
		NodesManager.add_node(node_name)
		e_keys = 'Author', 'year', 'type'
		e_values = 'Orwell', 1934, 'Dystopia'

		input_string = 'm'
		for key, value in zip(e_keys, e_values):
			input_string += f' {K.SET} {key} {value}'
		input_string += f' {K.IN} {node_name}'

		self.cli.parse(input_string)

		node = NodesManager.get_node(node_name)
		self.assertCountEqual(e_keys, node.keys())
		for e_key, e_value in zip(e_keys, e_values):
			self.assertEqual(e_value, node[e_key])

	def test_set_many_lists(self):
		node_name = 'n'
		NodesManager.add_node(node_name)
		e_keys = 'names', 'sons'
		e_values = ['Muhhamad', 'ibn', 'Hatimi'], ['Ali', 'Arim']

		for e_key in e_keys:
			self.cli.parse(f'm {K.SET} {e_key} [] {K.IN} {node_name}')

		input_string = f'm'
		for e_key, e_key_values in zip(e_keys, e_values):
			input_string += f' {K.SET} {e_key} ' + ' '.join(e_key_values)
		input_string += f' {K.IN} {node_name}'
		self.cli.parse(input_string)

		node = NodesManager.get_node(node_name)
		self.assertCountEqual(e_keys, node.keys())
		for e_key, e_key_values in zip(e_keys, e_values):
			self.assertCountEqual(e_key_values, node[e_key])
