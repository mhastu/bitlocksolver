from abc import ABC
import numpy as np
from collections import Counter

class Tile:
    """Represents a game tile. Equal to other tile if positions and type are same.
    Equal to integer if integer==position."""
    def __init__(self, typ, pos):
        self.type = typ  # for distinguishing between tiles. 26 for destroyer tile
        self.pos = pos
    
    def is_destroyer(self):
        return self.type == 26
    
    def __eq__(self, other):
        if type(other) == int:
            return self.pos == other
        return (self.pos == other.pos) and (self.type == other.type)
    
    def __hash__(self):
        return hash(frozenset([self.pos, self.type]))

    def __lt__(self, other):
        return self.pos < other.pos  # for sorting


class TileList(list):
    """A sortable list of tiles."""
    hashabletype = frozenset

    def __add__(self, other):
        return TileList(super().__add__(other))

    def copy(self):
        """Return a TileList of new, equal Tile instances."""
        return TileList([Tile(t.type, t.pos) for t in self])

    def hashable(self) -> hashabletype:
        """Return a hashable set of this list."""
        return self.hashabletype(self)

    def dist(self, other, mp) -> float:
        """Distance to other TileList.
        
        Distance between two tiles is l2-norm + 1.
        Distance between two sets of indistinguishable tiles is the product of all distances.
        Distance between all tiles is the sum of all distances between all sets of tiles.
        """
        # calculate norm between all positions
        selfvecs = np.array([mp.pos2vec(st.pos) for st in self])[None]  # shape: (1, N, 2)
        selfvecs = np.transpose(selfvecs, [2, 1, 0])  # shape: (2, N, 1)
        othervecs = np.array([mp.pos2vec(ot.pos) for ot in other])[None]  # shape: (1, K, 2)
        othervecs = np.transpose(othervecs, [2, 0, 1])  # shape: (2, 1, K)
        norm1 = np.linalg.norm(selfvecs - othervecs, axis=0) + 1  # shape: (N, K)

        # extract types for comparing (in-)distinguishable tiles
        selftypes = np.array([st.type for st in self])  # shape: (N,)
        othertypes = np.array([ot.type for ot in other])  # shape: (K,)
        alltypes = set(list(selftypes) + list(othertypes))  # length: L (depends on repeated types)

        # sum over all set-distances
        dist = 0
        for typ in alltypes:
            setdist = np.prod(norm1[selftypes==typ,:][:,othertypes==typ])
            dist += setdist

        return dist


class Map(ABC):
    def moves(self, pos, func) -> list[TileList.hashabletype]:
        """Move each pos in tiles in all 4 directions and return a list of 4 sets of tiles."""
        pass

    def load(self, filename):
        pass

    def print(self, tiles):
        pass


