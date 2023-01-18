from parameterized import parameterized

from abstractCategorierTest import AbstractCategorierTest
from categorierCli import Keywords as K
from nodes import NodesManager


class NodeValuesTest(AbstractCategorierTest):
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
		self.assertEqual(e_value, node.get(e_key))

	def test_set_single_list(self):
		node_name = 'n'
		NodesManager.add_node(node_name)
		e_key = 'names'
		e_values = ['Muhamad', 'ibn', 'Hatimi']
		self.cli.parse(f'm {K.SET} {e_key} [] {K.IN} {node_name}')
		self.cli.parse(f'm {K.ADD} {K.VALUES} {e_key} {" ".join(e_values)} {K.TO} {node_name}')

		node = NodesManager.get_node(node_name)
		self.assertIn(e_key, node.keys())
		self.assertCountEqual(e_values, node.get(e_key))

	def test_set_many_values(self):
		node_name = 'n'
		NodesManager.add_node(node_name)
		e_keys = 'Author', 'year', 'type'
		e_values = 'Orwell', '1934', 'Dystopia'

		input_string = 'm'
		for key, value in zip(e_keys, e_values):
			input_string += f' {K.AND} {key} {value}'
		input_string += f' {K.IN} {node_name}'
		input_string = input_string.replace(K.AND, K.SET, 1)

		self.cli.parse(input_string)

		node = NodesManager.get_node(node_name)
		self.assertCountEqual(e_keys, node.keys())
		for e_key, e_value in zip(e_keys, e_values):
			self.assertEqual(e_value, node[e_key])

	def test_set_many_lists(self):
		node_name = 'n'
		NodesManager.add_node(node_name)
		e_keys = 'names', 'sons'
		e_values = ['Muhamad', 'ibn', 'Hatimi'], ['Ali', 'Arim']

		for e_key in e_keys:
			self.cli.parse(f'm {K.SET} {e_key} [] {K.IN} {node_name}')

		input_string = f'm {K.SET}'
		input_string += f' {K.AND} '.join((f' {e_key} ' + ' '.join(e_key_values) for e_key, e_key_values in zip(e_keys, e_values)))
		input_string += f' {K.IN} {node_name}'
		self.cli.parse(input_string)

		node = NodesManager.get_node(node_name)
		self.assertCountEqual(e_keys, node.keys())
		for e_key, e_key_values in zip(e_keys, e_values):
			self.assertCountEqual(e_key_values, node[e_key])

	def test_add_node_with_setting(self):
		node_name = 'n'
		e_key = 'Author'
		e_val = 'Orwell'
		self.cli.parse(f'm {K.ADD} {node_name} {K.SET} {e_key} {e_val}')

		node = NodesManager.get_node(node_name)
		self.assertIn(e_key, node.keys())
		self.assertEqual(e_val, node.get(e_key))

	def test_add_node_with_setting_many(self):
		node_name = 'n'
		e_keys = 'Author', 'Year'
		e_vals = 'Orwell', '1935'
		self.cli.parse(f'm {K.ADD} {node_name} {K.SET} {e_keys[0]} {e_vals[0]} {K.AND} {e_keys[1]} {e_vals[1]}')

		node = NodesManager.get_node(node_name)
		for e_key, e_val in zip(e_keys, e_vals):
			self.assertIn(e_key, node.keys())
			self.assertEqual(e_val, node.get(e_key))

	def test_add_node_with_setting_and_grandparents(self):
		node_name = 'n'
		grand_parent = 'g'
		e_key = 'Author'
		e_val = 'Orwell'
		self.cli.parse(f'm {K.ADD} {grand_parent}')
		self.cli.parse(f'm {K.ADD} {node_name} {grand_parent} {K.SET} {e_key} {e_val}')

		node = NodesManager.get_node(node_name)
		self.assertIn(grand_parent, node.parents.get_names())
		self.assertIn(e_key, node.keys())
		self.assertEqual(e_val, node.get(e_key))

	def test_unset_value(self):
		node_name = 'n'
		key = 'Author'
		val = 'Orwell'
		node = NodesManager.add_node(node_name)
		node[key] = val

		self.cli.parse(f'm {K.UNSET} {key} {K.FROM} {node_name}')

		node = NodesManager.get_node(node_name)
		self.assertNotIn(key, node.keys())

	def test_unset_many_values(self):
		node_name = 'n'
		keys = 'Author', 'Year'
		vals = 'Orwell', '1935'
		node = NodesManager.add_node(node_name)
		for key, val in zip(keys, vals):
			node[key] = val

		self.cli.parse(f'm {K.UNSET} {keys[0]} {K.AND} {keys[1]} {K.FROM} {node_name}')

		node = NodesManager.get_node(node_name)
		for key in keys:
			self.assertNotIn(key, node.keys())

	@parameterized.expand([
		('unset', ['Muhhamad', 'Hatimi'], ['ibn'], K.UNSET),
		('delete_value', ['Muhhamad', 'Hatimi'], ['ibn'], f'{K.DEL} {K.VALUE}'),
		('two_values', ['Muhhamad'], ['ibn', 'Hatimi'], f'{K.DELETE} {K.VALUES}'),
		('unset_by_number', ['Muhhamad', 'Hatimi'], [2], K.UNSET),
		('delete_value_by_number', ['Muhhamad', 'Hatimi'], [2], f'{K.DEL} {K.VALUE}'),
		('two_values_by_number', ['Muhhamad'], [2, 3], f'{K.DELETE} {K.VALUES}'),
	])
	def test_unset_concrete_value(self, name: str, e_values: list[str], to_unsets: list[str], unset_way: str):
		node_name = 'n'
		e_key = 'names'
		values = ['Muhhamad', 'ibn', 'Hatimi']
		node = NodesManager.add_node(node_name)
		node[e_key] = values

		self.cli.parse(f'm {unset_way} {e_key} {" ".join(to_unsets)} {K.FROM} {node_name}')

		node = NodesManager.get_node(node_name)
		self.assertIn(e_key, node.keys())
		self.assertCountEqual(e_values, node[e_key])
