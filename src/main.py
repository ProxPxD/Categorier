#!/usr/bin/python
from __future__ import annotations

import sys
from shlex import shlex

from categorierCli import CategorierCli
from nodes import NodesManager, Paths


def main():
    in_debug = True
    if not in_debug:
        args = sys.argv
        NodesManager.load_data(Paths.RESOURCES / 'debug.yml')
        # NodesManager.load_data(Paths.DATABASE)
    else:
        NodesManager.load_data(Paths.DATABASE)
        args = get_args_for_test()

    cli = CategorierCli()
    cli.parse(args)
    NodesManager.save_data()


def get_args_for_test():
    return shlex('mem del 1 2 3 ')
    # return shlex('mem add dziecko Yay ')


if __name__ == '__main__':
    main()
