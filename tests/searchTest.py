from itertools import chain, repeat

from parameterized import parameterized
from smartcli.nodes.smartList import SmartList

from abstractCategorierTest import AbstractCategorierTest
from categorierCli import Keywords as K
from nodes import NodesManager


class SearchTest(AbstractCategorierTest):
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
		for i, line in enumerate(lines):
			prefix, name = line.split(' ')
			self.assertIn(name, e_results)
			self.assertIn(str(i+1), prefix)


	#TODO: write a test for list values

	@parameterized.expand([
		('all_default', '', ['Poland', 'Portugal', 'Czechia', 'Peru', 'Colombia', 'Chile']),
		('all_with_argument', 'all', ['Poland', 'Portugal', 'Czechia', 'Peru', 'Colombia', 'Chile']),
		('concrete', 'Poland', ['Poland']),
	])
	def test_show(self, name: str, to_show: str, e_values: list):
		countries = 'Poland', 'Portugal', 'Czechia', 'Peru', 'Colombia', 'Chile'
		continent_key = 'continent'
		continents = list(chain(repeat('Europe', 3), repeat('America', 2)))  # Chile without a value set
		NodesManager.add_nodes(*countries)
		for country, continent in zip(countries, continents):
			NodesManager.get_node(country).put(continent_key, continent)

		lines = SmartList()
		self.cli.set_out_stream(lines.__iadd__)
		self.cli.parse(f'm {K.SHOW} {to_show}')
		result = '\n'.join(lines)
		for country in countries:
			if country in e_values:
				self.assertIn(country, result)
			else:
				self.assertNotIn(country, result)
