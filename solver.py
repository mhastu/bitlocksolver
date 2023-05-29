from map import Map, IntMap, TileList, Tile
from node import Node


class Tree:
    """Represents the game moves-tree.
    Saved are just the leaves (Node objects) from where one can iterate from above.
    Additionally, the "seen" set contains all seen tile constellations.
    """
    def __init__(self, leaves: set[Node], seen: set = None):
        self.leaves = leaves  # type: set[Node]
        self.seen = seen  # type: set[frozenset]
        if self.seen is None:
            self.seen = set()
        self.height = 0  # level of the leaves


class Solver():
    def __init__(self, filename: str, treesize: int, forgetfulsize: int):
        self.map = IntMap(filename)
        self.treesize = treesize
        self.forgetfulsize = forgetfulsize

    def solve(self) -> list or False:
        """Search for solution.
        
        ## Returns
        - path (list) if solution found.
        - False, if no solution found.
        """
        root = Node(self.map.start)
        print(f"Building tree with {self.treesize} levels... ")
        treeresult = self.buildtree(set([root]))
        print("Done.")
        if type(treeresult) == list:
            path = treeresult
            print(f"Found optimal path in {len(path)} steps:")
            print(self.map.strpath(path))
            return path
        if type(treeresult) == int:
            dead_end_step = treeresult
            print(f"No moves possible anymore after {dead_end_step} steps.")
            return False
        if type(treeresult) == Tree:
            tree = treeresult
            print(f"Starting forgetful iteration with additional path-length of {self.forgetfulsize}... ")
            result = self.forgetful_iteration(tree, self.forgetfulsize)
            print("Done.")
            if result is False:
                print(f"Found no solution in {self.treesize+self.forgetfulsize} steps.")
            elif type(result) == list:
                path = result
                print(f"Found optimal path in {len(path)} steps:")
                print(self.map.strpath(path))
            return result

    def buildtree(self, leaves: set[Node]) -> list or Tree or int:
        """Breadth-first iteration through tree.

        ## Parameters:
        tiles: current position of each game tile.
        leaves: nodes to walk through
        it_left: number of iterations left.

        ## Returns
        - path: (list) if optimal solution found inside tree.
        - tree: (Tree) if no solution found in tree.
        - steps: (int) if no moves possible anymore.
        """
        tree = Tree(leaves)
        for level in range(self.treesize):
            newleaves = set()  # leaves of new level
            for node in tree.leaves:
                moves = self.map.moves(node.tiles)  # type: list[TileList.hashabletype]
                for dir_i, newtiles in enumerate(moves):
                    if self.map.node_has_no_future(newtiles):
                        continue
                    newleaf = Node(newtiles, node, dir_i)
                    if newleaf.tiles == self.map.dest:
                        return newleaf.getrootpath()
                    if newleaf.tiles not in tree.seen:
                        newleaves.add(newleaf)
                        tree.seen.add(newleaf.tiles)
            if len(newleaves) == 0:
                return level
            tree.leaves = newleaves
            tree.height = level+1
            print(f"{tree.height}/{self.treesize}", end="\r")
        print("           ", end="\r")  # delete progress counter
        return tree

    def forgetful_iteration(self, tree, length) -> list or False:
        """Try all possibilities starting starting from tree.leaves, with given path-length.
        
        ## Parameters:
        tree: (Tree) We start at its leaves.
        length: (int) Maximum length of each additional path to try.

        ## Returns
        - path (list) if optimal path found.
        - False if no optimal path found.
        """
        # sort nodes by distance to destination
        nodes = list(tree.leaves)
        print(f"  Sorting {len(nodes)} leaves by distance to target... ", end="")
        dest = TileList(self.map.dest)
        distances = [TileList(node.tiles).dist(dest, self.map) for node in nodes]
        nodes = [node for _, node in sorted(zip(distances, nodes), key=lambda pair: pair[0])]
        print("Done.")

        maxlength = length
        path = False  # optimal path
        numleaves = len(tree.leaves)
        for i, node in enumerate(tree.leaves):
            result = self.iterate_heightfirst(node, tree.height, maxlength, 0)
            if type(result) == list:
                path = result
                print(f"  Found solution in {len(path)} (+{len(path) - tree.height}) steps:", self.map.strpath(path))
                maxlength = len(path) - tree.height - 1  # adjust maximum step length
            print(f"{i}/{numleaves}", end="\r")
        print("           ", end="\r")  # delete progress counter
        return path
    
    def iterate_heightfirst(self, node, treeheight, maxlength, depth):
        """Search for solution by height-first iteration, beginning at node.

        ## Parameters:
        node: (Node) node object to start from.
        baseheight: (int) memorized tree height to start from.
        treeheight: (int) number of steps to try.
        depth: (int) current iteration depth.

        ## Returns
        - False if no solution has been found,
        - path (list) if solution has been found.
        """
        path = False
        if (maxlength - depth) <= 0:
            return False
        moves = self.map.moves(node.tiles)  # type: list[TileList.hashabletype]
        for dir_i, newtiles in enumerate(moves):
            if self.map.node_has_no_future(newtiles):
                continue
            newleaf = Node(newtiles, node, dir_i)
            if newleaf.tiles == self.map.dest:
                return newleaf.getrootpath()
            result = self.iterate_heightfirst(newleaf, treeheight, maxlength, depth+1)
            if type(result) == list:  # found a solution
                path = result
                maxlength = len(path) - treeheight - 1  # adjust maximum step length
        return path

    def walkthrough(self, path: list or str):
        """Simulate walkthrough. Advance with Enter.

        ## Parameters:
        path: list of directions (int) or string of arrows
        """
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
