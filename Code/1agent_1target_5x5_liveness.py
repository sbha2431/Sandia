__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import cegar
import simulateController
import grid_partition

nrows = 5
ncols = 5
nagents = 1
initial = [7]
targets = [[12]]
obstacles = [12]
moveobstacles = [17]
velocity = 1

beliefparts = 2
belief_safety = 0 
belief_liveness = 1 # with 2 realizable
target_reachability = False

gwfile = 'Examples/gridworldfig_5x5_liveness.png'
outfile = 'Examples/output_5x5_liveness'
infile = 'Examples/input_5x5_liveness'
cexfile = 'Examples/counterexample_5x5_liveness.txt'

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
gwg.draw_state_labels()
gwg.save(gwfile)

#partition = dict()
#partition[(0,0,0)] = {6,7,8,11}
#partition[(0,0,1)] = {13,16,17,18}

cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,dict(),True)

# with precise partition
#partition = grid_partition.precise_partition(gwg)
#cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,partition)
