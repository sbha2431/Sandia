__author__ = 'sudab'

import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gridworld import *
import simulateController
import grid_partition
# Define gridworld parameters
nrows = 15
ncols = 20
nagents = 1
initial = [237,257]
targets = [[ncols+1]]
obstacles = [153,154,155,173,174,175,193,194,195,213,214,215,233,234,235,68,69,88,89,108,109,128,129,183,184,185,186,187,203,204,205,206,207,223,224,225,226,227]
moveobstacles = [197]

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.render()
outfile = 'slugs_output_1agent15x20_8.json'
gwg.draw_state_labels()
beliefparts = 8
partition = grid_partition.partitionGrid(gwg,beliefparts)
simulateController.userControlled_partition(outfile,gwg,partition,moveobstacles)
