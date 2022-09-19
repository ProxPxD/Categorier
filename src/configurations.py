import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Paths:
    RESOURCES = Path(__file__).parent / 'resources'
    DATA_DIR = RESOURCES / 'data'
    IDEAS_NAME: str = 'ideas.pickle'
    CATEGORIES_NAME: str = 'categories.pickle'
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
    if Paths.IDEAS_NAME in path.name:
        return None
    elif Paths.CATEGORIES_NAME in path.name:
        return []
    return []


def _save_default_list(path: Path, test_mode=False):
    save_list(get_default_list(path), path)


def _create_directories(test_mode=False):
    dirs = (Paths.RESOURCES, Paths.DATA_DIR) if not test_mode else (Paths.RESOURCES, Paths.TESTS_DIR)
    for path in dirs:
        if not path.exists():
            path.mkdir()


def remove_file(path: Path):
    if path.exists():
        path.unlink()
