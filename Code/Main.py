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
#
nrows = 10
ncols = 10
nagents = 1
initial = [88]
targets = [[ncols+1]]
obstacles = [34,44,45,54,55,64,47]
moveobstacles = [68]

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.render()
outfile = 'slugs_output_1agent15x20_belief.json'
infile = 'slugs_input_15x20_1agent_belief'
gwg.draw_state_labels()
beliefparts = 6
beliefcons = 10
# gwg.save('gridworld')
print ('Writing slugs input file...')
# Salty_input.write_to_slugs(gwg,moveobstacles[0],1)
Salty_input.write_to_slugs_belief(infile,gwg,moveobstacles[0],2, beliefparts,beliefcons)
print ('Converting input file...')
os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
print('Computing controller...')
result = subprocess.Popen('/home/sudab/Applications/slugs/src/slugs --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
# result = subprocess.Popen('/home/sudab/Applications/slugs/src/slugs --counterStrategy ' + infile+'.slugsin > counterexample.txt',shell=True, stdout=subprocess.PIPE)
# # # #
time.sleep(15)
#
# # #
# simulateController.userControlled_belief(outfile,gwg,beliefparts)


# simulateController.userControlled_belief('slugsoutput_1steplookahead_4.json',gwg)
# simulateController.simulate_path(gwg,filename,counterexample)