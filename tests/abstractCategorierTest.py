from abc import ABC
from typing import Iterable

from abstractTest import AbstractTest


class AbstractCategorierTest(AbstractTest, ABC):

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
