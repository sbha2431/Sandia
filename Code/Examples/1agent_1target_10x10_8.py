__author__ = 'sudab'


import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gridworld import *
import simulateController
# Define gridworld parameters
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
outfile = 'slugs_output_1agent10x10_8_belief.json'
gwg.draw_state_labels()
beliefparts = 8
beliefcons = 10

simulateController.userControlled_belief(outfile,gwg,beliefparts)
