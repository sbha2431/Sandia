__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import cegar
import simulateController
import time
import grid_partition

nrows = 7
ncols = 7
nagents = 1
initial = [19]
targets = [[10]]
obstacles = [23,24,25]
moveobstacles = [32]
velocity = 1

beliefparts = 2
belief_safety = 0
belief_liveness = 2
target_reachability = False


outfile = 'Examples/output_7x7_liveness'
infile = 'Examples/input_7x7_liveness'
cexfile = 'Examples/counterexample_7x7_liveness.txt'
gwfile = 'Examples/gridworldfig_7x7_liveness.png'

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
gwg.draw_state_labels()
gwg.save(gwfile)

partition = dict()
partition[(0,0,0)] = {8,9,10,11,12,15,16,17,18,19}
partition[(0,0,1)] = {26,29,30,31,32,33,36,37,38,39,40}
partition[(0,0,2)] = {22}


cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability)

# with precise partition
#partition = grid_partition.precise_partition(gwg)
#cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,partition)


