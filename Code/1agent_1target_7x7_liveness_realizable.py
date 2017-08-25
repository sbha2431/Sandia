__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import cegar
import simulateController
import grid_partition

nrows = 7
ncols = 7
nagents = 1
initial = [19]
targets = [[24]]
obstacles = [16,17,18,23,24,25,30,31,32]
moveobstacles = [38]
velocity = 2


beliefparts = 2
belief_safety = 0 
belief_liveness = 3
target_reachability = False

gwfile = 'Examples/gridworldfig_7x7_unrealizable.png'
outfile = 'Examples/output_5x5_unrealizable'
infile = 'Examples/input_5x5_unrealizable'
cexfile = 'Examples/counterexample_5x5_unrealizable.txt'

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
gwg.draw_state_labels()
gwg.save(gwfile)

cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,dict(),True)

# with precise partition of size 16
#partition = grid_partition.precise_partition(gwg)
#cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,partition)
