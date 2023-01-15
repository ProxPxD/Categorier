from dataclasses import dataclass

from smartcli import Cli


@dataclass
class Keywords:
	ADD = 'add'
	DELETE = 'delete'
	DEL = 'del'
	SET = 'set'
	UNSET = 'unset'

	FLAT_SHORT = '-f'
	FLAT_LONG = '--flat'
	ALL_FLAT_SHORT = '-af'
	ALL_FLAT_LONG = '--all-flat'
	MANY = 'many'
	AND = 'and'
	JUST = 'just'

	NODE = 'node'
	NODES = 'nodes'
	VALUE = 'value'
	VALUES = 'values'

	TO = 'to'
	FROM = 'from'
	IN = 'in'

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


class CategorierCli(Cli):
	pass
