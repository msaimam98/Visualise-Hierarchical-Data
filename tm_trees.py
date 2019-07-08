"""Assignment 2: Trees for Treemap

=== CSC148 Winter 2019 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """
    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None
        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        self._expanded = False

        if len(self._subtrees) == 0:
            self.data_size = data_size
        else:
            self.data_size = self._get_data_size()
            for subtree in self._subtrees:
                subtree._parent_tree = self

    def _get_data_size(self) -> int:
        if len(self._subtrees) == 0:
            return self.data_size
        else:
            data_size = 0
            for subtree in self._subtrees:
                data_size += subtree._get_data_size()
            return data_size

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """
        if self.data_size == 0:
            return
        self.rect = rect
        l, j, width, height = rect
        size = self.data_size

        for i in range(len(self._subtrees)):
            subtree = self._subtrees[i]
            if i < len(self._subtrees) - 1:
                ratio = subtree.data_size / size
                if width > height:
                    new_width = int(width * ratio)
                    rect1 = (l, j, new_width, height)
                    l += rect1[2]
                else:
                    new_height = int(height * ratio)
                    rect1 = (l, j, width, new_height)
                    j += rect1[3]
                subtree.update_rectangles(rect1)
            else:
                if width > height:
                    rect1 = (l, j, width + rect[0] - l, height)
                    subtree.update_rectangles(rect1)
                else:
                    rect1 = (l, j, width, height + rect[1] - j)
                    subtree.update_rectangles(rect1)

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int], \
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        >>> x = FileSystemTree('example-directory')
        >>> rect = (0, 0, 100, 100)
        >>> x.update_rectangles(rect)
        >>> x.get_rectangles()
        [((), ())]
        """
        if self.is_empty():
            return []
        elif self._subtrees == [] or not self._expanded:
            return [(self.rect, self._colour)]
        else:
            rectangles = []
            for subtree in self._subtrees:
                rectangles += subtree.get_rectangles()
            return rectangles

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is closer to the origin.
        """
        if self._subtrees == [] or not self._expanded:
            x1, y1, width, height = self.rect
            contains_position = (x1 <= pos[0] <= x1 + width) and \
                                (y1 <= pos[1] <= y1 + height)
            if contains_position:
                return self
            else:
                return None

        result = None

        def _get_closer_to_origin(sub: subtree) -> Optional[TMTree]:
            if not result:
                return sub
            else:
                curr_pos, next_pos = result.rect[:-2], sub.rect[:-2]
                # if next is on top or on the left return sub.
                if next_pos[1] < curr_pos[1] or next_pos[0] < curr_pos[0]:
                    return sub
                # else return None
                else:
                    return result

        for subtree in self._subtrees:
            valid = subtree.get_tree_at_position(pos)
            if valid:
                result = _get_closer_to_origin(valid)
        return result

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.
        If this tree is a leaf, return its size unchanged.
        """
        if not self._subtrees:
            return self.data_size
        else:
            size = 0
            for subtree in self._subtrees:
                size += subtree.update_data_sizes()
            self.data_size = size
        if size == 0:
            self.rect = (0, 0, 0, 0)
        return size

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        if self._subtrees == [] and destination._subtrees != []:
            self._parent_tree._subtrees.remove(self)
            destination._subtrees.append(self)
            if self._parent_tree._subtrees == []:
                self._parent_tree.data_size = 0
                self._parent_tree.rect = (0, 0, 0, 0)
            self._parent_tree = destination

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.
        Always round up the amount to change, so that it's an int, and
        some change is made.
        Do nothing if this tree is not a leaf.
        """
        if self._subtrees == []:
            size = math.ceil(abs(self.data_size * factor))
            if factor >= 0:
                new_size = self.data_size + size
            else:
                new_size = self.data_size - size

            self.data_size = 1 if new_size < 1 else new_size

    def expand(self) -> None:
        """ Expand selected folder. """
        if self._subtrees:
            self._expanded = True

    def expand_all(self) -> None:
        """ Expand all files and folder in folder. """
        if self._subtrees:
            self._expanded = True
            for subtree in self._subtrees:
                subtree.expand_all()

    def collapse(self) -> None:
        """ Collapse selected file/folder """
        if self._parent_tree is not None and self._parent_tree._expanded:
            self._parent_tree._collapse_everything_under()

    def _collapse_everything_under(self) -> None:
        if self._subtrees:
            self._expanded = False
            for subtree in self._subtrees:
                subtree._collapse_everything_under()

    def collapse_all(self) -> None:
        """Collapse everything """
        now = self
        while now._parent_tree is not None and now._parent_tree._expanded:
            now = now._parent_tree
        now._collapse_everything_under()

    # Methods for the string representation
    def get_path_string(self, final_node: bool = True) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name. If <final_node>, then add the suffix for the tree.
        """
        if self._parent_tree is None:
            path_str = self._name
            if final_node:
                path_str += self.get_suffix()
            return path_str
        else:
            path_str = (self._parent_tree.get_path_string(False) +
                        self.get_separator() + self._name)
            if final_node or len(self._subtrees) == 0:
                path_str += self.get_suffix()
            return path_str

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """

        if not os.path.isdir(path):
            name = os.path.basename(path)
            size = os.path.getsize(path)
            TMTree.__init__(self, name, [], size)
        else:
            subtree1 = []
            for filename in os.listdir(path):
                subtree = FileSystemTree(os.path.join(path, filename))
                subtree1.append(subtree)

            name1 = os.path.basename(path)
            TMTree.__init__(self, name1, subtree1)

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (folder)'


if __name__ == '__main__':
    import python_ta

    x = FileSystemTree('example-directory')
    y = 5

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })





