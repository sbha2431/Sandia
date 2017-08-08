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
initial = [19]
targets = [[10]]
obstacles = [23,24,25]
moveobstacles = [32]
velocity = 1

beliefparts = 2
belief_safety = 10
belief_liveness = 2
target_reachability = False


outfile = 'Examples/output_7x7_live+safe'
infile = 'Examples/input_7x7_live+safe'
cexfile = 'Examples/counterexample_7x7_live+safe.txt'
gwfile = 'Examples/gridworldfig_7x7_live+safe.png'

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
gwg.draw_state_labels()
gwg.save(gwfile)


cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability)



