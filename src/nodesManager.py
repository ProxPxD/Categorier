from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Paths:
	RESOURCES = Path(__file__).parent.parent / 'resources'
	DATABASE = RESOURCES / 'data.yml'


class DataLoader:
	def __init__(self, data_path: Path | str = Paths.DATABASE, load=False):
		self._data_path = data_path
		self._data = {}
		if load:
			self.load_data()

	def save_data(self):
		with open(self._data_path, 'w') as data_file:
			yaml.safe_dump(data_file, data_file, default_flow_style=False)

	def load_data(self):
		with open(self._data_path, 'r+') as data_file:
			self._data = yaml.safe_load(data_file) or {}


class NodesManager(DataLoader):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)