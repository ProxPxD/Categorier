import re
from dataclasses import dataclass
from itertools import chain, repeat
from re import Pattern
from typing import Iterable, Callable

from more_itertools import split_at, unique_everseen, chunked
from smartcli import Cli, Flag, VisibleNode, CliCollection

from exceptions import NodeExistsInDataBase
from nodes import NodesManager, MemberTypes, Node
from printer import Printer


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
	SHOW = 'show'

	FLAT_SHORT = '-f'
	FLAT_LONG = '--flat'
	ALL_FLAT_SHORT = '-af'
	ALL_FLAT_LONG = '--all-flat'
	WITH_PARENTS = '--with_parents'
	WITH_CHILDREN = '--with_children'
	MANY = 'many'
	AND = 'and'
	OR = 'or'
	JUST = 'just'
	ALL = 'all'

	NAME = 'name'
	NODE = 'node'
	NODES = 'nodes'
	VAL = 'val'
	VALUE = 'value'
	VALUES = 'values'
	KEY = 'key'
	KEYS = 'keys'
	ARGUMENTS = 'arguments'
	MEMO = 'memo'
	NONE = 'None'

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
		self._add_values_node: VisibleNode = None
		self._set_node: VisibleNode = None
		self._unset_node: VisibleNode = None
		self._argument_collection: CliCollection = None

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

		self._search_node: VisibleNode = None
		self._show_node: VisibleNode = None
		self._change_node: VisibleNode = None
		self._change_value_node: VisibleNode = None

		self._argument_collection = self.root.add_collection('argument_collection')
		self._create_general_flags()
		self._create_add_node()
		self._create_categorize_node()
		self._create_set_node()
		self._create_unset_node()
		self._create_delete_node()
		self._create_show_node()
		self._create_search_node()
		self._create_change_node()

	def set_out_stream(self, out):
		super().set_out_stream(out)
		Printer.out = out

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
		self._create_add_values_node()

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

			parents = list(parents)
			set_args = None
			if Keywords.SET in parents and parents and parents[-1] != Keywords.SET:
				set_index = parents.index(Keywords.SET)
				set_args = ['m'] + parents[set_index:] + [Keywords.TO, name]
				parents = parents[:set_index]

			node = NodesManager.add_node(name, parents=parents, children=children)
			descriptions = self._description_flag.get_as_list()
			node[MemberTypes.DESCRIPTIONS].extend(descriptions)

			if set_args:
				self.parse(set_args)

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

	def _create_add_values_node(self):
		self._add_values_node = self._add_node.add_node(Keywords.VALUES, Keywords.VALUE, Keywords.VAL)
		self._add_values_node.add_param(Keywords.ARGUMENTS, multi=True)
		self._add_values_node.add_action(self._add_values_action)

	def _add_values_action(self):
		node_names = self._prep_flag.get_as_list()
		arguments = self._add_values_node.get_param(Keywords.ARGUMENTS).get_as_list()
		key_value_pairs = list(split_at(arguments, lambda a: a == Keywords.AND, keep_separator=False))
		for node_name in node_names:
			node = NodesManager.get_node(node_name)
			for key, *values in key_value_pairs:
				try:
					node[key].extend(values)
				except KeyError:
					node[key] = values[:]

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

	def _create_set_node(self):
		self._set_node = self.root.add_node(Keywords.SET)
		self._set_node.add_param(Keywords.ARGUMENTS, multi=True)
		self._set_node.add_action(self._set_node_action)

	def _set_node_action(self):
		node_names = self._prep_flag.get_as_list()
		arguments = self._set_node.get_param(Keywords.ARGUMENTS).get_as_list()
		key_value_pairs = list(split_at(arguments, lambda a: a == Keywords.AND, keep_separator=False))
		for node_name in node_names:
			node = NodesManager.get_node(node_name)
			for key, *values in key_value_pairs:
				node[key] = values

	def _create_unset_node(self):
		self._unset_node = self.root.add_node(Keywords.UNSET)
		self._unset_node.add_param(Keywords.ARGUMENTS, storage=self._argument_collection)
		self._unset_node.add_action(self._unset_node_action)

	def _unset_node_action(self):
		node_names = self._prep_flag.get_as_list()
		arguments = self._argument_collection.get_as_list()
		key_value_pairs = list(split_at(arguments, lambda a: a == Keywords.AND, keep_separator=False))
		for node_name in node_names:
			node = NodesManager.get_node(node_name)
			for key, *to_unsets in key_value_pairs:
				if not to_unsets:
					del node[key]
				else:
					for i, to_unset in enumerate(to_unsets):
						if to_unset in node[key]:
							node[key].remove(to_unset)
						elif to_unset.isnumeric():
							to_unset = int(to_unset) - 1 - i
							del node[key][to_unset]

	def _create_delete_node(self):
		self._create_main_delete_node()
		self._create_delete_just_parent_node()
		self._create_delete_description_node()
		self._create_delete_values_node()

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
		to_delete_nodes = list(map(NodesManager.get_node, to_deletes))
		nodes = list(map(NodesManager.get_node, node_names))
		for node in nodes:
			between_node_names = list(self._get_between_nodes(node, to_delete_nodes))
			node.remove_parents(*between_node_names)
			exterior_nodes = list(self._extract_exterior_nodes(between_node_names))
			to_add = list(filter(lambda n: n not in node.parents.names , exterior_nodes))
			node.add_parents(*to_add)

	def _get_between_nodes(self, node: Node, to_deletes: list[Node]) -> set[str]:
		between_node_names = set(map(Node.get_name, to_deletes))
		ancestors = set(node.get_all_ancestors_names())
		for to_delete in to_deletes:
			between_node_names |= ancestors & set(to_delete.get_all_descendants_names())

		return between_node_names

	def _extract_exterior_nodes(self, between_node_names: Iterable[str]) -> Iterable[str]:
		between_node_names = list(between_node_names)
		nodes = list(map(NodesManager.get_node, between_node_names))
		extracted = (parent.name for node in nodes for parent in node.parents if parent.name not in between_node_names)
		return set(extracted)

	def _create_delete_values_node(self):
		self._delete_values_node = self._delete_node.add_node(Keywords.VALUES, Keywords.VALUE, Keywords.VAL)
		self._delete_values_node.add_param(Keywords.ARGUMENTS, storage=self._argument_collection)
		self._delete_values_node.add_action(self._unset_node_action)

	def _create_search_node(self):
		self._search_node = self.root.add_node(Keywords.SEARCH)
		self._search_node.add_param(Keywords.ARGUMENTS, multi=True, lower_limit=0)
		self._search_node.add_action(self._search_node_action)

	def _search_node_action(self):
		criteria = self._prep_flag.get_as_list()
		if not criteria:
			self._prep_flag.get_storage().append(Keywords.MEMO)
		found = self._search_by_criteria()
		Printer.print_short_node_info(found)

	def _search_by_criteria(self):
		K = Keywords
		arguments = self._search_node.get_param(Keywords.ARGUMENTS).get_as_list()
		criteria = self._prep_flag.get_as_list()
		func = all if K.AND in criteria else any if K.OR in criteria else None
		grouped_by_criteria = split_at(criteria, lambda w: w in (K.AND, K.OR), keep_separator=False)
		if arguments:
			grouped_by_criteria = zip(map(lambda g: g[0], grouped_by_criteria), arguments)
		criteria_pattern_pair = map(lambda p: (p[0], re.compile(p[1]) if p[1] != K.NONE else K.NONE), grouped_by_criteria)
		condition = self._get_search_condition(criteria_pattern_pair, func)
		found = filter(condition, map(NodesManager.get_node, NodesManager.get_all_names()))
		return found

	def _get_search_condition(self, criteria_pattern_pair: Iterable[tuple[str, Pattern]], func: Callable):
		criteria_pattern_pair_list = list(criteria_pattern_pair)
		if func is not None:
			return lambda node: func((self._verify_criterion(criterion, pattern, node) for criterion, pattern in criteria_pattern_pair_list))
		else:
			criterion, pattern = criteria_pattern_pair_list[0]
			return lambda node: self._verify_criterion(criterion, pattern, node)

	def _verify_criterion(self, criterion, pattern, node):
		try:
			return bool(pattern.search(node.get(criterion)))
		except KeyError:
			if criterion == Keywords.MEMO:
				return bool(pattern.search(node.name))
		except AttributeError:
			if pattern == Keywords.NONE:
				return criterion not in node
		return False

	def _create_change_node(self):
		self._create_main_change_node()
		self._change_node.add_node(self._create_generic_change_node(Keywords.NODE))
		self._create_rename_node()
		self._create_value_change_node()

	def _create_main_change_node(self):
		self._change_node = self.root.add_node(Keywords.CHANGE)
		self._change_node.set_params('old', 'new')
		self._change_node.add_action_when_is_active(self._change_key_name, self._prep_flag)
		self._change_node.add_action_when_is_inactive(self._change_node_name, self._prep_flag)

	def _create_generic_change_node(self, name) -> VisibleNode:
		node = VisibleNode(name)
		node.set_params('old', 'new')
		node.add_action_when_is_active(self._change_node_name, self._prep_flag)
		return node

	def _create_rename_node(self):
		rename_node = self.root.add_node(Keywords.RENAME)
		rename_node.set_params('old', 'new')
		old, new = rename_node.get_params('old', 'new')
		rename_node.add_action_when_is_active(lambda: self._change_key_name(old.get(), new.get()), self._prep_flag)
		rename_node.add_action_when_is_inactive(self._change_node_name, self._prep_flag)

	def _change_node_name(self, old=None, new=None):
		old = old or self._change_node.get_param('old').get()
		new = new or self._change_node.get_param('new').get()
		node = NodesManager.get_node(old)
		NodesManager.create_node_from_data(new, node.to_dict()[old])

	def _change_key_name(self, old=None, new=None):
		old = old or self._change_node.get_param('old').get()
		new = new or self._change_node.get_param('new').get()
		node_names = self._prep_flag.get_as_list()
		for node_name in node_names:
			node = NodesManager.get_node(node_name)
			node[new] = node[old]
			del node[old]

	def _create_value_change_node(self):
		self._change_value_node = self._change_node.add_node(Keywords.VALUES, Keywords.VALUE, Keywords.VAL)
		self._change_value_node.set_possible_param_order('key new')
		self._change_value_node.set_possible_param_order('key old new')
		self._change_value_node.get_param('old').set_default(None)
		self._change_value_node.add_action(self._change_node_value_action)

	def _change_node_value_action(self):
		key: str = self._change_value_node.get_param('key').get()
		old: str = self._change_value_node.get_param('old').get()
		new: str = self._change_value_node.get_param('new').get()
		node_names = self._prep_flag.get_as_list()
		for node_name in node_names:
			node = NodesManager.get_node(node_name)
			is_old_none = old is None
			is_list = isinstance(node[key], list)
			if is_old_none and not is_list:
				node[key] = new
			elif not is_old_none and is_list:
				elems: list = node[key]
				index = int(old)-1 if old.isnumeric() else elems.index(old)
				del elems[index]
				elems.insert(index, new)

	def _create_show_node(self):
		self._show_node = self.root.add_node(Keywords.SHOW)
		self._show_node.add_param(Keywords.NODE)
		self._show_node.get_param(Keywords.NODE).set_default(None)
		self._show_node.add_action(self._show_node_action)

	def _show_node_action(self):
		name = self._show_node.get_param(Keywords.NODE).get()
		if name is None or name == Keywords.ALL:
			nodes = NodesManager.get_all_nodes()
			Printer.print_short_node_info(nodes)
		else:
			node = NodesManager.get_node(name)
			Printer.print_detailed_node_info(node)
