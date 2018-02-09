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
nrows = 8
ncols = 6
nagents = 2
initial = [14,44]
targets = [[1],[40]]
obstacles = []
moveobstacles = [9]

allowed_states = [[None]]*nagents
allowed_states[0] = range((nrows-3)*ncols)
allowed_states[1] = range((nrows-4)*ncols,(nrows)*ncols)
fullvis_states = [[],[],
                  [],[],[]]

partialvis_states = [{0:{24,25,26,27,28,29}},{0:{24,25,26,27,28,29}}]

regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()

gwg.draw_state_labels()

partitionGrid0 = dict()
partitionGrid1 = dict()
partitionGrid2 = dict()
partitionGrid3 = dict()
partitionGrid4 = dict()
partitionGrid0[(0,0)] = range((nrows-3)*ncols)
partitionGrid1[(0,0)] = range((nrows-4)*ncols,(nrows)*ncols)

pg = [partitionGrid0,partitionGrid1]

# gwg.save('gridworldfig.png')
visdist = [3,3]
vel = [2,2]
print 'Writing input file...'
invisibilityset = []
filename = []
for n in range(gwg.nagents):

    # iset = dict.fromkeys(set(gwg.states),frozenset({gwg.nrows*gwg.ncols+1}))
    # for s in set(gwg.states):
    #     iset[s] = visibility.invis(gwg,s,visdist[n]).intersection(set(allowed_states[n]))
    #     iset[s] = iset[s] - set(fullvis_states[n])
    #     if s in gwg.obstacles:
    #         iset[s] = {-1}

    outfile = 'impinfotest{}.json'.format(n)
    infile = 'impinfotest{}'.format(n)
    filename.append(outfile)
    print 'output file: ', outfile
    print 'input file name:', infile
    iset = Salty_input.write_to_slugs_part_dist_impsensors(infile,gwg,initial[n],moveobstacles[0],targets[n],vel[n],visdist[n],allowed_states[n],fullvis_states[n],partialvis_states[n],
                                                pg[n], belief_safety = 0, belief_liveness = 7, target_reachability = True)
    invisibilityset.append(iset)
    print ('Converting input file...')
    os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
    print('Computing controller...')
    sp = subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
    sp.wait()


simulateController.userControlled_partition_dist_imp_sensor(filename,gwg,pg,moveobstacles,allowed_states,invisibilityset,partialvis_states)

