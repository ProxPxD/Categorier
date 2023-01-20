from typing import Iterable

from nodes import Node


class Formatter:

	@classmethod
	def format_short_node_info(cls, node: Node):
		line = f'{node.name}'
		return line

	@classmethod
	def format_detailed_node_info(cls, node: Node):
		info = ''
		info += f'Name: {node.name}\n'
		info += f'Parents:  {", ".join(node.parents.names)}\n'
		info += f'Children: {", ".join(node.children.names)}\n'
		info += f'Ancestors:   {", ".join(node.get_all_ancestors_names())}\n'
		info += f'Descendants: {", ".join(node.get_all_descendants_names())}\n'
		level = 0
		base_space = '    '
		for key, val in node.items():
			info += f'{base_space * level}{key}: '
			if isinstance(val, Iterable) and not isinstance(val, str):
				info += '\n'
				for i, iter_val in enumerate(val):
					info += f'{base_space * (level +1)}{i}) {iter_val}\n'
			else:
				info += val + '\n'

		return info


class Printer:

	out = print

	@classmethod
	def print(cls, to_print, **kwargs):
		cls.out(to_print, **kwargs)

	@classmethod
	def print_short_node_info(cls, nodes: Iterable[Node]):
		infos = map(Formatter.format_short_node_info, nodes)
		numerated = (f'{i+1}) {info}' for i, info in enumerate(infos))
		for line in numerated:
			cls.out(line)

	@classmethod
	def print_detailed_node_info(cls, node: Node):
		info = Formatter.format_detailed_node_info(node)
		cls.out(info + '\n')
