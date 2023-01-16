from dataclasses import dataclass
from itertools import chain

from smartcli import Cli, Flag

from exceptions import NodeExistsInDataBase
from nodes import NodesManager


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
		self._add_node = None
		self._with_parents = None
		self._with_children = None
		self._add_name_param = None
		self._add_parents_param = None
		self._prep_flag: Flag = None

		self._create_general_flags()
		self._create_add_node()
		self._create_categorize_node()

	def _create_general_flags(self):
		K = Keywords
		self._prep_flag = self.root.add_flag(K.TO, K.FROM, K.IN, K.OF, K.BY, K.AS)
		self._prep_flag.set_to_multi_at_least_one()

	def _create_add_node(self):
		self._add_node = self.root.add_node(Keywords.ADD)

		self._with_parents = self._add_node.add_flag(Keywords.WITH_PARENTS, flag_limit=None)
		self._with_children = self._add_node.add_flag(Keywords.WITH_CHILDREN, flag_limit=None)

		self._add_node.set_params(CliElements.NAME, CliElements.PARENTS)
		self._add_name_param = self._add_node.get_param(CliElements.NAME)
		self._add_parents_param = self._add_node.get_param(CliElements.PARENTS)
		self._add_parents_param.set_to_multi_at_least_zero()
		self._add_node.add_action(self._add_node_action)

	def _add_node_action(self):
		try:
			node = NodesManager.add_node(self._add_name_param.get(),
								  		 parents=chain(self._add_parents_param.get_as_list(), self._with_parents.get_as_list()),
								  		 children=self._with_children.get_as_list())
			# TODO: msg
		except NodeExistsInDataBase:
			pass  # TODO: msg

	def _create_categorize_node(self):
		self._cat_node = self.root.add_node(Keywords.CATEGORIZE, Keywords.CAT)
		self._cat_node.add_param(Keywords.NODES, multi=True)
		self._cat_node.add_action(self._add_category_action)

	def _add_category_action(self):
		cat_names = self._prep_flag.get_as_list()
		node_names = self._cat_node.get_param(Keywords.NODES).get_as_list()
		if not cat_names:
			node_names, cat_names = node_names[:1], node_names[1:]
		for node_name in node_names:
			node = NodesManager.get_node(node_name)
			node.add_parents(*cat_names)

