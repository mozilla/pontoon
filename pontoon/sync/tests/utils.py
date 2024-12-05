from os import mkdir
from os.path import join
from typing import Dict, Union


FileTree = Dict[str, Union[str, "FileTree"]]
"""Strings are files, dicts are directories."""


def build_file_tree(root: str, tree: FileTree) -> None:
    """
    Fill out `root` with `tree` contents:
    Strings are files, dicts are directories.
    """
    for name, value in tree.items():
        path = join(root, name)
        if isinstance(value, str):
            with open(path, "x") as file:
                if value:
                    file.write(value)
        else:
            mkdir(path)
            build_file_tree(path, value)
