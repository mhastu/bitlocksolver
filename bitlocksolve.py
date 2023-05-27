#!/bin/python3
# TODO: multithreading

from map import Map, IntMap, TileList, Tile
from node import Node
import sys
#import time

class Solver():
    def __init__(self, filename):
        self.seen = set()  # already seen tiles. if a newly calculated position is present here, the position is refused.
        self.level = 0  # currently generated level in tree
        self.map = IntMap(filename)
        #self.lastleveltime = 0

    def solve(self):
        #mp.print()
        #print("-----------")
        root = Node(self.map.start)
        #self.lastleveltime = time.thread_time_ns()
        result = self.walk(self.map, set([root]))
        print(self.map.strpath(result))

    def walk(self, mp: Map, leaves: set[Node], it_left = 30):
        """Breadth-first iteration through tree.
        
        ## Parameters:
        mp: Game map.
        tiles: current position of each game tile.
        leaves: nodes to walk through
        it_left: number of iterations left.
        """
        self.level += 1
        #print(self.level, time.thread_time_ns() - self.lastleveltime)
        #self.lastleveltime = time.thread_time_ns()
        #print("----- LEVEL", self.level, "------")
        newleaves = set()  # leaves of new level
        for nodenum, node in enumerate(leaves):
            #print("node", nodenum)
            moves = mp.moves(node.tiles)  # type: list[TileList.hashabletype]
            for dir_i, newtiles in enumerate(moves):
                #print("direction", dir_i)
                #mp.print(newtiles)
                #print("-----------")
                newleaf = Node(newtiles, node, dir_i)
                if newleaf.tiles == mp.dest:
                    print("Found optimal path in", self.level, "steps:")
                    return newleaf.getrootpath()
                if newleaf.tiles not in self.seen:
                    newleaves.add(newleaf)
                    self.seen.add(newleaf.tiles)
        if it_left <= 0:
            return False

        #print("------------------------------")
        return self.walk(mp, newleaves, it_left=it_left-1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage:", sys.argv[0], " <mapfilename>")
        exit(1)
    filename = sys.argv[1]
    Solver(filename).solve()
