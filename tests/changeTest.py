from parameterized import parameterized

from abstractTest import AbstractTest
from categorierCli import Keywords as K
from nodes import NodesManager


class ChangeTest(AbstractTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Change'

	@parameterized.expand([
		('just_change', K.CHANGE),
		('change_node', f'{K.CHANGE} {K.NODE}'),
		('rename', f'{K.RENAME}'),
	])
	def test_change_node(self, node_name: str, change_command: str):
		NodesManager.add_node(node_name)
		new_name = 'new_name'

		self.cli.parse(f'm {change_command} {node_name} {new_name}')

	@parameterized.expand([
		('just_change', 'firstname', 'name', 'Pavel',  K.CHANGE),
		('rename', 'firstname', 'name', 'Pavel', f'{K.RENAME}'),
	])
	def test_change_setting_name(self, node_name: str, new_setting_name: str, setting_name: str, setting_value: str, change_command: str):
		node = NodesManager.add_node(node_name)
		node[setting_name] = setting_value

		self.cli.parse(f'm {change_command} {setting_name} {new_setting_name} {K.OF} {node_name}')

		try:
			node = NodesManager.get_node(node_name)
		except Exception:
			self.fail('node name changed')

		self.assertIn(new_setting_name, node.keys())
		self.assertEqual(setting_value, node.get(new_setting_name))

	@parameterized.expand([
		('change_value', 'name', 'default_name', 'Pavel', f'{K.CHANGE} {K.VALUE}'),
	])
	def test_change_value(self, node_name: str, setting_name: str, setting_value: str, new_setting_value: str, change_command: str):
		node = NodesManager.add_node(node_name)
		node[setting_name] = setting_value

		self.cli.parse(f'm {change_command} {setting_name} {new_setting_value} {K.OF} {node_name}')

		try:
			node = NodesManager.get_node(node_name)
		except Exception:
			self.fail('node name changed')

		self.assertIn(setting_name, node.keys(), 'setting value changed')
		self.assertEqual(new_setting_value, node.get(setting_name), 'value not changed')

	@parameterized.expand([
		('change_by_value', ['Muhhamad', 'in', 'Hatimi'], 'in', 'ibn', f'{K.CHANGE} {K.VALUE}'),
		('change_by_number', ['Muhhamad', 'in', 'Hatimi'], 'in', 2, f'{K.CHANGE} {K.VALUE}'),
	])
	def test_change_concrete_value(self, name: str, e_values: list[str], new_value: str, old_value: str, change_way: str):
		node_name = 'n'
		key = 'names'
		values = ['Muhhamad', 'ibn', 'Hatimi']
		node = NodesManager.add_node(node_name)
		node[key] = values

		self.cli.parse(f'm {change_way} {key} {old_value} {new_value} {K.FROM} {node_name}')

		node = NodesManager.get_node(node_name)
		self.assertIn(key, node.keys())
		self.assertIn(e_values, node[key])