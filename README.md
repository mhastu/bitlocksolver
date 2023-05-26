# bitlocksolver
A solver for the awesome puzzle game [Block in the Lock](https://store.steampowered.com/app/1138990/Block_in_the_Lock/) (formerly known as B.i.t.Lock).
Currently one type of game tile and one type of obstacle is supported.

Usage:
```
bitlocksolve.py <mapfilename>
```

Mapfile is a text file representing the 2D game map and uses following conventions:
| character | meaning |
|-----------|---------|
| `x`       | An obstacle (or a wall). Make sure the map is surrounded by those. |
| `1`       | A starting point for a game tile. |
| `a`       | A target point for a game tile. |
