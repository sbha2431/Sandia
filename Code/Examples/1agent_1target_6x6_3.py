__author__ = 'sudab'

import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gridworld import *
import simulateController
# Define gridworld parameters

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
gwg.render()
outfile = 'slugs_output_1agent6x6_3_belief.json'
gwg.draw_state_labels()
beliefparts = 3

simulateController.userControlled_belief(outfile,gwg,beliefparts)
