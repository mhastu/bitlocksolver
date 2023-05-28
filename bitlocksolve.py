#!/bin/python3
import sys
from solver import Solver
import argparse


class BitLockSolve:
    def __init__(self):
        self.parse_args()

    def main(self):
        solver = Solver(self.args.mapfilename, treesize=self.args.tree_size, forgetfulsize=self.args.forgetful_size)

        if self.args.walkthrough_path:  # just simulate walkthrough, do not solve
            solver.walkthrough(sys.argv[3])
            exit(0)

        path = solver.solve()
        if path is not False and self.args.walkthrough:
            solver.walkthrough(path)

    def parse_args(self):
        argparser = argparse.ArgumentParser(
            prog="B.i.t.Lock Solver",
            description="""Solve levels by brute-force.
            If walkthrough is simulated, press enter to advance to next step.
            """
        )
        argparser.add_argument("mapfilename")
        argparser.add_argument("-w", "--walkthrough", action="store_true",
                               help="Walkthrough after completion")
        argparser.add_argument("-W", "--walkthrough-path", type=str, metavar="arrows",
                               help="Walk through given direction arrows (do not solve)")
        argparser.add_argument("-t", "--tree-size", type=int, metavar="INT", default=15,
                               help="Maximum number of tree levels to memorize before forgetful iteration.")
        argparser.add_argument("-f", "--forgetful-size", type=int, metavar="INT", default=5,
                               help="Number of steps to simulate in forgetful iteration.")

        self.args = argparser.parse_args()


# ========== ENTRY POINT ==========
if __name__ == "__main__":
    BitLockSolve().main()
# =================================
