from __future__ import annotations

import operator as op
from abc import ABC
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Iterable

import yaml


@dataclass(frozen=True)
class Paths:
	RESOURCES = Path(__file__).parent.parent / 'resources'
	DATABASE = RESOURCES / 'data.yml'


@dataclass(frozen=True)
class MemberTypes:
	PARENTS = 'parents'
	CHILDREN = 'children'
	DESCRIPTIONS = 'descriptions'

	@classmethod
	def get_opposite_type(cls, further_type: str) -> str:
		return MemberTypes.PARENTS if further_type == MemberTypes.CHILDREN else MemberTypes.CHILDREN


class DataManager:
	_data = {}
	_loaded_path = None

	@classmethod
	def save_data(cls):
		with open(cls._loaded_path, 'w') as data_file:
			yaml.safe_dump(data_file, data_file, default_flow_style=False)

	@classmethod
	def load_data(cls, path: str | Path = None):
		Paths.RESOURCES.mkdir(exist_ok=True)
		cls._loaded_path = path or Paths.DATABASE
		cls._loaded_path.touch(exist_ok=True)
		with open(cls._loaded_path, 'r+') as data_file:
			cls._data = yaml.safe_load(data_file) or {}


class NodesManager(DataManager):
	_taken_nodes = dict()

	@classmethod
	def get_node(cls, name: str) -> Node:
		try:
			return cls._taken_nodes[name]
		except KeyError:
			return cls._get_node_from_data(name)

	@classmethod
	def get_nodes(cls, *names: str) -> Iterable[Node]:
		return map(cls.get_node, names)

	@classmethod
	def _get_node_from_data(cls, name: str) -> Node:
		node_data = cls._data[name]
		node = cls.create_node_from_data(name, node_data)
		cls._taken_nodes[name] = node
		return node

	@classmethod
	def create_node_from_data(cls, name: str, data: dict) -> Node:
		node = Node(name)
		node.parents = data.get(MemberTypes.PARENTS, tuple())
		node.children = data.get(MemberTypes.CHILDREN, tuple())
		node.descriptions = data.get(MemberTypes.DESCRIPTIONS, tuple())
		return node

	@classmethod
	def add_node(cls, name: str, *, parents: Iterable[str] = None, children: Iterable[str] = None) -> Node:
		cls.create_node(name, parents=parents, children=children)
		return cls.get_node(name)

	@classmethod
	def create_node(cls, name: str, *, parents: Iterable[str] = None, children: Iterable[str] = None) -> None:
		if cls.is_in_data(name):
			raise ValueError
		node = Node(name)
		node.add_parents(*list(parents or []))
		node.add_children(*list(children or []))
		cls._taken_nodes[name] = node

	@classmethod
	def is_in_data(cls, name: str) -> bool:
		return name in cls._data

	@classmethod
	def get_data(cls) -> dict:
		return cls._data


#########
# Nodes #
#########


class IToDict:
	def to_dict(self):
		raise NotImplementedError


class IName:
	def __init__(self, name: str, **kwargs):
		super().__init__(**kwargs)
		self.name = name

	def get_name(self) -> str:
		return self.name


class Field(IName, IToDict):
	def __init__(self, name, **kwargs):
		super().__init__(name=name, **kwargs)

	def to_dict(self) -> dict:
		return {}


class CollectiveField(Field):
	def __init__(self, name, values=None, **kwargs):
		super().__init__(name=name, **kwargs)
		self._values = values or []

	def to_dict(self) -> dict:
		return {self.name: self._values} if self._values else {}

	def get_nth(self, n: int):
		return self._values[n]

	def add(self, *to_adds) -> None:
		self._values.extend(*to_adds)

	def remove(self, *to_removes):
		for to_remove in to_removes:
			self._values.remove(to_remove)

	def get_all(self) -> list:
		return self._values

	def __getitem__(self, index: int) -> Node:
		return self.get_nth(index)

	def __len__(self):
		return len(self._values)

	def __contains__(self, value):
		return self._values.__contains__(value)

	def __iter__(self):
		return iter(self._values)


