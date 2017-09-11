__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
# nrows = 10
# ncols = 15
# nagents = 1
# initial = [130]
# targets = [[ncols+1]]
# obstacles = [18,33,66,67,97,112,127,96,95,94,98,99,69,70,71,72,102,103,25,40,55,68]
# moveobstacles = [101]


nrows = 15
ncols = 20
nagents = 1
initial = [237,257]
targets = [[ncols+1]]
obstacles = [153,154,155,173,174,175,193,194,195,213,214,215,233,234,235,68,69,88,89,108,109,128,129,183,184,185,186,187,203,204,205,206,207,223,224,225,226,227]
moveobstacles = [197]


regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()
#
gwg.draw_state_labels()

outfile = '15x20reachabilityliveness.json'
infile = '15x20reachabilityliveness'
print 'output file: ', outfile
print 'input file name:', infile
beliefparts = 7
beliefsafety = 0
beliefliveness = 60
targetreachability = True
partition = grid_partition.partitionGrid(gwg,beliefparts)
# partition = dict()
# partition[(0,0,0)] = {16,17,31,32,46,47,61,62,76,77,91,92,106,107,121,122,78,79,80,81,82,83}
# partition[(0,1,0)] = {19,20,21,34,35,36,48,49,50,51,66,22,37,52,63,64,65,23,24,38,39,53,54,93,108,109,110,111,123,124,125,126}
# partition[(1,0,0)] = {93,108,109,110,111,123,124,125,126}
# partition[(0,2,0)] = {26,27,28,41,42,43,56,57,58,68,73}
# partition[(1,1,0)] = {100,101,113,114,115,116,117,118,128,129,130,131,132,133}
# partition[(1,2,0)] = {78,79,80,81,82,83}
# partition[(1,3,0)] = {84,85,86,87,88}
# gwg.save('gridworldfig.png'),77,78
print ('Writing slugs input file...')
Salty_input.write_to_slugs_part(infile,gwg,moveobstacles,2,partition, beliefsafety,beliefliveness,targetreachability)
print ('Converting input file...')
os.system('python /home/sudab/Documents/Research/DARPA/Code/compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
print('Computing controller...')
result = subprocess.Popen('/home/sudab/Applications/slugs/src/slugs --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
result.wait()

simulateController.userControlled_partition(outfile,gwg,partition,moveobstacles)