from map import TileList

class Node():
    def __init__(self, tiles: TileList.hashabletype, parent = None, parent_edge = None):
        self.tiles = tiles  # type: TileList.hashabletype
        self.parent = parent  # type: Node or None  # None ==> Node is root
        self.parent_edge = parent_edge  # type: int or None  # one of [None, 0, 1, 2, 3]
    
    def get_tiles(self) -> TileList.hashabletype:
        """Return game tiles."""
        return self.tiles

    def is_root(self) -> bool:
        return self.parent == None

    def getrootpath(self) -> list[int]:
        """Returns path from root to node as list."""
        if self.parent.is_root():
            return [self.parent_edge]
        return self.parent.getrootpath() + [self.parent_edge]


class NodeWithDestroyerTileSupport(Node):
    """Node which supports destroyer tiles."""
    def get_tiles(self) -> TileList.hashabletype:
        """Return game tiles (no destroyer tiles)."""
        return TileList(filter(lambda t: not t.is_destroyer(), self.tiles)).hashable()
