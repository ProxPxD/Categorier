from dataclasses import dataclass
from itertools import chain, repeat
from typing import Iterable, Callable

from more_itertools import split_at, unique_everseen
from smartcli import Cli, Flag, VisibleNode

from exceptions import NodeExistsInDataBase
from nodes import NodesManager, MemberTypes, Node


@dataclass
class Keywords:
	ADD = 'add'
	CATEGORIZE = 'categorize'
	CAT = 'cat'
	DELETE = 'delete'
	DEL = 'del'
	SET = 'set'
	UNSET = 'unset'
	CHANGE = 'change'
	RENAME = 'rename'
	SEARCH = 'search'

	FLAT_SHORT = '-f'
	FLAT_LONG = '--flat'
	ALL_FLAT_SHORT = '-af'
	ALL_FLAT_LONG = '--all-flat'
	WITH_PARENTS = '--with_parents'
	WITH_CHILDREN = '--with_children'
	MANY = 'many'
	AND = 'and'
	JUST = 'just'

	NAME = 'name'
	NODE = 'node'
	NODES = 'nodes'
	VALUE = 'value'
	VALUES = 'values'

	TO = 'to'
	FROM = 'from'
	IN = 'in'
	OF = 'of'
	BY = 'by'
	AS = 'as'

	DESCRIPTIONS = 'descriptions'
	DESCRIPTION = 'description'
	DESCR = 'descr'
	DESCRIPTION_FLAG = '-d'


# Redesign
# add (descr)* <NAME> (--flat/-f) (CAT...) (to <NAME>)* (-d DESCR)

# Examples:
	# "add idea idea_name" == "add idea_name to idea" == "add to idea idea_name
	# add (idea|cat|descr)* <NAME> (CAT...) ({to <idea|cat>})* ({-d < DESCR >})
	# del (idea|cat|descr)* < NAME | NUM > ({from <idea|cat>}) *
	# show (idea|cat)* (NAME | NUM)({from <idea|cat>}) ({from < idea | cat >}) *
	# search (idea|cat)* < cat... > ({ in < idea | cat >}) * ({by < cat| descr | name >})
	# rename (idea|cat)* < NAME > < NEW_NAME > ({ in < idea | cat >}) *

@dataclass(frozen=True)
class CliElements:
	PARENTS = 'parents'
	NAME = 'name'


