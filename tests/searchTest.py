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
		('by_value_in_search_string', ['Poland', 'Portugal', 'Czechia'], 'Europe', f'{K.BY} continent'),
		('by_value_in_by', ['Poland', 'Portugal', 'Czechia'], '', f'{K.BY} continent Europe'),
		('by_value_not_set', ['Chile'], '', f'{K.BY} continent None'),
		('by_name_explicit', ['Czechia', 'Colombia', 'Chile'], 'C', f'{K.BY} name'),
		('by_name_implicit', ['Czechia', 'Colombia', 'Chile'], 'C', ''),
	])
	def test_search(self, name: str, e_results: list[str], to_search: str, search_by: str):
		countries = 'Poland', 'Portugal', 'Czechia', 'Peru', 'Colombia', 'Chile'
		continent_key = 'continent'
		continents = list(chain(repeat('Europe', 3), repeat('America', 2)))  # Chile without a value set
		NodesManager.add_nodes(*countries)
		for country, continent in zip(countries, continents):
			self.cli.parse(f'm {K.ADD} {country} {K.SET} {continent_key} {continent}')

		lines = SmartList()
		self.cli.set_out_stream(lines.__iadd__)
		self.cli.parse(f'm {K.SEARCH} {to_search} {search_by}')
		e_results = [f'{i+1}) {line}' for i, line in enumerate(e_results)]

		self.assertCountEqual(e_results, lines)

