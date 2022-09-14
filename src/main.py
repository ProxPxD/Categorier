#!/usr/bin/python
from __future__ import annotations

import sys
from dataclasses import dataclass

import configurations
from configurations import Saved
from idea import Idea
from category import Category


@dataclass
class Flags:
    CATEGORY = 'cat'
    DESCRIPTIONS = '-d'
    SUBS = '-s'
    SHOW = 'show'
    IDEAS = 'ideas'


def get_range_save(args: list[str], start: int, end: int = None) -> list[str] | str:
    if len(args) <= start:
        return []
    return args[start:end] if end is not None else args[start:]


def get_value_save(args: list[str], index: int, otherwise=None) -> str:
    return args[index] if index < len(args) else otherwise


def get_idea(args: list[str]) -> Idea | None:
    if not args:
        return None
    content = args[0]
    categories = get_range_save(args, 1)
    descriptions = parse_descriptions(args)
    return Idea(content, categories, descriptions)


def get_new_category(args: list[str]) -> Category:
    category_name = args[0]
    description = get_value_save(args, 1)
    sub_categories = parse_subs(args) or get_range_save(args, 2)
    return Category(category_name, description, sub_categories)


def parse_descriptions(args: list[str]):
    return parse_flag(args, Flags.DESCRIPTIONS)


def parse_subs(args: list[str]):
    return parse_flag(args, Flags.SUBS)


def parse_flag(args: list[str], flag: str):
    start = args.index(flag) if flag in args else None
    return args[start:] if start is not None else []


def print_details(type: str):
    pass

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        args = [] or ['cat', 'debug_cat']
    ideasList = configurations.load_list(Saved.IDEAS_LIST_PATH)
    Category.load_categories()
    if Flags.CATEGORY in args:
        args.remove(Flags.CATEGORY)
        cat = get_new_category(args)
        configurations.save_list(Category.get_all_categories(), configurations.Saved.CATEGORIES_LIST_PATH)
    elif Flags.SHOW in args:
        arg = args[-1]
        print()
    else:
        ideasList.add(get_idea(args))
        configurations.save_list(ideasList, Saved.IDEAS_LIST_PATH)
    print('ideas:      ', ideasList)
    print('categories: ', [str(cat) for cat in Category.get_all_categories()])

