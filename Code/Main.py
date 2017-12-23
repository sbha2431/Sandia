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
slugs = '/home/sudab/Applications/slugs/src/slugs'
# Define gridworld parameters
nrows = 7
ncols = 10
nagents = 1
initial = [0]
targets = [[ncols+1]]
obstacles = [4,14,24,44,54,64]
moveobstacles = [1]

# nrows = 15
# ncols = 20
# nagents = 1
# initial = [237]
# targets = [[ncols+1]]
# obstacles = [153,154,155,173,174,175,193,194,195,213,214,215,233,234,235,68,69,88,89,108,109,128,129,183,184,185,186,187,203,204,205,206,207,223,224,225,226,227]
# moveobstacles = [197]



regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()

gwg.draw_state_labels()

outfile = 'test.json'
infile = 'test'
print 'output file: ', outfile
print 'input file name:', infile
partitionGrid = dict()
# partitionGrid[(0,0)] = [0,1,2,3,4,5,6,7,8,9,20,21,22,23,24,25,26,27,28,29,40,41,42,43,44,45,46,47,48,49,60,61,62,63,64,65,66,67,
#                         80,81,82,83,84,85,86,87,100,101,102,103,104,105,106,107,120,121,122,123,124,125,126,127,
#                         140,141,142,143,144,145,146,147,148,149,160,161,162,163,164,165,166,167,168,169,
#                         180,181,182,188,189,200,201,202,208,209,220,221,222,228,229,240,241,242,243,244,245,246,247,248,249,
#                         260,261,262,263,264,265,266,267,268,269,280,281,282,283,284,285,286,287,288,289]
#
# partitionGrid[(1,0)] = [10,11,12,13,14,15,16,17,18,19,30,31,32,33,34,35,36,37,38,39,50,51,52,53,54,55,56,57,58,59,70,71,72,73,74,75,76,77,78,79,
#                         90,91,92,93,94,95,96,97,98,99,110,111,112,113,114,115,116,117,118,119,130,131,132,133,134,135,136,137,138,139,
#                         150,151,152,156,157,158,159,170,171,172,176,177,178,179,190,191,192,196,197,198,199,210,211,212,216,217,218,219,
#                         230,231,232,236,237,238,239,250,251,252,253,254,255,256,257,258,259,270,271,272,273,274,275,276,277,278,279,
#                         290,291,292,293,294,295,296,296,297,298,299]

partitionGrid[(0,0)] = [0,1,2,3,10,11,12,13,20,21,22,23,30,31,32,33,34,40,41,42,43,50,51,52,53,60,61,62,63]
partitionGrid[(0,1)] = [5,6,7,8,9,15,16,17,18,19,25,26,27,28,29,35,36,37,38,39,45,46,47,48,49,55,56,57,58,59,65,66,67,68,69]

# gwg.save('gridworldfig.png')
visdist = 2
gs = [12,25]
print 'Writing input file...'
invisibilityset = Salty_input.write_to_slugs_part(infile,gwg,initial[0],moveobstacles[0],targets[0],2,visdist,gs, partitionGrid, belief_safety = 0, belief_liveness = 10, target_reachability = True)

print ('Converting input file...')
os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
print('Computing controller...')
sp = subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
sp.wait()
simulateController.userControlled_partition(outfile,gwg,partitionGrid,moveobstacles,invisibilityset)