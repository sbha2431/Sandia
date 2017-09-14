__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import cegar
import simulateController
import time
import grid_partition
import Salty_input
import subprocess

import time


slugs = '/home/sudab/Applications/slugs/src/slugs'

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
gwg.render()
outfile = 'slugs_output_1agent15x20_8.json'
gwg.draw_state_labels()

infile = 'slugs_output_1agent15x20_8'
print 'output file: ', outfile
print 'input file name:', infile
beliefparts = 6
belief_safety = 30
belief_liveness = 0
target_reachability = True
velocity = 2
# partition = grid_partition.partitionGrid(gwg,beliefparts)
# print partition
partition = dict()
partition[(0,0,0)] = {21,21,22,23,24,25,26,27,41,42,43,44,45,46,47,61,62,63,64,65,66,67,
                      81,82,83,84,85,86,87,101,102,103,104,105,106,107,121,122,123,124,125,126,127,
                      141,142,143,144,145,146,147,161,162,163,164,165,166,167}
partition[(1,0,0)] = {181,182,201,202,221,222,241,242,261,262,243,244,245,246,247,263,264,265,266,267}
partition[(0,1,0)] = {28,29,30,31,32,33,48,49,50,51,52,53,
                      70,71,72,73,90,91,92,93,
                      110,111,112,113,130,131,132,133}
partition[(0,2,0)] = {34,35,36,37,38,54,55,56,57,58,74,75,76,77,78,94,95,96,97,98,114,115,116,117,118,
                      134,135,136,137,138}
partition[(1,2,0)] = {156,157,158,176,177,178,196,197,198,216,217,218,236,237,238,253,254,255,256,257,258,273,274,275,276,277,278}
# partition[(2,2,0)] = {253,254,255,256,257,258,273,274,275,276,277,278}
partition[(2,1,0)] = {148,149,150,151,152,168,169,170,171,172,188,189,190,191,192,
                      208,209,210,211,212,228,229,230,231,232,248,249,250,251,252,268,269,270,271,272}
# partition[(1,1,0)] = {243,244,245,246,247,263,264,265,266,267}

cexfile = 'Examples/slugs_output_1agent15x20_8.txt'
gwfile = 'Examples/slugs_output_1agent15x20_8.png'
print ('Writing slugs input file...')
Salty_input.write_to_slugs_part(infile,gwg,moveobstacles[0],velocity, partition,belief_safety,belief_liveness,target_reachability)
print ('Converting input file...')
os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
print('Checking realizability of full spec...')
sp = subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
sp.wait()
simulateController.userControlled_partition(outfile,gwg,partition,moveobstacles)

