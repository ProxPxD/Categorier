import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ideasList import IdeasList


@dataclass
class Saved:
    RESOURCES = Path(__file__).parent / 'resources'
    DATA_DIR = RESOURCES / 'data'
    IDEAS_NAME = 'ideas.pickle'
    CATEGORIES_NAME = 'categories.pickle'
    IDEAS_PATH = DATA_DIR / IDEAS_NAME
    CATEGORIES_PATH = DATA_DIR / CATEGORIES_NAME

    TESTS_DIR = RESOURCES / 'tests'
    CATEGORIES_TESTS_PATH = TESTS_DIR / CATEGORIES_NAME
    IDEAS_TESTS_PATH = TESTS_DIR / IDEAS_NAME


def load_list(path: Path, test_mode=False):
    if not path.exists():
        _create_directories(test_mode)
        _save_default_list(path)

    with open(path, 'rb') as f:
        return pickle.load(f)


def save_list(list_to_save: Any, path: Path):
    with open(path, 'wb') as f:
        pickle.dump(list_to_save, f)


def get_default_list(path: Path):
    if Saved.IDEAS_NAME in path.name:
        return IdeasList()
    elif Saved.CATEGORIES_NAME in path.name:
        return []
    return []


def _save_default_list(path: Path, test_mode=False):
    save_list(get_default_list(path), path)


def _create_directories(test_mode=False):
    dirs = (Saved.RESOURCES, Saved.DATA_DIR) if not test_mode else (Saved.RESOURCES, Saved.TESTS_DIR)
    for path in dirs:
        if not path.exists():
            path.mkdir()


def remove_file(path: Path):
    path.unlink()
