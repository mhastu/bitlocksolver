from map import TileList

class Node():
    def __init__(self, tiles: TileList.hashabletype, parent = None, parent_edge = None):
        self.tiles = tiles  # type: TileList.hashabletype
        self.parent = parent  # type: Node or None  # None ==> Node is root
        self.parent_edge = parent_edge  # type: int or None  # one of [None, 0, 1, 2, 3]

    def is_root(self):
        return self.parent == None

    def getrootpath(self):
        """Returns path from root to node as list."""
        if self.parent.is_root():
            return [self.parent_edge]
        return self.parent.getrootpath() + [self.parent_edge]
