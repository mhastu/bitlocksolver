#!/bin/python3

from map import Map, IntMap
from node import Node
import sys

class Solver():
    # already seen tiles. if a newly calculated position is present here, the position is refused.
    seen = set()
    level = 0
    map = None

    def __init__(self, filename):
        self.map = IntMap(filename)
        self.seen = set()
        self.level = 0

    def solve(self):
        #mp.print()
        #print("-----------")
        root = Node(self.map.start)
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
        #print("----- LEVEL", self.level, "------")
        newleaves = set()  # leaves of new level
        for nodenum, node in enumerate(leaves):
            #print("node", nodenum)
            moves = mp.moves(node.tiles)
            for dir_i, newtiles in enumerate(moves):
                #print("direction", dir_i)
                #mp.print(newtiles)
                #print("-----------")
                newleaf = Node(newtiles, node, dir_i)
                if newleaf.tiles == mp.dest:
                    return newleaf.getrootpath()  # found path!
                if newleaf.tiles not in self.seen:
                    newleaves.add(newleaf)
                    self.seen.add(newleaf.tiles)
        if it_left <= 0:
            return False

        #print("------------------------------")
        self.level += 1
        return self.walk(mp, newleaves, it_left=it_left-1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage:", sys.argv[0], " <mapfilename>")
        exit(1)
    filename = sys.argv[1]
    Solver(filename).solve()
