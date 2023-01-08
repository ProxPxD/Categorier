from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
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


class NodesStorage(ABC):

	def __init__(self, *names: str, further_type: str = None, **kwargs):
		super().__init__(**kwargs)
		self._names = list(names)
		self._further_type: str = further_type

	def get_names(self) -> Iterable[str]:
		return list(self._names)

	def add_names(self, *names: str):
		self._names.extend(names)

	def remove_names(self, *names: str):
		for name in names:
			self._names.remove(name)

	def get_all_member_names_flattened(self) -> Iterable[str]:
		yold = set()
		to_extend = self._names[:]
		while to_extend:
			name = to_extend.pop()
			if name not in yold:
				node = NodesManager.get_node(name)
				further = node.get_further(self._further_type).get_names()
				to_extend.extend(further)
				yield name

	def has_in_flattened_members(self, to_check: str):
		return to_check not in self.get_all_member_names_flattened()

	def get_final_members(self) -> Iterable[str]:
		to_extend = self._names[:]
		while to_extend:
			name = to_extend.pop()
			node = NodesManager.get_node(name)
			if not len(node.parents):
				yield name
			else:
				to_extend.extend(node.parents.get_names())

	def get(self, name: str) -> Node:
		if name in self._names:
			return NodesManager.get_node(name)
		raise KeyError

	def __getitem__(self, name: str) -> Node:
		return self.get(name)

	def __len__(self):
		return len(self._names)

	def __contains__(self, name):
		return name in self._names

	def __iter__(self):
		return iter(map(NodesManager.get_node, self._names))


class ParentNodesStorage(NodesStorage):
	def __init__(self, *parents: str, **kwargs):
		super().__init__(*parents, further_type=MemberTypes.PARENTS, **kwargs)


class ChildNodesStorage(NodesStorage):
	def __init__(self, *parents: str, **kwargs):
		super().__init__(*parents, further_type=MemberTypes.CHILDREN, **kwargs)


class Node:

	def __init__(self, name: str, **kwargs):
		super().__init__(**kwargs)
		self.name = name
		self.parents = ParentNodesStorage()
		self.children = ChildNodesStorage()
		self.fields = {}

	def __setattr__(self, name, value):
		match name:
			case MemberTypes.PARENTS | MemberTypes.CHILDREN:
				if isinstance(value, str):
					value = [value]
				if isinstance(value, list | tuple):
					collection: NodesStorage = self.__dict__[name]
					collection.add_names(*value)
			case MemberTypes.DESCRIPTIONS:
				if isinstance(value, str):
					value = [value]
				if isinstance(value, list | tuple):
					collection: list = self.__dict__[name]
					collection.extend(value)
			case _: self.__dict__[name] = value

	def to_dict(self) -> dict:
		return {self.name: {
			MemberTypes.PARENTS: self.parents.get_names(),
			MemberTypes.CHILDREN: self.children.get_names(),
			**self.fields
		}}

	def get_further(self, type: str) -> NodesStorage:
		match type:
			case MemberTypes.PARENTS: return self.parents
			case MemberTypes.CHILDREN: return self.children
			case _: raise ValueError

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

		further.add_names(to_put)
		put = further.get(to_put)
		puts_opposite = put.get_further(opposite_type)
		puts_opposite.add_names(self.name)

	def remove_parents(self, *parents):
		self._remove_member(*parents, further_type=MemberTypes.PARENTS)

	def remove_children(self, *children):
		self._remove_member(*children, further_type=MemberTypes.CHILDREN)

	def _remove_member(self, *to_remove, further_type: str):
		further = self.get_further(further_type)
		further.remove_names(*to_remove)

	def __hash__(self):
		return hash(self.name)

