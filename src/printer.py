from typing import Iterable

from nodes import Node


class Formatter:

	@classmethod
	def format_short_node_info(self, node: Node):
		line = f'{node.name}'
		return line


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
