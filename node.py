class Node():
    parent = None  # type: Node  # None ==> Node is root
    parent_edge = None  # one of [None, 0, 1, 2, 3]
    tiles = None  # type: int

    def __init__(self, tiles: set, parent = None, parent_edge = None):
        self.tiles = tiles
        self.parent = parent
        self.parent_edge = parent_edge
    
    def is_root(self):
        return self.parent == None

    def getrootpath(self):
        """Returns path from root to node as list."""
        if self.parent.is_root():
            return [self.parent_edge]
        return self.parent.getrootpath() + [self.parent_edge]
