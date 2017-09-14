__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import cegar
import simulateController
import time
import grid_partition


nrows = 10
ncols = 15
nagents = 1
initial = [116]
targets = [[ncols+1]]
obstacles = [18,33,66,67,97,112,127,96,95,94,98,99,69,70,71,72,102,103,25,40,55,68]
moveobstacles = [101]
velocity = 3

beliefparts = 2
belief_safety = 0
belief_liveness = 1
target_reachability = True

outfile = 'Examples/output_10x15_live+reach2'
infile = 'Examples/input_10x15_live+reach2'
cexfile = 'Examples/counterexample_10x15_live+reach2.txt'
gwfile = 'Examples/gridworldfig_10x15_live+reach2.png'

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
gwg.draw_state_labels()
gwg.save(gwfile)

partition = dict()
partition[(0,0,0)] = {16,17,31,32,46,47,61,62,76,77,91,92,106,107,121,122}
partition[(0,1,0)] = {19,20,21,34,35,36,48,49,50,51,22,37,52,63,64,65,23,24,38,39,53,54,93,108,109,110,111,123,124,125,126}
partition[(0,2,0)] = {26,27,28,41,42,43,56,57,58,73,100,101,113,114,115,116,117,118,128,129,130,131,132,133}
partition[(1,2,0)] = {78,79,80,81,82,83,84,85,86,87,88}

cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,partition,True)



# with precise partition
#partition = grid_partition.precise_partition(gwg)
#cegar.cegar_loop(gwg,moveobstacles,velocity,beliefparts,infile,outfile,cexfile,belief_safety,belief_liveness,target_reachability,partition)
