__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import cegar
import simulateController

nrows = 6
ncols = 6
nagents = 1
initial = [28]
targets = [[ncols+1]]
obstacles = [14,15,20,21]
moveobstacles = [25]

beliefparts = 2
beliefcons = 3
target_reachability = False

gwfile = 'Examples/gridworldfig_6x6.png'
outfile = 'Examples/output_6x6'
infile = 'Examples/input_6x6'
cexfile = 'Examples/counterexample_6x6.txt'

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
gwg.draw_state_labels()
gwg.save(gwfile)

cegar.cegar_loop(gwg,moveobstacles,beliefcons,beliefparts,infile,outfile,cexfile,'safety',target_reachability)
