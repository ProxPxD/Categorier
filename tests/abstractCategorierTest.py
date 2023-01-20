from abc import ABC
from typing import Iterable

from abstractTest import AbstractTest
from categorierCli import CategorierCli
from nodes import NodesManager, Paths


class AbstractCategorierTest(AbstractTest, ABC):

	test_path = Paths.RESOURCES / 'test_data.yml'
	cli = CategorierCli()

	def setUp(self) -> None:
		super().setUp()
		NodesManager.load_data(self.test_path)

	def flatten_string_lists(self, *to_flattens, unique=False):
		flat = []
		for member in to_flattens:
			if isinstance(member, str):
				flat.append(member)
			elif isinstance(member, Iterable):
				flat.extend(self.flatten_string_lists(*member))

		if unique:
			flat = list(set(flat))
		return flat
