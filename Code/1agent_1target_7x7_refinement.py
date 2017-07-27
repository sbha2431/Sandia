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
initial = [25]
targets = [[9]]
obstacles = [9,10,15,18,23,24,29,32,37,33,8,36,22]
moveobstacles = [17]

beliefparts = 2
beliefcons = 2
belief_only = True

outfile = 'Examples/output_5x6'
infile = 'Examples/input_5x6'
cexfile = 'Examples/counterexample_5x6.txt'
gwfile = 'Examples/gridworldfig_5x6.png'

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
gwg.draw_state_labels()
gwg.save(gwfile)

cegar.cegar_loop(gwg,moveobstacles,beliefcons,beliefparts,infile,outfile,cexfile,belief_only)

