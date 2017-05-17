__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import counterexample_parser
import grid_partition
import Slugs_input
import Salty_input
import subprocess
import time


nrows = 6
ncols = 6
nagents = 1
initial = [28]
targets = [[ncols+1]]
obstacles = [14,15,20,21]
moveobstacles = [10]


regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()

gwg.draw_state_labels()
gwg.save('gridworldfig_6x6.png')

outfile = 'output_6x6.json'
infile = 'input_6x6'
cexfile = 'counterexample_6x6.txt'
slugs = '/home/rayna/work/tools/slugs/src/slugs'

beliefparts = 2
beliefcons = 2
partition = grid_partition.partitionGrid(gwg,beliefparts);
print (partition)

done= False

while (not done):

	initial = [28]
	moveobstacles = [10]
	gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
	gwg.colorstates = [set(),set()]

	print ('Writing slugs input file...')
	Salty_input.write_to_slugs_part(infile,gwg,moveobstacles[0],1, partition,beliefcons)
	print ('Converting input file...')
	os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
	print('Checking realizability...')
	subprocess.Popen(slugs + ' --counterStrategy ' + infile+'.slugsin > ' + cexfile,shell=True, stdout=subprocess.PIPE)

	time.sleep(10)

	done = (os.stat(cexfile).st_size == 0)
	
	if (done):
		break;
	
	(refineLeaf,leafBelief) = counterexample_parser.analyse_counterexample(cexfile,gwg,partition,beliefcons)
	print (refineLeaf)
	print (leafBelief)

	for k in refineLeaf:
		partition = grid_partition.partitionState_manual(partition,k,leafBelief)

	print (partition)

initial = [28]
moveobstacles = [10]
gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]

Salty_input.write_to_slugs_part(infile,gwg,moveobstacles[0],1, partition,beliefcons)
print ('Converting input file...')
os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
print('Computing controller...')
subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)

