# B.i.t.Lock Solver
A solver for the awesome puzzle game [Block in the Lock](https://store.steampowered.com/app/1138990/Block_in_the_Lock/) (formerly known as B.i.t.Lock).

Currently supported blocks:
- 26 types of game tiles
- movable destroyer game tile
- obstacle/wall
- destroyer

Usage:
```
usage: bitlocksolve.py [-h] [-w] [-W arrows] [-t INT] [-f INT] mapfilename
  -h, --help            show this help message and exit
  -w, --walkthrough     Walkthrough after completion
  -W arrows, --walkthrough-path arrows
                        Walk through given direction arrows (do not solve)
  -t INT, --tree-size INT
                        Maximum number of tree levels to memorize before forgetful iteration.
  -f INT, --forgetful-size INT
                        Number of steps to simulate in forgetful iteration.
```

Mapfile is a text file representing the 2D game map and uses following conventions:
| character | meaning |
|-----------|---------|
| `a`-`z`   | A starting point for a game tile. Use different letters for discriminable tiles. |
| `A`-`Z`   | A target point for a game tile. Corresponds to lower-case letters of the starting point. |
| `#`       | An obstacle (or a wall). Make sure the map is surrounded by those. |
| `+`       | A destroyer block (game tiles landing in it will vanish). |
| `*`       | A destroyer game tile (also moves). |

## Game rules
Given is a 2D tiled map containing blocks of various types:
- game tiles
- destroyer tiles (also move), blocked by destroyer blocks
- obstacle/wall
- destroyer blocks
- many more are available in the game but not implemented in this solver.

The player has 4 possible decisions in each step: Left, right, up or down.
After selecting a direction, all game tiles (including destroyer tiles) move one step in this direction, _if possible_.
They can e.g. be blocked by an obstacles or destroyed by a, you guessed it, destroyer block.
Ideally, after as few steps as possible, the game tiles are in the _target position_.

## Solving concept
This is a brute-force solver which walks through all possible combinations of directions.
This builds up a tree with 4 edges (directions) after each node (tile constellation).
The solver iterates breadth-first through the tree, so if it finds a solution it is guaranteed to use a minimal number of steps (=tree levels).
Generated nodes with already seen tile constellations are neglected (because we already know a shorter path).

## Performance
### Computational Complexity
The upper bound of computational complexity is an inconceivable _O_(4<sup>_n_</sup>),
(_n_ is the step count)
i.e. 4 directions are added to all possible paths in each step.
The real complexity, however, is lower but hard to define, since it depends on the map.
This is because already seen tile constellations are rejected,
which happens more often in smaller maps.

An infinitely expanded map with no obstacles is solved in _O_(_n_<sup>2</sup>),
because only at the perimeter of new positions can be found, which grows with the square of the radius.

An infinitely expanded map with no obstacles and height 1 is solved in _O_(_n_).

### Memory complexity
This is the hurtful part.
Because all paths in the tree possibly lead to the solution we have to memorize the whole tree,
whose memory complexity has an upper bound of _O_(4<sup>_n_</sup>).
We even need to save the tile constellation of all nodes, to check if we already know a shorter path to a newly generated one.

## Outlook (ToDo)
- [x] The bottleneck seems to be the memory complexity.
Since the computations are, even in a non-optimized version, pretty low-cost, it might be advantageous to memorize the tree only up to a certain limit (tree level).
Thereafter, we could compute all possibilities for the next _k_ steps height-first.
If we find a solution we save the path, the tree itself is not saved (forgetful iteration).
Set _k_ = _pathlength_ - 1, to ensure new solutions are shorter.
- [x] Additionally to the _forgetful iteration_, we could sort the nodes of the last saved level by distance to the target to find more likely minimal solutions first.
- [ ] Add [multithreading](https://docs.python.org/3/library/multiprocessing.html) support.
