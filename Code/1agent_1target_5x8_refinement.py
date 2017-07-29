__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import cegar
import simulateController

nrows = 8
ncols = 5
nagents = 1
initial = [32]
targets = [[16]]
obstacles = [13,16,18,26,21,28,23]
moveobstacles = [12]

beliefparts = 2
beliefcons = 1
target_reachability = False

outfile = 'Examples/output_5x8'
infile = 'Examples/input_5x8'
cexfile = 'Examples/counterexample_5x8.txt'
gwfile = 'Examples/gridworldfig_5x8.png'

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
gwg.draw_state_labels()
gwg.save(gwfile)


cegar.cegar_loop(gwg,moveobstacles,beliefcons,beliefparts,infile,outfile,cexfile,'safety',target_reachability)

