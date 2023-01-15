from parameterized import parameterized

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
		self.cli.parse(f'm {K.ADD} {K.VALUES} {" ".join(e_value)} {K.TO} {node_name}')

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

		input_string = f'm {K.SET}'
		input_string += f' {K.AND} '.join((f'{e_key}' + ' '.join(e_key_values) for e_key, e_key_values in zip(e_keys, e_values)))
		input_string += f' {K.IN} {node_name}'
		self.cli.parse(input_string)

		node = NodesManager.get_node(node_name)
		self.assertCountEqual(e_keys, node.keys())
		for e_key, e_key_values in zip(e_keys, e_values):
			self.assertCountEqual(e_key_values, node[e_key])

	def test_add_node_with_setting(self):
		node_name = 'n'
		e_key = 'Author'
		e_value = 'Orwell'
		self.cli.parse(f'm {K.ADD} {node_name} {K.SET} {e_key} {e_value}')

		node = NodesManager.get_node(node_name)
		self.assertIn(e_key, node.keys())
		self.assertEqual(e_key, node.get(e_key))

	def test_add_node_with_setting_many(self):
		node_name = 'n'
		e_keys = 'Author', 'Year'
		e_vals = 'Orwell', 1935
		self.cli.parse(f'm {K.ADD} {node_name} {K.SET} {e_keys[0]} {e_vals[0]} {K.AND} {e_keys[1]} {e_vals[1]}')

		node = NodesManager.get_node(node_name)
		self.assertCountEqual(e_keys, node.keys())
		for e_key, e_val in zip(e_keys, e_vals):
			self.assertEqual(e_val, node.get(e_key))