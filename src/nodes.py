from typing import Iterable


class ParentPossessor:

	def __init__(self, *parents: str, **kwargs):
		super().__init__(**kwargs)
		self.parents: list[str] = list(parents)


class ChildPossessor:

	def __init__(self, *children: str, **kwargs):
		super().__init__(**kwargs)
		self.children: list[str] = list(children)


class Node(ParentPossessor, ChildPossessor):

	def __init__(self, parents: Iterable, children: Iterable, **kwargs):
		super().__init__(parents=list(parents), children=list(children), **kwargs)
