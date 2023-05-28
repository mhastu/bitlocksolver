#!/bin/python3
import sys
from solver import Solver

if len(sys.argv) < 2:
    print("usage:", sys.argv[0], " <mapfilename> [-w|-W <arrows>]")
    print("      -w:          walkthrough after completion")
    print("      -W <arrows>: walkthrough given direction arrows")
    exit(1)
filename = sys.argv[1]
solver = Solver(filename)
if (len(sys.argv) > 2) and (sys.argv[2] == "-W"):
    if len(sys.argv) < 4:
        print("missing positional argument for -W: arrows")
        exit(2)
    solver.walkthrough(sys.argv[3])
    exit(0)

path = solver.solve()
if (len(sys.argv) > 2) and (sys.argv[2] == "-w"):
    solver.walkthrough(path)
