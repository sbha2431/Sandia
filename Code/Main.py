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
# Define gridworld parameters
nrows = 15
ncols = 20
nagents = 1
initial = [237]
targets = [[ncols+1]]
obstacles = [153,154,155,173,174,175,193,194,195,213,214,215,233,234,235,68,69,88,89,108,109,128,129,183,184,185,186,187,203,204,205,206,207,223,224,225,226,227]
moveobstacles = [197,177]
#
# nrows = 10
# ncols = 10
# nagents = 1
# initial = [56]
# targets = [[ncols+1]]
# obstacles = [34,44,45,54,55,64,57]
# moveobstacles = [46,37]


regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
# gwg.render()
#
# gwg.draw_state_labels()

outfile = '15x20_multitarget_4_8belief.json'
infile = '15x20_multitarget_4_8belief'
print 'output file: ', outfile
print 'input file name:', infile
beliefparts = 10
beliefcons = 120
# gwg.save('gridworldfig.png')
# print ('Writing slugs input file...')

# Salty_input.write_to_slugs_belief(infile,gwg,2, beliefparts,beliefcons)
# Salty_input.write_to_slugs_belief_multipletargets(infile,gwg,4, beliefparts,beliefcons)
# print ('Converting input file...')
# os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
# print('Computing controller...')
# result = subprocess.Popen('/home/sudab/Applications/slugs/src/slugs --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
# result = subprocess.Popen('/home/sudab/Applications/slugs/src/slugs --counterStrategy ' + infile+'.slugsin > counterexample_10x10_4.txt',shell=True, stdout=subprocess.PIPE)
# # # # #
# time.sleep(10)
#
# # #
# simulateController.userControlled_belief(outfile,gwg,beliefparts)
#
# counterexample_parser.run_counterexample('counterexample.txt',gwg,beliefparts)

# simulateController.userControlled('slugs_output_2agents.json',gwg)
# simulateController.simulate_path(gwg,filename,counterexample)
# simulateController.userControlled_belief_multitarget(outfile,gwg,beliefparts)