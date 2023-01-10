from dataclasses import dataclass

from smartcli import Cli


@dataclass
class Keywords:
	ADD_FULL = 'add'
	DELETE_FULL = 'delete'
	DELETE_SHORT = 'del'
	FLAT_SHORT = '-f'
	FLAT_LONG = '--flat'

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
