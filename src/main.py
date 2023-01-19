#!/usr/bin/python
from __future__ import annotations

import sys
from shlex import shlex

from categorierCli import CategorierCli
from nodes import NodesManager


def main():
    in_debug = True
    cli = CategorierCli()
    args = sys.argv if not in_debug else get_args_for_test()
    cli.parse(args)
    NodesManager.save_data()


def get_args_for_test():
    return shlex('m')


if __name__ == '__main__':
    main()
