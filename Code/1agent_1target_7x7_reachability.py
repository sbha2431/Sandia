__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import cegar
import simulateController
import time

nrows = 7
ncols = 7
nagents = 1
initial = [10]
targets = [[32]]
obstacles = [16,17,18,24]
moveobstacles = [37]
velocity = 1
 
beliefparts = 2
belief_safety = 50
belief_liveness = 0
target_reachability = True


outfile = 'Examples/output_7x7_reachability'
infile = 'Examples/input_7x7_reachability'
cexfile = 'Examples/counterexample_7x7_reachability.txt'
gwfile = 'Examples/gridworldfig_7x7_reachability.png'

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
gwg.draw_state_labels()
gwg.save(gwfile)

cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,dict(),True)

