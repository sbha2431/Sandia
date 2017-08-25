__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import cegar
import simulateController
import grid_partition

nrows = 7
ncols = 5
nagents = 1
initial = [27]
targets = [[16]]
obstacles = [13,16,18]
moveobstacles = [12]
velocity = 1

beliefparts = 2
belief_safety = 1
belief_liveness = 0
target_reachability = False

outfile = 'Examples/output_5x7'
infile = 'Examples/input_5x7'
cexfile = 'Examples/counterexample_5x7.txt'
gwfile = 'Examples/gridworldfig_5x7.png'

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
