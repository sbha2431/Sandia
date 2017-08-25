__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import cegar
import simulateController
import grid_partition

nrows = 7
ncols = 6
nagents = 1
initial = [9]
targets = [[33]]
obstacles = [14,15,16,20,26]
moveobstacles = [27]
velocity = 1

beliefparts = 2
belief_safety = 42
belief_liveness = 0
target_reachability = True

gwfile = 'Examples/gridworldfig_7x6_reachability.png'
outfile = 'Examples/output_7x6_reachability'
infile = 'Examples/input_7x6_reachability'
cexfile = 'Examples/counterexample_7x6_reachability.txt'

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
gwg.draw_state_labels()
gwg.save(gwfile)

cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,dict(),True)

# with precise partition
#partition = grid_partition.precise_partition(gwg)
#cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,partition)