class IntMap(Map):
    """A map where each position is represented by an integer."""
    DIRECTIONS = ['←', '→', '↑', '↓']
    START_CHARS = [chr(ord('a')+i) for i in range(26)] + ['*']  # index 26 is destroyer tile
    DEST_CHARS = [chr(ord('A')+i) for i in range(26)]
    OBSTACLE_CHAR = '#'
    DESTROYER_CHAR = '+'

    def __init__(self, filename=None, width=None, height=None, obstacles=None, start=None, dest=None):
        self.dir_funcs = [self.__left, self.__right, self.__up, self.__down]
        self.node_has_no_future = lambda tiles: not self.notzero_tiles(tiles)
        self.destroy_tiles = self.destroy_tiles_onlyblocks
        self.newpos_valid = lambda tile, newpos, tiles: not self.in_obstacle(newpos) and self.valid_with_othertiles(newpos, tiles)
        if filename is not None:
            self.load(filename)
        else:
            self.width = width
            self.height = height
            self.obstacles = obstacles
            self.start = start  # type: TileList.hashabletype  # a set of tiles in starting position
            self.dest = dest  # type: TileList.hashabletype  # a set of tiles in target position

    def __str__(self) -> str:
        return self.str()

    def str(self, tiles = None) -> str:
        if tiles is None:
            tiles = []  # cannot use mutable object as default
        textmap = [self.width*[' '] for _ in range(self.height)]
        # convert to list so we can search for positions
        startlist = list(self.start)
        destlist = list(self.dest)
        startpositions = [t.pos for t in startlist]
        destpositions = [t.pos for t in destlist]
        for h in range(self.height):
            for w in range(self.width):
                pos = self.vec2pos([h, w])
                if pos in self.obstacles:
                    textmap[h][w] = self.OBSTACLE_CHAR
                elif pos in self.destroyers:
                    textmap[h][w] = self.DESTROYER_CHAR
                #elif pos in startpositions:  # don't print start positions
                #    tile = startlist[startpositions.index(pos)]  # extract tile to get type
                #    textmap[h][w] = self.START_CHARS[tile.type]
                elif pos in destpositions:
                    tile = destlist[destpositions.index(pos)]  # extract tile to get type
                    textmap[h][w] = self.DEST_CHARS[tile.type]
        
        # overwrite with current tiles
        for tile in tiles:
            vec = self.pos2vec(tile.pos)
            h = vec[0]
            w = vec[1]
            textmap[h][w] = self.START_CHARS[tile.type]

        for h in range(self.height):
            textmap[h] = ''.join(textmap[h])
        textmap = '\n'.join(textmap)
        return textmap

    def strpath(self, path_indices) -> str:
        return "".join([self.DIRECTIONS[i] for i in path_indices])

    def moves(self, tiles) -> list[TileList.hashabletype]:
        """Return all possible moves as list[left, right, up, down]."""
        # ascending sort, because for left and up movement the upper and left-most tiles
        # have to be moved first (to prevent collision with a tile which could
        # actually be moved).
        tiles = TileList(sorted(tiles))
        left = self.__move(tiles.copy(), self.__left)
        up = self.__move(tiles.copy(), self.__up)
        tiles = TileList(tiles[::-1])  # reverse order for right and down
        right = self.__move(tiles.copy(), self.__right)
        down = self.__move(tiles.copy(), self.__down)
        return [left, right, up, down]  # must be consistent with self.DIRECTIONS!

    def move(self, tiles, dir):
        return self.__move(tiles, self.dir_funcs[dir])

    def __move(self, tiles: TileList, func) -> TileList.hashabletype:
        """Move each pos in tiles according to func, if possible.
        Assumes correctly sorted TileList.
        """
        for tile in tiles:
            newpos = func(tile.pos)  # type: int
            if self.newpos_valid(tile, newpos, tiles):
                tile.pos = newpos
        tiles = self.destroy_tiles(tiles)
        return tiles.hashable()  # make tiles hashable

    def newpos_valid(self, tile, newpos, tiles) -> bool:
        """True, if newly calculated position is valid."""
        pass  # set in __init__() and load()
    
    def valid_with_destroyertiles(self, tile: Tile, newpos: int, tiles: TileList) -> bool:
        """True, if newly calculated position is valid according to other tiles, destroyer tiles and destroyer blocks on map."""
        is_destroyer = tile.is_destroyer()
        if is_destroyer:
            if newpos in self.destroyers:
                return False  # destroyer tiles cannot move through destroyer blocks
        if newpos in tiles:
            othertile = tiles[tiles.index(newpos)]  # type: Tile
            if is_destroyer == othertile.is_destroyer():
                return False  # tiles only collide if different type (destroyer or not)
        return True

    def valid_with_othertiles(self, newpos: int, tiles: TileList) -> bool:
        """True if newly calculated position is not inside another tile."""
        return not (newpos in tiles)

    def in_obstacle(self, pos: int) -> bool:
        """True, if pos is inside an obstacle"""
        return pos in self.obstacles

    def destroy_tiles(self, tiles: TileList) -> TileList:
        """Let destroyer tiles and blocks destroy tiles."""
        pass  # set in __init__() and load()

    def destroy_tiles_onlyblocks(self, tiles: TileList) -> TileList:
        """Let destroyer blocks destroy tiles."""
        return TileList(filter(lambda t: t.pos not in self.destroyers, tiles))
    
    def destroy_tiles_with_destroyertiles(self, tiles: TileList) -> TileList:
        """Filter tiles destroyed by destroyer tiles and blocks."""
        destroyer_tiles = TileList(filter(lambda t: t.is_destroyer(), tiles))
        normal_tiles = TileList(filter(lambda t: not t.is_destroyer(), tiles))  # can this partitioning be done faster?
        survived = lambda t: (
            (t.pos not in self.destroyers) and  # not destroyed by block
            (t.pos not in destroyer_tiles)  # not destroyed by tile
        )
        # destroyer tiles always survive
        return destroyer_tiles + TileList(filter(survived, normal_tiles))

    def __left(self, pos) -> int:
        return pos-1

    def __right(self, pos) -> int:
        return pos+1

    def __up(self, pos) -> int:
        return pos-self.width

    def __down(self, pos) -> int:
        return pos+self.width

    def load(self, filename) -> None:
        """Loads a textfile as a map.
        Sets 3 variables:
        self.obstacles: the positions of the obstacles as a set.
        self.destroyers: the positions of the destroyer blocks as a set.
        self.start: the positions of the starting elements as a list, containing indistinguishable sets of tiles.
        self.dest: the positions of the target points as a list, containing indistinguishable sets of tiles.
        each position is an integer value counting row-first from top-left, i.e.
        pos=rownum*width + colnum
        """
        with open(filename, 'r') as file:
            textmap = file.read().splitlines()
        self.height = len(textmap)
        self.width = max(len(line) for line in textmap)
        self.obstacles = TileList()
        self.destroyers = TileList()
        self.start = TileList()
        self.dest = TileList()

        # parse textmap
        for h, line in enumerate(textmap):
            for w, char in enumerate(line):
                pos = self.vec2pos([h, w])
                if char == self.OBSTACLE_CHAR:
                    self.obstacles.append(pos)
                if char == self.DESTROYER_CHAR:
                    self.destroyers.append(pos)
                if char in self.START_CHARS:
                    self.start.append(Tile(self.START_CHARS.index(char), pos))
                if char in self.DEST_CHARS:
                    self.dest.append(Tile(self.DEST_CHARS.index(char), pos))

        # make objects hashable
        self.obstacles = self.obstacles.hashable()
        self.destroyers = self.destroyers.hashable()
        self.start = self.start.hashable()
        self.dest = self.dest.hashable()

        error = self.check_for_errors()
        if error:
            print("ERROR: " + error)
            exit(10)
        
        # default
        self.node_has_no_future = lambda tiles: not self.notzero_tiles(tiles)
        if len(self.destroyers) > 0:
            # always count tiles if destroyer block is present
            self.node_has_no_future = lambda tiles: (not self.notzero_tiles(tiles)) or (not self.enough_tiles(tiles))
        
        # default
        self.destroy_tiles = self.destroy_tiles_onlyblocks
        self.newpos_valid = lambda tile, newpos, tiles: not self.in_obstacle(newpos) and self.valid_with_othertiles(newpos, tiles)
        if self.has_destroyer_tiles():  # map has destroyer tiles
            self.destroy_tiles = self.destroy_tiles_with_destroyertiles
            self.newpos_valid = lambda tile, newpos, tiles: not self.in_obstacle(newpos) and self.valid_with_destroyertiles(tile, newpos, tiles)

    def has_destroyer_tiles(self) -> bool:
        """True, if destroyer tiles exist on map."""
        return len([t for t in self.start if t.is_destroyer()]) > 0

    def check_for_errors(self) -> str or False:
        """Returns error string if map blocks are invalid, else False."""
        if len(self.obstacles) == 0:
            return "No obstacles in map"
        if len(self.dest) == 0:
            return "No target blocks in map"
        if len(self.start) == 0:
            return "No starting blocks in map"
        
        starttypes = set([st.type for st in self.start])
        desttypes = set([dt.type for dt in self.dest])
        for typ in desttypes:
            if typ not in starttypes:
                return "No corresponding starting tile for target tile " + self.DEST_CHARS[typ]
        
        # change this if a generator block is added
        if not self.enough_tiles(self.start):
            return "Did not find enough starting tiles for all target tiles."

        for h in range(self.height):
            for w in range(self.width):
                pos = self.vec2pos([h, w])
                if self.isborder(pos) and (pos not in self.obstacles) and (pos not in self.destroyers):
                    return "Map is not surrounded by obstacle or destroyer blocks"
        
        return False
    
    def isborder(self, pos):
        """True, if pos is at the border of the map."""
        vec = self.pos2vec(pos)
        h = vec[0]
        w = vec[1]
        return (h==0) or (h==(self.height-1)) or (w==0) or (w==(self.width-1))

    def pos2vec(self, pos):
        """Convert pos (int) to 2-coordinate vector."""
        w = pos % self.width
        h = (pos - w) // self.width
        return [h, w]

    def vec2pos(self, vec):
        """Convert vec (h, w) to pos (int)."""
        h = vec[0]
        w = vec[1]
        return h*self.width + w

    def enough_tiles(self, tiles):
        """True, if set of tiles are enough for target (types must also match)."""
        if len(tiles) < len(self.dest):
            return False
        desttypes = [tile.type for tile in self.dest]
        desttypesn = Counter(desttypes)
        types = [tile.type for tile in tiles]
        typesn = Counter(types)
        for typ in desttypesn.keys():
            if typesn[typ] < desttypesn[typ]:
                return False
        return True
    
    def notzero_tiles(self, tiles):
        return len(tiles) != 0

    def node_has_no_future(self, tiles):
        """True, if set of tiles can't lead to solution anymore."""
        pass  # set in load function
