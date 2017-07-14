__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import belief_refinement
import grid_partition
import Slugs_input
import Salty_input
import subprocess
import time
import simulateController

slugs = '/home/rayna/work/tools/slugs/src/slugs'

def cegar_loop(gwg,moveobstacles,beliefcons,beliefparts,infile,outfile,cexfile):

    partition = grid_partition.partitionGrid(gwg,beliefparts);

    done= False
    realizable = False
    iteration = 1

    while (not done):

        print 'ITERATION ',iteration
        print 'PARTITION', partition
    
        # check realizability
    
        print ('Writing slugs input file...')
        Salty_input.write_to_slugs_part(infile,gwg,moveobstacles[0],1, partition,beliefcons)
        print ('Converting input file...')
        os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
        print('Checking realizability...')
        subprocess.Popen(slugs + ' --counterStrategy ' + infile+'.slugsin > ' + cexfile,shell=True, stdout=subprocess.PIPE)

        time.sleep(10)

        done = (os.stat(cexfile).st_size == 0)

        if (done):
            realizable=True
            break;
    
        # check if counterexample is spurious
        
        (res,refineLeaf,leafBelief) = belief_refinement.analyse_counterexample(cexfile,gwg,partition,beliefcons)

        if(not res):
            break

        # refine belief abstraction
    
        for k in refineLeaf:
            partition = grid_partition.partitionState_manual(partition,k,leafBelief)

        iteration = iteration+1

    if(not realizable):
        print('Specification is not realizable')
    else:
        # compute controller for realizable abstraction

        Salty_input.write_to_slugs_part(infile,gwg,moveobstacles[0],1, partition,beliefcons)
        print ('Converting input file...')
        os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
        print('Computing controller...')
        subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
        time.sleep(10)
        print('Simulating controller ...')
        simulateController.userControlled_partition(outfile,gwg,partition)
        


