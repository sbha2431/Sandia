__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import counterexample_parser

nrows = 6
ncols = 6
nagents = 1
initial = [28]
targets = [[ncols+1]]
obstacles = [14,15,20,21]
moveobstacles = [10]

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()

gwg.draw_state_labels()

beliefparts = 2
beliefcons = 2
counterexample_parser.run_counterexample('counterexample_6x6_2.txt',gwg,beliefparts)
