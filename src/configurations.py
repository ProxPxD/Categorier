import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ideasList import IdeasList


@dataclass
class Saved:
    RESOURCES = Path(__file__).parent / 'resources'
    IDEAS_LIST_PATH = RESOURCES / 'ideas.pickle'
    CATEGORIES_LIST_PATH = RESOURCES / 'categories.pickle'


def load_list(path: Path):
    if not path.exists():
       save_default_list(path)

    with open(path, 'rb') as f:
        return pickle.load(f)


def save_list(list_to_save: Any, path: Path):
    with open(path, 'wb') as f:
        pickle.dump(list_to_save, f)


def get_default_list(path: Path):
    if path == Saved.IDEAS_LIST_PATH:
        return IdeasList()
    elif path == Saved.CATEGORIES_LIST_PATH:
        return []
    return []


def save_default_list(path: Path):
    save_list(get_default_list(path), path)