class CategorierCli(Cli):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		NodesManager.load_data()
		self._add_node: VisibleNode = None
		self._add_many_node: VisibleNode = None
		self._add_description_node: VisibleNode = None

		self._with_parents = None
		self._with_children = None
		self._add_parents_param = None
		self._prep_flag: Flag = None
		self._description_flag: Flag = None
		self._flat_flag: Flag = None
		self._all_flat_flag: Flag = None

		self._delete_node: VisibleNode = None
		self._delete_description_node: VisibleNode = None
		self._delete_just_ancestor_node: VisibleNode = None

		self._create_general_flags()
		self._create_add_node()
		self._create_categorize_node()
		self._create_delete_node()

	def _create_general_flags(self):
		K = Keywords
		self._prep_flag = self.root.add_flag(K.TO, K.FROM, K.IN, K.OF, K.BY, K.AS)
		self._prep_flag.set_to_multi_at_least_one()
		self._description_flag = self.root.add_flag(K.DESCRIPTION_FLAG, multi=True)
		self._flat_flag = self.root.add_flag(K.FLAT_LONG, K.FLAT_SHORT, flag_limit=0)
		self._all_flat_flag = self.root.add_flag(K.ALL_FLAT_LONG, K.FLAT_SHORT, flag_limit=0)

	def _create_add_node(self):
		self._with_parents = self.root.add_flag(Keywords.WITH_PARENTS, flag_limit=None)
		self._with_children = self.root.add_flag(Keywords.WITH_CHILDREN, flag_limit=None)
		self._create_main_add_node()
		self._create_add_many_node()
		self._create_add_description_node()

	def _create_main_add_node(self):
		self._add_node = self.root.add_node(Keywords.ADD)

		self._add_node.set_params(CliElements.NAME, CliElements.PARENTS)
		self._add_name_param = self._add_node.get_param(CliElements.NAME)
		self._add_parents_param = self._add_node.get_param(CliElements.PARENTS)
		self._add_parents_param.set_to_multi_at_least_zero()
		self._add_node.add_action(self._add_node_action)

	def _add_node_action(self):
		try:
			name = self._add_node.get_param(CliElements.NAME).get()
			children = self._with_children.get_as_list()
			parents = chain(self._add_parents_param.get_as_list(), self._with_parents.get_as_list())

			if self._is_any_flat_active():
				parents = self._get_desire_flat_parents(parents)

			node = NodesManager.add_node(name, parents=parents, children=children)
			descriptions = self._description_flag.get_as_list()
			node[MemberTypes.DESCRIPTIONS].extend(descriptions)
			# TODO: msg
		except NodeExistsInDataBase:
			pass  # TODO: msg

	def _add_node_flat_action(self):
		try:
			name = self._add_node.get_param(CliElements.NAME).get()
			children = self._with_children.get_as_list()
			argument_parents = chain(self._add_parents_param.get_as_list(), self._with_parents.get_as_list())
			end_parents = [p for parents in map(Node.get_all_ancestors_names, argument_parents) for p in parents]
			unique_parents = unique_everseen(end_parents)

			node = NodesManager.add_node(name, parents=list(unique_parents), children=children)
			descriptions = self._description_flag.get_as_list()
			node[MemberTypes.DESCRIPTIONS].extend(descriptions)
		except NodeExistsInDataBase:
			pass  # TODO: msg

	def _create_add_many_node(self):
		self._add_many_node = self._add_node.add_node(Keywords.MANY)
		self._add_many_node.add_param(Keywords.NODES, multi=True)
		self._add_many_node.add_action(self._add_many_nodes_action)

	def _add_many_nodes_action(self):
		try:
			node_names = self._add_many_node.get_param(Keywords.NODES).get_as_list()
			parents = self._with_parents.get_as_list() + self._prep_flag.get_as_list()
			children = self._with_children.get_as_list()
			descriptions = self._description_flag.get_as_list()
			n = len(node_names)
			all_parents = self._split_by_conjunction_or_repeat(parents, n=n)
			all_children = self._split_by_conjunction_or_repeat(children, n=n)
			all_descriptions = self._split_by_conjunction_or_repeat(descriptions, n=n)

			NodesManager.add_nodes(*node_names, all_parents=all_parents, all_children=all_children, all_descriptions=all_descriptions)
		except NodeExistsInDataBase:
			pass  # TODO: msg

	def _split_by_conjunction_or_repeat(self, collection: list, conjunction=Keywords.AND, n=None):
		if conjunction not in collection:
			return repeat(collection, n)
		return split_at(collection, lambda x: x == conjunction, keep_separator=False)

	def _create_add_description_node(self):
		self._add_description_node = self._add_node.add_node(Keywords.DESCRIPTION, Keywords.DESCR, Keywords.DESCRIPTIONS)
		self._add_description_node.add_param(Keywords.DESCRIPTIONS, multi=True)
		self._add_description_node.add_action(self._add_description_action)

	def _add_description_action(self):
		descriptions = self._add_description_node.get_param(Keywords.DESCRIPTIONS).get_as_list()
		node_names = self._prep_flag.get_as_list()
		for node_name in node_names:
			node = NodesManager.get_node(node_name)
			node.descriptions.extend(descriptions)

	def _create_categorize_node(self):
		self._cat_node = self.root.add_node(Keywords.CATEGORIZE, Keywords.CAT)
		self._cat_node.add_param(Keywords.NODES, multi=True)
		self._cat_node.add_action(self._add_category_action)

	def _add_category_action(self):
		cat_names = self._prep_flag.get_as_list()
		node_names = self._cat_node.get_param(Keywords.NODES).get_as_list()

		if not cat_names:
			node_names, cat_names = node_names[:1], node_names[1:]

		if self._is_any_flat_active():
			cat_names = self._get_desire_flat_parents(cat_names)

		for node_name in node_names:
			node = NodesManager.get_node(node_name)
			node.add_parents(*cat_names)

	def _is_any_flat_active(self) -> bool:
		return any(map(Flag.is_active, (self._flat_flag, self._all_flat_flag)))

	def _get_desire_flat_parents(self, parents: Iterable[str]) -> Iterable[str]:
		parents = list(parents)
		if self._flat_flag.is_active():
			desired = self._get_ancestors_using(parents, Node.get_final_ancestors)
		if self._all_flat_flag.is_active():
			further_ancestors = self._get_ancestors_using(parents, Node.get_all_ancestors_names)
			desired = chain(parents, further_ancestors)

		unique = unique_everseen(desired)
		return unique

	def _get_ancestors_using(self, parents: Iterable[str], ancestor_getter: Callable):
		nodes = map(NodesManager.get_node, parents)
		all_final = map(ancestor_getter, nodes)
		flat_final = (a for ancestors in all_final for a in ancestors)
		return flat_final

	def _create_delete_node(self):
		self._create_main_delete_node()
		self._create_delete_just_parent_node()
		self._create_delete_description_node()

	def _create_main_delete_node(self):
		self._delete_node = self.root.add_node(Keywords.DELETE, Keywords.DEL)
		self._delete_node.add_param(Keywords.NODES, multi=True)
		self._delete_node.add_action(self._delete_action)

	def _delete_action(self):
		to_deletes = self._delete_node.get_param(Keywords.NODES).get_as_list()
		for to_delete in to_deletes:
			NodesManager.delete_node(to_delete)

	def _create_delete_description_node(self):
		self._delete_description_node = self._delete_node.add_node(Keywords.DESCRIPTION, Keywords.DESCRIPTIONS, Keywords.DESCR)
		self._delete_description_node.add_param(Keywords.DESCRIPTIONS, multi=True)
		self._delete_description_node.add_action(self._delete_description_action)

	def _delete_description_action(self):
		node_names = self._prep_flag.get_as_list()
		to_deletes = self._delete_description_node.get_param(Keywords.DESCRIPTIONS).get_as_list()
		to_deletes = [n-1 for n in sorted(map(int, to_deletes))]
		for node_name in node_names:
			node = NodesManager.get_node(node_name)
			for i, to_delete in enumerate(to_deletes):
				del node.descriptions[to_delete - i]

	def _create_delete_just_parent_node(self):
		self._delete_just_ancestor_node = self._delete_node.add_node(Keywords.JUST)
		self._delete_just_ancestor_node.add_param(Keywords.NODES, multi=True)
		self._delete_just_ancestor_node.add_action(self._delete_just_ancestor_node_action)

	def _delete_just_ancestor_node_action(self):
		to_deletes = self._delete_just_ancestor_node.get_param(Keywords.NODES).get_as_list()
		node_names = self._prep_flag.get_as_list()

		for node_name in node_names:
			node = NodesManager.get_node(node_name)
			for to_delete in to_deletes:
				self._delete_just_ancestor_helper(node, to_delete)

	def _delete_just_ancestor_helper(self, node: Node, to_delete):
		raise NotImplementedError
