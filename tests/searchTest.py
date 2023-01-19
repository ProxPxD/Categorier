from itertools import chain, repeat

from parameterized import parameterized
from smartcli.nodes.smartList import SmartList

from abstractTest import AbstractTest
from nodes import NodesManager
from categorierCli import Keywords as K


class SearchTest(AbstractTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Search'

	@parameterized.expand([
		('by_value_in_arguments', ['Poland', 'Portugal', 'Czechia'], 'Europe', f'{K.BY} continent'),
		('by_value_in_by', ['Poland', 'Portugal', 'Czechia'], '', f'{K.BY} continent Europe'),
		('by_values_in_arguments_and', ['Czechia'], 'Europe Cz', f'{K.BY} continent and memo'),
		('by_values_in_arguments_or', ['Czechia', 'Chile', 'Poland', 'Portugal',], 'Europe Ch', f'{K.BY} continent or memo'),
		('by_values_in_by_and', ['Poland', 'Portugal'], '', f'{K.BY} continent Europe and memo P'),
		('by_values_in_by_or', ['Poland', 'Czechia', 'Portugal', 'Peru'], '', f'{K.BY} continent Europe or memo P'),
		('by_value_not_set', ['Chile'], '', f'{K.BY} continent None'),
		('by_name_explicit', ['Czechia', 'Colombia', 'Chile'], 'C', ''),
		('by_name_implicit', ['Czechia', 'Colombia', 'Chile'], 'C', f'{K.BY} {K.MEMO}'),
	])
	def test_search(self, name: str, e_results: list[str], to_search: str, search_by: str):
		countries = 'Poland', 'Portugal', 'Czechia', 'Peru', 'Colombia', 'Chile'
		continent_key = 'continent'
		continents = list(chain(repeat('Europe', 3), repeat('America', 2)))  # Chile without a value set
		NodesManager.add_nodes(*countries)
		for country, continent in zip(countries, continents):
			NodesManager.get_node(country).put(continent_key, continent)

		lines = SmartList()
		self.cli.set_out_stream(lines.__iadd__)
		self.cli.parse(f'm {K.SEARCH} {to_search} {search_by}')
		# e_results = [f'{i+1}) {line}' for i, line in enumerate(e_results)]

		self.assertCountEqual(e_results, lines)

	#TODO: write a test for list values

