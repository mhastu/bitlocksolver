from abc import ABC

class Map(ABC):
    width = None
    height = None

    def moves(self, pos, func) -> list[frozenset]:
        """Move each pos in tiles in all 4 directions and return a list of 4 sets of tiles."""
        pass

    def load(self, filename):
        pass

    def print(self, tiles):
        pass


class IntMap(Map):
    """A map where each position is represented by in integer."""
    width = None
    height = None
    directions = ["←", "→", "↑", "↓"]

    def __init__(self, filename=None, width=None, height=None, obstacles=None, start=None, dest=None):
        if filename is not None:
            self.load(filename)
        else:
            self.width = width
            self.height = height
            self.obstacles = obstacles
            self.start = start
            self.dest = dest
    
    def strpath(self, path_indices):
        return "".join([self.directions[i] for i in path_indices])

    def print(self, tiles = None):
        if tiles is None:
            tiles = []
        for line in self.str(tiles):
            print(line)
    
    def str(self, tiles):
        textmap = [self.width*[' '] for _ in range(self.height)]
        for h in range(self.height):
            for w in range(self.width):
                pos = h*self.width + w
                if pos in self.obstacles:
                    textmap[h][w] = "x"
                elif pos in self.dest:
                    textmap[h][w] = "a"
                elif pos in self.start:
                    textmap[h][w] = "1"
                # overwrite with current tiles
                if pos in tiles:
                    textmap[h][w] = "o"
            textmap[h] = ''.join(textmap[h])
        return textmap
    
    def moves(self, tiles):
        # ascending sort, because for left and up movement the upper and left-most tiles
        # have to be moved first (to prevent collision with a tile which could
        # actually be moved).
        tiles = sorted(list(tiles))
        left = self.__move(tiles.copy(), self.__left)
        up = self.__move(tiles.copy(), self.__up)
        tiles = tiles[::-1]  # reverse order for right and down
        right = self.__move(tiles.copy(), self.__right)
        down = self.__move(tiles.copy(), self.__down)
        return [left, right, up, down]  # must be consistent with self.directions!

    def __move(self, tiles: list[set], func):
        """Move each pos in tiles according to func, if possible."""
        for i, pos in enumerate(tiles):
            newpos = func(pos)
            #        collision with obstacle      collision with other tile
            if not ((newpos in self.obstacles) or (newpos in tiles)):
                tiles[i] = newpos
        return frozenset(tiles)  # make tiles hashable

    def __left(self, pos):
        return pos-1

    def __right(self, pos):
        return pos+1

    def __up(self, pos):
        return pos-self.width

    def __down(self, pos):
        return pos+self.width

    def load(self, filename):
        """Loads a textfile where all obstacles (including borders) are marked by x
        Returns 3 variables:
        obstacles: the positions of the obstacles as a set.
        start: the positions of the starting elements as a set.
        dest: the positions of the target points as a set.
        each position is an integer value counting row-first from top-left, i.e.
        pos=rownum*width + colnum
        """
        with open(filename, 'r') as file:
            textmap = file.read().splitlines()
        self.height = len(textmap)
        self.width = max(len(line) for line in textmap)
        self.obstacles = set()
        self.start = set()
        self.dest = set()
        for h, line in enumerate(textmap):
            for w, char in enumerate(line):
                if char == "x":
                    self.obstacles.add(h*self.width + w)
                elif char == "1":
                    self.start.add(h*self.width + w)
                elif char == "a":
                    self.dest.add(h*self.width + w)
        # make objects hashable
        self.obstacles = frozenset(self.obstacles)
        self.start = frozenset(self.start)
        self.dest = frozenset(self.dest)