class NodesStorageField(CollectiveField, ABC):

	def __init__(self, *names: str, name: str = None, **kwargs):
		super().__init__(name=name, values=names, **kwargs)

	def get_all_member_names_flattened(self) -> Iterable[str]:
		yold = set()
		to_extend = self._values[:]
		while to_extend:
			name = to_extend.pop()
			if name not in yold:
				node = NodesManager.get_node(name)
				further = node.get_further(self.name).get_all()
				to_extend.extend(further)
				yield name

	def get_names(self) -> Iterable[str]:
		return self._values

	def has_in_flattened_members(self, to_check: str):
		return to_check not in self.get_all_member_names_flattened()

	def get_final_members(self) -> Iterable[str]:
		to_extend = self._values[:]
		while to_extend:
			name = to_extend.pop()
			node = NodesManager.get_node(name)
			if not len(node.parents):
				yield name
			else:
				to_extend.extend(node.parents.get_all())

	def get_node(self, name: str) -> Node:
		if name in self._values:
			return NodesManager.get_node(name)
		raise KeyError

	def __getitem__(self, index: str | int) -> Node:
		if isinstance(index, int):
			index = super().__getitem__(index)
		if isinstance(index, str):
			return self.get_node(index)
		raise KeyError

	def __iter__(self):
		return iter(map(NodesManager.get_node, self.__iter__()))


class ParentNodesStorageField(NodesStorageField):
	def __init__(self, *parents: str, **kwargs):
		super().__init__(*parents, name=MemberTypes.PARENTS, **kwargs)


class ChildNodesStorageField(NodesStorageField):
	def __init__(self, *parents: str, **kwargs):
		super().__init__(*parents, name=MemberTypes.CHILDREN, **kwargs)


class DescriptionField(Field):
	def __init__(self, **kwargs):
		super().__init__(name=MemberTypes.DESCRIPTIONS, **kwargs)


class NodesStorageFieldPossessor(IName):

	def __init__(self, name, **kwargs):
		super().__init__(name, **kwargs)
		self.parents = ParentNodesStorageField()
		self.children = ChildNodesStorageField()

	# Nodes storages:

	def get_further(self, type: str) -> NodesStorageField:
		match type:
			case MemberTypes.PARENTS:
				return self.parents
			case MemberTypes.CHILDREN:
				return self.children
			case _:
				raise ValueError

	def get_all_ancestors_names(self) -> Iterable[str]:
		return self.parents.get_all_member_names_flattened()

	def get_all_descendants_names(self) -> Iterable[str]:
		return self.children.get_all_member_names_flattened()

	def get_final_ancestors(self) -> Iterable:
		return self.parents.get_final_members()

	def get_final_descendants(self) -> Iterable:
		return self.children.get_final_members()

	# modifying nodes

	def add_parents(self, *parents: str) -> None:
		for parent in parents:
			self._add_member(parent, MemberTypes.PARENTS)

	def add_children(self, *children: str) -> None:
		for child in children:
			self._add_member(child, MemberTypes.CHILDREN)

	def _add_member(self, to_put, further_type: str) -> None:
		further = self.get_further(further_type)
		if further.has_in_flattened_members(to_put):
			return None
		opposite_type = MemberTypes.PARENTS if further_type == MemberTypes.CHILDREN else MemberTypes.CHILDREN
		opposite = self.get_further(opposite_type)
		if opposite.has_in_flattened_members(to_put):
			raise ValueError

		further.add(to_put)
		put = further.get_node(to_put)
		puts_opposite = put.get_further(opposite_type)
		puts_opposite.add(self.name)

	def remove_parents(self, *parents):
		self._remove_member(*parents, further_type=MemberTypes.PARENTS)

	def remove_children(self, *children):
		self._remove_member(*children, further_type=MemberTypes.CHILDREN)

	def _remove_member(self, *to_removes, further_type: str):
		further = self.get_further(further_type)
		opposite_type = MemberTypes.get_opposite_type(further_type)
		nodes = map(further.get_node, to_removes)
		opposite_side = map(lambda n: n.get_further(opposite_type), nodes)
		for opposite_node_further in opposite_side:
			opposite_node_further.remove(self.name)

		further.remove(*to_removes)


class Node(IName, NodesStorageFieldPossessor):

	def __init__(self, name: str, **kwargs):
		super().__init__(name=name, **kwargs)
		self.description = DescriptionField()

	def __setattr__(self, name, value):
		match name:
			case MemberTypes.PARENTS | MemberTypes.CHILDREN | MemberTypes.DESCRIPTIONS:
				if isinstance(value, str):
					value = [value]
				if isinstance(value, list | tuple):
					collection: CollectiveField = self.__dict__[name]
					collection.add(*value)
				raise ValueError
			case _:
				self.__dict__[name] = value

	def to_dict(self) -> dict:
		fields = (self.parents, self.children, self.description)
		as_dicts = map(CollectiveField.to_dict, fields)
		joined_dict = reduce(op.or_, as_dicts)
		return joined_dict

	def __hash__(self):
		return hash(self.name)
