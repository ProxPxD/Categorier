#!/usr/bin/python
import sys

import configurations
from idea import Idea


def get_idea(args: list[str]):
    content = args[1]
    categories = args[2:] if len(args) > 1 else []
    return Idea(content, categories)


if __name__ == '__main__':
    ideasList = configurations.load_list()
    ideasList.add(get_idea(sys.argv))
    print(len(ideasList))
    print(ideasList)

