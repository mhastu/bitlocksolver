from map import Map, IntMap, TileList, Tile
from node import Node
import sys
#import time

# TODO: multithreading

class Solver():
    maxit = 20

    def __init__(self, filename, maxit: int = None):
        if maxit is not None:
            self.maxit = maxit

        self.seen = set()  # already seen tiles. if a newly calculated position is present here, the position is refused.
        self.level = 0  # currently generated level in tree
        self.map = IntMap(filename)
        #self.lastleveltime = 0

    def solve(self):
        #print(self.map)
        #print("-----------")
        root = Node(self.map.start)
        #self.lastleveltime = time.thread_time_ns()
        path = self.walk(self.map, set([root]))
        if path is False:
            print("Found no optimal path in", self.maxit, "steps.")
        elif path is None:
            print("No moves possible anymore after", self.level, "steps.")
        else:
            print("Found optimal path in", self.level, "steps:")
            print(self.map.strpath(path))
        return path

    def walk(self, mp: Map, leaves: set[Node], it_left = None):
        """Breadth-first iteration through tree.
        
        ## Parameters:
        mp: Game map.
        tiles: current position of each game tile.
        leaves: nodes to walk through
        it_left: number of iterations left.
        """
        if it_left is None:
            it_left = self.maxit

        self.level += 1
        #print(self.level, time.thread_time_ns() - self.lastleveltime)
        print(self.level)
        #self.lastleveltime = time.thread_time_ns()
        #print("----- LEVEL", self.level, "------")
        newleaves = set()  # leaves of new level
        for nodenum, node in enumerate(leaves):
            #print("node", nodenum)
            moves = mp.moves(node.tiles)  # type: list[TileList.hashabletype]
            for dir_i, newtiles in enumerate(moves):
                #print("direction", dir_i)
                #print(mp.str(newtiles))
                #print("-----------")
                if len(newtiles) == 0:
                    continue  # no moves possible for this node
                newleaf = Node(newtiles, node, dir_i)
                if newleaf.tiles == mp.dest:
                    return newleaf.getrootpath()
                if newleaf.tiles not in self.seen:
                    newleaves.add(newleaf)
                    self.seen.add(newleaf.tiles)
        if len(newleaves) == 0:
            return None
        if it_left <= 0:
            return False

        #print("------------------------------")
        return self.walk(mp, newleaves, it_left=it_left-1)

    def walkthrough(self, path):
        if type(path) == str:  # arrow path string
            try:
                path = [self.map.DIRECTIONS.index(a) for a in path]
            except ValueError:
                print("ERROR: use arrow symbols (like in output) to specify walkthrough path")
                return

        tiles = self.map.start
        print(self.map.str(tiles))
        for dir in path:
            print(self.map.DIRECTIONS[dir])
            tiles = TileList(sorted(tiles))
            if dir in [1, 3]:
                tiles = tiles[::-1]
            tiles = self.map.move(tiles, dir)
            print(self.map.str(tiles))
            input()
