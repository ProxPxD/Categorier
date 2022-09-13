import pickle
from dataclasses import dataclass
from pathlib import Path

from ideasList import IdeasList


@dataclass
class Saved:
    IDEAS_LIST_PATH: Path = Path(__file__).parent / 'resources' / 'ideas.pickle'


def load_list():
    if not Saved.IDEAS_LIST_PATH.exists():
        save_default_list()

    with open(Saved.IDEAS_LIST_PATH, 'rb') as f:
        return pickle.load(f)


def save_list(ideasList):
    with open(Saved.IDEAS_LIST_PATH, 'wb') as f:
        pickle.dump(ideasList, f)


def get_default_list():
    return IdeasList()


def save_default_list():
    save_list(get_default_list())
