__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import counterexample_parser

nrows = 10
ncols = 10
nagents = 1
initial = [88]
targets = [[ncols+1]]
obstacles = [34,44,45,54,55,64,47]
moveobstacles = [68]

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.render()

gwg.draw_state_labels()
beliefparts = 4
beliefcons = 10
counterexample_parser.run_counterexample('counterexample_10x10.txt',gwg,beliefparts)
