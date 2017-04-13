__author__ = 'sudab'

from gridworld import *
import grid_partition
import Slugs_input
import Salty_input
import random
import os
import subprocess
import visibility
import simplejson as json
import time
import simulateController
#Define gridworld parameters
# nrows = 15
# ncols = 20
# nagents = 1
# initial = [237,257]
# targets = [[ncols+1]]
# obsnum = 3
# # obstacles = [27,63,78,26,37,36,72,62,73,77,67,66,76,52,53,68,16,17]
# obstacles = [153,154,155,173,174,175,193,194,195,213,214,215,233,234,235,68,69,88,89,108,109,128,129,183,184,185,186,187,203,204,205,206,207,223,224,225,226,227]
# # obstacles = [15,16,19]
# moveobstacles = [197]

nrows = 7
ncols = 7
nagents = 1
initial = [40]
targets = [[ncols+1]]
obstacles = [24,31,32]
moveobstacles = [33]

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.render()

gwg.draw_state_labels()
beliefparts = 6
beliefcons = 4
# gwg.save('gridworld')
print ('Writing slugs input file...')
# Salty_input.write_to_slugs(gwg,moveobstacles[0],1)
Salty_input.write_to_slugs_belief(gwg,moveobstacles[0],2, beliefparts,beliefcons)
print ('Converting input file...')
os.system('python compiler.py slugs_input_1agents_belief.structuredslugs > slugs_input_1agent_belief.slugsin')
print('Computing controller...')
result = subprocess.Popen('/home/sudab/Applications/slugs/src/slugs --explicitStrategy --jsonOutput slugs_input_1agent_belief.slugsin > slugs_output_1agent_belief.json',shell=True, stdout=subprocess.PIPE)
# result = subprocess.Popen('/home/sudab/Applications/slugs/src/slugs --counterStrategy slugs_input_1agent_belief.slugsin > counterexample.txt',shell=True, stdout=subprocess.PIPE)
# #
# time.sleep(5)

filename = 'slugs_output_1agent_belief.json'
# #
simulateController.userControlled_belief(filename,gwg,beliefparts)


# simulateController.userControlled_belief('slugsoutput_1steplookahead_4.json',gwg)
# simulateController.simulate_path(gwg,filename,counterexample)